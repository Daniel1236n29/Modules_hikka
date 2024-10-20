# meta developer: @stupid_alien_mods
from .. import loader, utils
from telethon import events
from skimage import transform
from skimage.io import imread, imsave
import io
import numpy as np

@loader.tds
class resizeimageMod(loader.Module):
    """Изменяет размер изображения"""
    strings = {"name": "resizeimage"}

    async def ricmd(self, message):
        """Меняет размер изображения. Использование: .ri <ширина> <высота>"""
        reply = await message.get_reply_message()
        if not reply or not reply.photo:
            await message.edit("Ответьте на сообщение с фото!")
            return

        args = utils.get_args(message)
        if len(args) != 2:
            await message.edit("Укажите новую ширину и высоту!")
            return

        try:
            new_width, new_height = map(int, args)
        except ValueError:
            await message.edit("Ширина и высота должны быть целыми числами!")
            return

        photo = await reply.download_media(bytes)
        img = imread(io.BytesIO(photo))

        try:
            resized = transform.resize(img, (new_height, new_width), mode='constant')
        except Exception as e:
            await message.edit(f"Ошибка при изменении размера: {str(e)}")
            return

        output = io.BytesIO()
        imsave(output, (resized * 255).astype(np.uint8), format='PNG')
        output.seek(0)

        await message.client.send_file(message.to_id, output, reply_to=reply)
        await message.delete()

    async def watcher(self, message):
        pass