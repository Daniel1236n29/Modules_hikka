# ———————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————                                                
#          _____                    _____                    _____                    _____                    _____                    _____  
#         /\    \                  /\    \                  /\    \                  /\    \                  /\    \                  /\    \ 
#        /::\    \                /::\    \                /::\____\                /::\    \                /::\    \                /::\____\
#       /::::\    \              /::::\    \              /::::|   |                \:::\    \               \:::\    \              /:::/    /
#      /::::::\    \            /::::::\    \            /:::::|   |                 \:::\    \               \:::\    \            /:::/    / 
#     /:::/\:::\    \          /:::/\:::\    \          /::::::|   |                  \:::\    \               \:::\    \          /:::/    /  
#    /:::/  \:::\    \        /:::/__\:::\    \        /:::/|::|   |                   \:::\    \               \:::\    \        /:::/    /   
#   /:::/    \:::\    \      /::::\   \:::\    \      /:::/ |::|   |                   /::::\    \              /::::\    \      /:::/    /    
#  /:::/    / \:::\    \    /::::::\   \:::\    \    /:::/  |::|   | _____    ____    /::::::\    \    ____    /::::::\    \    /:::/    /     
# /:::/    /   \:::\ ___\  /:::/\:::\   \:::\    \  /:::/   |::|   |/\    \  /\   \  /:::/\:::\    \  /\   \  /:::/\:::\    \  /:::/    /      
#/:::/____/     \:::|    |/:::/  \:::\   \:::\____\/:: /    |::|   /::\____\/::\   \/:::/  \:::\____\/::\   \/:::/  \:::\____\/:::/____/       
#\:::\    \     /:::|____|\::/    \:::\  /:::/    /\::/    /|::|  /:::/    /\:::\  /:::/    \::/    /\:::\  /:::/    \::/    /\:::\    \       
# \:::\    \   /:::/    /  \/____/ \:::\/:::/    /  \/____/ |::| /:::/    /  \:::\/:::/    / \/____/  \:::\/:::/    / \/____/  \:::\    \      
#  \:::\    \ /:::/    /            \::::::/    /           |::|/:::/    /    \::::::/    /            \::::::/    /            \:::\    \     
#   \:::\    /:::/    /              \::::/    /            |::::::/    /      \::::/____/              \::::/____/              \:::\    \    
#    \:::\  /:::/    /               /:::/    /             |:::::/    /        \:::\    \               \:::\    \               \:::\    \   
#     \:::\/:::/    /               /:::/    /              |::::/    /          \:::\    \               \:::\    \               \:::\    \  
#      \::::::/    /               /:::/    /               /:::/    /            \:::\    \               \:::\    \               \:::\    \ 
#       \::::/    /               /:::/    /               /:::/    /              \:::\____\               \:::\____\               \:::\____\
#        \::/____/                \::/    /                \::/    /                \::/    /                \::/    /                \::/    /
#         ~~                       \/____/                  \/____/                  \/____/                  \/____/                  \/____/ 
#————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# meta developer: @stupid_alien_mods
                                                                     
                                                     


from .. import loader, utils
from telethon.tl.types import Message
from telethon import events
import os
import mimetypes
from PIL import Image
import moviepy.editor as mp

@loader.tds
class FileConverterMod(loader.Module):
    """Конвертер файлов"""
    strings = {"name": "FileConverter"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.command(
        ru_doc="Конвертировать файл"
    )
    async def convertcmd(self, message: Message):
        """Конвертировать файл"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await utils.answer(message, "Ответьте на сообщение с файлом.")
            return

        file = await reply.download_media()
        mime_type, _ = mimetypes.guess_type(file)

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
                [{'text': fmt, 'callback': self.convert_file, 'args': (file, fmt.lower(), type_category)}]
                for fmt in formats[type_category]
            ]
            await self.inline.form(
                message=message,
                text="Выберите формат для конвертации:",
                reply_markup=buttons,
            )
        else:
            await utils.answer(message, "❌Неподдерживаемый тип файла.")
            os.remove(file)

    async def convert_file(self, call, file, new_format, type_category):
        output_file = os.path.splitext(file)[0] + "." + new_format
        
        if type_category == "image":
            img = Image.open(file)
            img.save(output_file, format=new_format.upper())
        elif type_category == "video":
            video = mp.VideoFileClip(file)
            if new_format == "gif":
                video.write_gif(output_file)
            else:
                video.write_videofile(output_file)
        elif type_category == "audio":
            audio = mp.AudioFileClip(file)
            audio.write_audiofile(output_file)

        await call.edit("✅Файл успешно конвертирован!")
        await self.client.send_file(call.form["chat"], output_file)
        
        os.remove(file)
        os.remove(output_file)
