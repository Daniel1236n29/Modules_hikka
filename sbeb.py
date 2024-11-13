# meta developer: @shrimp_mod

from telethon import events
import datetime
from .. import loader, utils

@loader.tds
class SbebMod(loader.Module):
    """Перевод на ваш sbebbank"""
    strings = {"name": "Sbeb"}

    
    async def client_ready(self, client, db):
        self.client = client
        
    @loader.command()
    async def sbebcmd(self, message):
        """Переводит деньги на ваш sbebbank"""
        args = message.raw_text.split()
        if len(args) < 2 or not args[1].isdigit():
            await utils.answer(message, "Пожалуйста, укажите корректную сумму!")
            return
        await utils.answer(message, "Выполняется перевод")

        amount = args[1]
        

        now = datetime.datetime.now().strftime("%H:%M")

        transfer_message = f"{message.sender.username}\n{amount}\n0\n{now}"

        async with self.client.conversation('@Sber_t_bot') as conv:
            await conv.send_message('✅ Сбербанк')
            await conv.get_response()

            await conv.send_message('💸 Скриншот перевода')
            await conv.get_response()

            await conv.send_message('🆕🎉 Перевод Айфон 10-15')
            await conv.get_response()

            await conv.send_message(transfer_message)
            await conv.get_response()

            response = await conv.get_response()

            if response.media:

                await self.client.send_file(message.chat_id, response.media, caption= f"Перевод выполнен на сумму: {amount} ₽")
            else:
                await utils.answer(message, "Не удалось получить изображение. Попробуйте еще раз.")
