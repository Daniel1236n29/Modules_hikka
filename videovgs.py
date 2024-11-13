
# meta developer: @shrimp_mod

import os
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from .. import loader, utils

@loader.tds
class VideoToVoiceMod(loader.Module):
    """Модуль для конвертации видео в голосовое сообщение"""
    strings = {"name": "VideoToVoice"}

    async def vtvcmd(self, message):
        """Конвертация видео в голосовое сообщение"""
        reply = await message.get_reply_message()

        if not reply or not reply.media:
            await message.edit("❌ Пожалуйста, ответь на видео.")
            return


        video = await message.client.download_media(reply, "input_video.mp4")
        if not video:
            await message.edit("❌ Не удалось загрузить видео.")
            return

        try:

            await message.edit("🔄 Извлечение аудио из видео...")
            video_clip = VideoFileClip(video)
            video_clip.audio.write_audiofile("output_audio.mp3")


            await message.edit("🔄 Конвертация в голосовое сообщение...")
            audio = AudioSegment.from_file("output_audio.mp3", format="mp3")
            audio.export("voice_message.ogg", format="ogg", codec="libopus")

            await message.client.send_file(message.chat_id, "voice_message.ogg", voice_note=True)

            await message.edit("✅ Видео успешно преобразовано в голосовое сообщение!")
        finally:
            os.remove("input_video.mp4")
            os.remove("output_audio.mp3")
            os.remove("voice_message.ogg")
