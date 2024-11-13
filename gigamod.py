
# meta developer: @shrimp_mod

from .. import loader, utils
from telethon import events
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

class GigaChatMod(loader.Module):
    """Модуль для использования GigaChat. чтобы получить api перейдите сюда: https://developers.sber.ru/studio/workspaces """

    strings = {"name": "GigaChat"}
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            "GIGACHAT_API_KEY", None, "Введите ваш API ключ для GigaChat"
        )
    
    async def client_ready(self, client, db):
        self.client = client
    
    @loader.command()
    async def gigacmd(self, message):
        """Получить gigaОтвет на ваш вопрос"""
        if not self.config["GIGACHAT_API_KEY"]:
            await utils.answer(message, "Пожалуйста, установите API ключ в конфигурации модуля.")
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "Пожалуйста, введите запрос после команды.")
            return

        async with GigaChat(credentials=self.config["GIGACHAT_API_KEY"], scope="GIGACHAT_API_PERS", verify_ssl_certs=False) as giga:
            response = giga.chat(args)

        result = response.choices[0].message.content
        
        await utils.answer(
            message,
            f"❔ Запрос: {args}\n🥸 GigaОтвет: {result}"
        )
   
