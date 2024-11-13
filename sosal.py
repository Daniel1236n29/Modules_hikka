# meta developer: @shrimp_mod


from .. import loader, utils
from telethon import events

@loader.tds
class SosalMod(loader.Module):
    strings = {"name": "Sosal"}

    def __init__(self):
        self.config = loader.ModuleConfig("active", False, "Активировать модуль")
        self.triggers = ["да", "конечно", "естественно", "каждый день", "ага", "Да", "Конечно", "Естественно", "Каждый день", "Ага", "До", "до"
        ]

    async def client_ready(self, client, db):
        self.db = db

    async def watcher(self, message):
        if not self.db.get(self.strings["name"], "active", False):
            return

        if message.sender_id == (await message.client.get_me()).id:
            return

        if message.is_reply:

            replied_msg = await message.get_reply_message()
            

            if any(trigger in message.raw_text.lower() for trigger in self.triggers):

                if replied_msg.sender_id == (await message.client.get_me()).id:
                    await replied_msg.edit("Сосал?")

    async def sosalcmd(self, message):
        """Активация/деактивация модуля"""
        current_state = self.db.get(self.strings["name"], "active", False)
        new_state = not current_state
        self.db.set(self.strings["name"], "active", new_state)
        await utils.answer(message, f"Модуль {'активирован' if new_state else 'деактивирован'}")
