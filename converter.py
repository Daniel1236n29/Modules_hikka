
# meta developer: @shrimp_mod

from .. import loader, utils
from telethon.tl.types import Message, DocumentAttributeFilename
from telethon import events
import mimetypes
from PIL import Image
import moviepy.editor as mp
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import asyncio
import tempfile
import os

@loader.tds
class FileConverterMod(loader.Module):
    """Конвертер файлов"""
    strings = {"name": "FileConverter"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "thread_pool_size", 3, "Размер пула потоков для конвертации"
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=self.config["thread_pool_size"])

    @loader.command(
        ru_doc="Конвертировать файл"
    )
    async def convertcmd(self, message: Message):
        """Конвертировать файл"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await utils.answer(message, "Ответьте на сообщение с файлом.")
            return

        try:
            file_data = await reply.download_media(file=bytes)
            mime_type = reply.file.mime_type
            original_filename = reply.file.name or "file"

            if mime_type:
                type_category = mime_type.split('/')[0]
            else:
                type_category = "unknown"

            formats = {
                "image": ["PNG", "JPEG", "WebP"],
                "video": ["MP4", "AVI", "GIF"],
                "audio": ["MP3", "WAV", "OGG"],
            }

            if type_category in formats:
                buttons = [
                    [{'text': fmt, 'callback': self.convert_file, 'args': (file_data, fmt.lower(), type_category, original_filename)}]
                    for fmt in formats[type_category]
                ]
                await self.inline.form(
                    message=message,
                    text="Выберите формат для конвертации:",
                    reply_markup=buttons,
                )
            else:
                await utils.answer(message, "❌Неподдерживаемый тип файла.")
        except Exception as e:
            await utils.answer(message, f"❌Произошла ошибка при обработке файла: {str(e)}")

    async def convert_file(self, call, file_data, new_format, type_category, original_filename):
        try:
            await call.edit("⏳Конвертация файла...")
            
            input_buffer = BytesIO(file_data)
            output_buffer = BytesIO()
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._convert, input_buffer, output_buffer, new_format, type_category)
            
            output_buffer.seek(0)
            new_filename = f"{original_filename.rsplit('.', 1)[0]}.{new_format}"
            
            mime_type, _ = mimetypes.guess_type(new_filename)
            if not mime_type:
                mime_type = f"{type_category}/{new_format}"

            await call.edit("✅Файл успешно конвертирован!")
            await self.client.send_file(
                call.form["chat"],
                file=output_buffer,
                filename=new_filename,
                mime_type=mime_type,
                force_document=True,
                attributes=[DocumentAttributeFilename(file_name=new_filename)]
            )
        except Exception as e:
            await call.edit(f"❌Произошла ошибка при конвертации: {str(e)}")

    def _convert(self, input_buffer, output_buffer, new_format, type_category):
        if type_category == "image":
            img = Image.open(input_buffer)
            img.save(output_buffer, format=new_format.upper())
        elif type_category in ["video", "audio"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{new_format}") as temp_file:
                temp_file.write(input_buffer.getvalue())
                temp_file_name = temp_file.name

            try:
                if type_category == "video":
                    with mp.VideoFileClip(temp_file_name) as video:
                        if new_format == "gif":
                            video.write_gif(temp_file_name)
                        else:
                            video.write_videofile(temp_file_name, codec='libx264')
                elif type_category == "audio":
                    with mp.AudioFileClip(temp_file_name) as audio:
                        audio.write_audiofile(temp_file_name)

                with open(temp_file_name, "rb") as f:
                    output_buffer.write(f.read())
            finally:
                os.unlink(temp_file_name)
