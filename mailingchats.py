__version__ = (1, 2, 1)

# meta developer: @shrimp_mod

from .. import loader, utils
import logging
import asyncio

@loader.tds
class MailingChatsMod(loader.Module):
    """Модуль для управления списком чатов для рассылки"""
    strings = {
        "name": "Mailing Chats",
        "chat_added": "✅ Чат {} ({}) добавлен в список рассылки",
        "chat_removed": "❌ Чат {} ({}) удален из списка рассылки",
        "no_chats": "📋 Список чатов для рассылки пуст",
        "chats_list": "📝 Текущие чаты для рассылки:\n{}",
        "chat_already_exists": "⚠️ Чат {} ({}) уже есть в списке рассылки",
        "chat_not_found": "❌ Чат {} ({}) не найден в списке рассылки",
        "delay_updated": "⚙️ Задержка между отправкой сообщений установлена на {} секунд"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "mailing_chats",
                [],
                doc=lambda: "Список чатов для рассылки",
                validator=loader.validators.Series(loader.validators.Integer())
            ),
            loader.ConfigValue(
                "delay_between_sends",
                2,
                doc=lambda: "Задержка между отправкой сообщений в секундах"
            )
        )

    async def get_chat_name(self, message):
        """Получить название чата или имя пользователя"""
        try:
            chat = await message.get_chat()
            if hasattr(chat, 'title'):
                return chat.title
            elif hasattr(chat, 'first_name'):
                return f"{chat.first_name} {chat.last_name or ''}".strip()
            else:
                return "Неизвестный чат"
        except Exception:
            return "Неизвестный чат"

    @loader.command()
    async def addchatr(self, message):
        """Добавить чат в список рассылки"""
        chat_id = utils.get_chat_id(message)
        chat_name = await self.get_chat_name(message)
        
        if chat_id in self.config['mailing_chats']:
            status_message = await message.edit(self.strings["chat_already_exists"].format(chat_id, chat_name))
            await asyncio.sleep(3)
            await status_message.delete()
            return

        chats_list = list(self.config['mailing_chats'])
        chats_list.append(chat_id)
        self.config['mailing_chats'] = chats_list

        status_message = await message.edit(self.strings["chat_added"].format(chat_id, chat_name))
        await asyncio.sleep(3)
        await status_message.delete()

    @loader.command()
    async def delchatr(self, message):
        """Удалить чат из списка рассылки"""
        chat_id = utils.get_chat_id(message)
        chat_name = await self.get_chat_name(message)
        
        if chat_id not in self.config['mailing_chats']:
            status_message = await message.edit(self.strings["chat_not_found"].format(chat_id, chat_name))
            await asyncio.sleep(3)
            await status_message.delete()
            return

        chats_list = list(self.config['mailing_chats'])
        chats_list.remove(chat_id)
        self.config['mailing_chats'] = chats_list

        status_message = await message.edit(self.strings["chat_removed"].format(chat_id, chat_name))
        await asyncio.sleep(3)
        await status_message.delete()

    @loader.command()
    async def setdelay(self, message):
        """Установить задержку между отправкой сообщений (в секундах)"""
        args = utils.get_args_raw(message)
        try:
            delay = float(args)
            if delay < 0:
                raise ValueError
            self.config['delay_between_sends'] = delay
            status_message = await message.edit(self.strings["delay_updated"].format(delay))
            await asyncio.sleep(3)
            await status_message.delete()
        except (ValueError, TypeError):
            status_message = await message.edit("❌ Пожалуйста, введите положительное число")
            await asyncio.sleep(3)
            await status_message.delete()

    @loader.command()
    async def listchatr(self, message):
        """Показать список чатов для рассылки"""
        chats = self.config['mailing_chats']
        
        if not chats:
            status_message = await message.edit(self.strings["no_chats"])
            await asyncio.sleep(3)
            await status_message.delete()
            return

        chat_names = []
        for chat_id in chats:
            try:
                chat = await message.client.get_entity(chat_id)
                if hasattr(chat, 'title'):
                    chat_names.append(f"{chat_id}: {chat.title}")
                elif hasattr(chat, 'first_name'):
                    name = f"{chat.first_name} {chat.last_name or ''}".strip()
                    chat_names.append(f"{chat_id}: {name}")
                else:
                    chat_names.append(str(chat_id))
            except Exception:
                chat_names.append(str(chat_id))

        chat_list = "\n".join(chat_names)
        status_message = await message.edit(self.strings["chats_list"].format(chat_list))
        await asyncio.sleep(10)
        await status_message.delete()

    @loader.command()
    async def mailall(self, message):
        """Отправить сообщение во все чаты из списка"""
        text = utils.get_args_raw(message)
        if not text:
            status_message = await message.edit("❌ Введите текст для рассылки")
            await asyncio.sleep(3)
            await status_message.delete()
            return

        chats = self.config['mailing_chats']
        if not chats:
            status_message = await message.edit(self.strings["no_chats"])
            await asyncio.sleep(3)
            await status_message.delete()
            return

        success_count = 0
        for chat in chats:
            try:
                await message.client.send_message(chat, text)
                success_count += 1
                if success_count < len(chats):
                    await asyncio.sleep(self.config['delay_between_sends'])
            except Exception as e:
                logging.error(f"Ошибка при отправке в чат {chat}: {e}")

        status_message = await message.edit(f"✅ Сообщение отправлено в {success_count} чатов")
        await asyncio.sleep(3)
        await status_message.delete()
