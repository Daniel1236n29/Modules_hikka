# meta developer: @stupid_alien_mods

from .. import loader, utils
import asyncio

@loader.tds
class FarmdMod(loader.Module):
    """Модуль для увеличения 🍆 в @themetrbot"""
    strings = {"name": "FarmdMod"}
    
    def __init__(self):
        self.running = False 

    async def farmdoncmd(self, message):
        """Включить автоматическую отправку /dick """
        if self.running:
            await message.edit("<b>❎Процесс уже запущен!</b>")
            return

        self.running = True
        await message.edit("<b>✅Автоматическая отправка /dick запущена!</b>")

        while self.running:
            await message.client.send_message("@themetrbot", "/dick")
            await asyncio.sleep(3600)
    async def farmdoffcmd(self, message):
        """Отключить автоматическую отправку /dick """
        if not self.running:
            await message.edit("<b>❎Процесс не запущен!</b>")
            return

        self.running = False
        await message.edit("<b>❎Автоматическая отправка /dick остановлена!</b>")
