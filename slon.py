__version__ = (0, 0, 1)
# meta developer: @daniilmods
#----------------------------------------------------------------------------
from .. import loader
from hikkatl.types import Message

@loader.tds
class ReplyModule(loader.Module):
    """Модуль, который отвечает на каждое сообщение в чате 'все говорят [текст], а ты купи слона'"""
    strings = {"name": "ReplyModule"}
    
    async def client_ready(self, client, db):
        self.db = db
        self.client = client
    
    @loader.command()
    async def sloncmd(self, message: Message):
        """Включает/выключает автоответчика на 'купи слона' в текущем чате"""
        chat_id = message.chat_id
        current_status = self.db.get("ReplyModule", "chats", {})
        
        if chat_id in current_status:

            del current_status[chat_id]
            self.db.set("ReplyModule", "chats", current_status)
            await message.respond("Автоответчик 'купи слона' отключен в этом чате.")
        else:

            current_status[chat_id] = True
            self.db.set("ReplyModule", "chats", current_status)
            await message.respond("Автоответчик 'купи слона' включен в этом чате.")
        
        await message.delete()

    async def watcher(self, message: Message):
        current_status = self.db.get("ReplyModule", "chats", {})
        chat_id = message.chat_id
        
        if chat_id in current_status and not message.out:
            response_text = f"все говорят '{message.raw_text}', а ты купи слона"
            await message.reply(response_text)