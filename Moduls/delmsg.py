#meta developer: @daniilmods
#----------------------------------------------------------------------------
from hikka import loader, utils

@loader.tds
class DeleteMessagesMod(loader.Module):
    """Модуль для удаления определённого количества сообщений"""
    strings = {
        "name": "DeleteMessagesMod",
        "invalid_number": "❗ Укажите корректное количество сообщений для удаления.",
        "deleted": "✅ Удалено {count} сообщений."
    }

    async def delcmd(self, message):
        """Удалить указанное количество сообщений. Использование: .del <количество>"""
        args = utils.get_args_raw(message)

        if not args.isdigit():
            await utils.answer(message, self.strings["invalid_number"])
            return

        count = int(args)

        messages = []
        async for msg in message.client.iter_messages(message.chat_id, limit=count+1):
            messages.append(msg.id)

        await message.client.delete_messages(message.chat_id, messages)


        await utils.answer(message, self.strings["deleted"].format(count=len(messages)-1))