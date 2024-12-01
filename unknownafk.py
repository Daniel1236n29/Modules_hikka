# meta developer: @shrimp_mod
__version__ = (3, 5, 4)

import asyncio
import datetime
import time
import re
import pytz

from telethon import types
from telethon.tl.functions.account import UpdateProfileRequest, UpdateEmojiStatusRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import EmojiStatus, EmojiStatusEmpty

from .. import loader, utils
from ..inline.types import InlineCall

class UnknownAFKMod(loader.Module):
    """Модуль АФК который меняет эмодзи статус (онли Прем) и всякая другая всячина"""

    PERMANENT_BLACKLIST = [777000]

    strings = {
        "name": "UnknownAFK",
        "bt_off_afk": "<emoji document_id=5872829476143894491>🚫</emoji> <b>АФК</b> режим <b>отключен</b>!",
        "invalid_time_format": "<emoji document_id=5778527486270770928>❌</emoji> <b>Неверный формат времени!</b>\n<emoji document_id=5335054400513649848>📝</emoji> Используйте формат <code>16:30</code>",
        "chat_blacklisted": "<emoji document_id=5309788666984415888>😊</emoji> <b>Текущий чат добавлен в черный список</b>",
        "chat_already_blacklisted": "<emoji document_id=5778527486270770928>❌</emoji> <b>Этот чат уже в черном списке</b>",
        "chat_removed": "<emoji document_id=5309788666984415888>😊</emoji> <b>Текущий чат удален из черного списка</b>",
        "no_chat_in_blacklist": "<emoji document_id=5778527486270770928>❌</emoji> <b>Этот чат не находится в черном списке</b>",
        "blacklist_title": "<emoji document_id=5872829476143894491>🚫</emoji> <b>Черный список чатов:</b>\n",
        "blacklist_empty": "<emoji document_id=5416118154424242282>🐱</emoji> <b>Черный список чатов пуст</b>",
        "contact_feedback": "📞 Связаться с ботом",
        "turn_off_afk": "🚫 Выключить АФК"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "blacklist_chats",
                [],
                doc=lambda: "Список чатов и пользователей, в которых не будут отправляться АФК уведомления (ID чатов и пользователей)",
                validator=loader.validators.Series(loader.validators.Integer())
            ),
            loader.ConfigValue(
                "timezone",
                "Europe/Moscow",
                doc=lambda: "Часовой пояс (например, Europe/Moscow, Europe/London, US/Eastern)"
            ),
            loader.ConfigValue(
                "prefix",
                "",
                doc=lambda: "Префикс для имени во время АФК"
            ),
            loader.ConfigValue(
                "feedback",
                None,
                doc=lambda: "Юзернейм вашего feedback бота. Если нету - не трогайте",
            ),
            loader.ConfigValue(
                "about_text",
                None,
                doc=lambda: "Текст в био при АФК. Используйте {bot} для бота и {reason} для причины."
            ),
            loader.ConfigValue(
                "afk_text",
                "None",
                doc=lambda: "Кастомный текст афк. Используй {time} для времени, {reason} для причины, {return_time} для времени возвращения и {zone} для часового пояса",
            ),
            loader.ConfigValue(
                "use_emoji_status",
                True,
                doc=lambda: "Использовать эмодзи статус (требуется премиум)",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "afk_emoji_status_id",
                5433792778070925926, 
                doc=lambda: "ID эмодзи для статуса АФК (работает только с премиум)",
            ),
            loader.ConfigValue(
                "default_emoji_status_id",
                None,
                doc=lambda: "ID вашего обычного эмодзи статуса (чтобы вернуть после АФК)",
            ),
            loader.ConfigValue(
                "button",
                False,
                doc=lambda: "Добавить кнопку отключения АФК режима?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "original_last_name",
                "",
                doc=lambda: "Оригинальная фамилия пользователя для восстановления"
            )
        )

    async def client_ready(self, client, db):
        user_blacklist = self.config["blacklist_chats"]
        combined_blacklist = list(set(self.PERMANENT_BLACKLIST + user_blacklist))
        self.config["blacklist_chats"] = combined_blacklist
        self._me = await client.get_me()
        self._premium = self._me.premium
        if not self._db.get(__name__, "notified_users"):
            self._db.set(__name__, "notified_users", [])
        self._check_return_time_task = asyncio.create_task(self._check_return_time_loop())
        
        me = await client(GetFullUserRequest(self._me.id))
        self.config["original_last_name"] = me.users[0].last_name or ""

    async def _disable_afk_mode(self):
        """Отключение АФК режима программно"""
        self._db.set(__name__, "afk", False)
        self._db.set(__name__, "gone", None)
        self._db.set(__name__, "notified_users", [])
        self._db.set(__name__, "return_time", None)
        
        original_last_name = self.config["original_last_name"]
        await self._client(UpdateProfileRequest(last_name=original_last_name or " "))
        
        if self._db.get(__name__, "change_bio", False):
            try:
                await self._client(UpdateProfileRequest(about=self._db.get(__name__, "about", "")))
            except Exception:
                pass

        await self._update_emoji_status(False)

    async def _check_return_time_loop(self):
        """Фоновая задача для проверки времени возврата и отключения АФК"""
        while True:
            await asyncio.sleep(60)
            afk_state = self._db.get(__name__, "afk", False)
            return_time = self._db.get(__name__, "return_time")
            
            if afk_state and return_time and return_time != "не указано":
                tz = pytz.timezone(self.config["timezone"])
                current_time = datetime.datetime.now(tz).strftime("%H:%M")
                
                if current_time == return_time:
                    await self._disable_afk_mode()


    @loader.command()
    async def afklist(self, message):
        """Показать черный список чатов"""
        blacklist_chats = self.config["blacklist_chats"]
        
        if not blacklist_chats:
            await utils.answer(message, self.strings["blacklist_empty"])
            return
        
        blacklist_msg = self.strings["blacklist_title"]
        for chat_id in blacklist_chats:
            try:
                is_permanent = chat_id in self.PERMANENT_BLACKLIST
                permanent_mark = " 🔒" if is_permanent else ""
                
                chat = await message.client.get_entity(chat_id)
                chat_name = getattr(chat, 'title', str(chat_id))
                blacklist_msg += f"• <code>{chat_id}</code> - {chat_name}{permanent_mark}\n"
            except Exception:
                blacklist_msg += f"• <code>{chat_id}</code>{' 🔒' if chat_id in self.PERMANENT_BLACKLIST else ''}\n"
        
        await utils.answer(message, blacklist_msg)

    @loader.command()
    async def afkadd(self, message):
        """Добавить текущий чат или пользователя в черный список"""
        blacklist_chats = self.config["blacklist_chats"]
        
        try:
            if message.chat_id in self.PERMANENT_BLACKLIST:
                await utils.answer(message, "<emoji document_id=5778527486270770928>❌</emoji> <b>Этот чат/пользователь является частью постоянного черного списка!</b>")
                return

            if message.is_private:
                user_id = message.chat_id
                if user_id not in blacklist_chats:
                    blacklist_chats.append(user_id)
                    self.config["blacklist_chats"] = blacklist_chats
                    await utils.answer(message, "<emoji document_id=5309788666984415888>😊</emoji> <b>Пользователь добавлен в черный список</b>")
                else:
                    await utils.answer(message, "<emoji document_id=5778527486270770928>❌</emoji> <b>Этот пользователь уже в черном списке</b>")
            else:
                current_chat_id = message.chat_id
                
                if current_chat_id not in blacklist_chats:
                    blacklist_chats.append(current_chat_id)
                    self.config["blacklist_chats"] = blacklist_chats
                    await utils.answer(message, self.strings["chat_blacklisted"])
                else:
                    await utils.answer(message, self.strings["chat_already_blacklisted"])
        except Exception as e:
            await utils.answer(message, f"Ошибка: {str(e)}")

    @loader.command()
    async def afkdel(self, message):
        """Удалить текущий чат из черного списка"""
        blacklist_chats = self.config["blacklist_chats"]
        current_chat_id = message.chat_id
        
        if current_chat_id in self.PERMANENT_BLACKLIST:
            await utils.answer(message, "<emoji document_id=5778527486270770928>❌</emoji> <b>Этот чат/пользователь является частью постоянного черного списка и не может быть удален!</b>")
            return
        
        if current_chat_id in blacklist_chats:
            blacklist_chats.remove(current_chat_id)
            self.config["blacklist_chats"] = blacklist_chats
            await utils.answer(message, self.strings["chat_removed"])
        else:
            await utils.answer(message, self.strings["no_chat_in_blacklist"])

    def _validate_time(self, time_str):
        """
        Проверяет корректность времени
        Возвращает True, если время корректно, иначе False
        """
        try:
            time_pattern = r'^\d{1,2}:\d{2}$'
            if not re.match(time_pattern, time_str):
                return False
            
            hours, minutes = map(int, time_str.split(':'))
            
            if hours < 0 or hours > 23:
                return False
            if minutes < 0 or minutes > 59:
                return False
            
            return True
        except:
            return False

    def _parse_return_time(self, text):
        """Парсит время возвращения из текста"""
        time_pattern = r'\d{1,2}:\d{2}'
        match = re.search(time_pattern, text)
        if match and self._validate_time(match.group(0)):
            return match.group(0)
        return None

    def _afk_custom_text(self) -> str:
        """Генерация кастомного текста АФК"""
        now = datetime.datetime.now().replace(microsecond=0)
        gone = datetime.datetime.fromtimestamp(
            self._db.get(__name__, "gone")
        ).replace(microsecond=0)

        time = now - gone
        reason = self._db.get(__name__, "reason")
        return_time = self._db.get(__name__, "return_time", "не указано")
        zone = self.config["timezone"]
        
        return (
            ""
            + self.config["afk_text"].format(
                time=time,
                reason=reason,
                return_time=return_time,
                zone=zone
            )
        )

    async def _update_emoji_status(self, enable: bool = True):
        if not self._premium or not self.config["use_emoji_status"]:
            return
            
        try:
            if enable:
                await self._client(UpdateEmojiStatusRequest(
                    emoji_status=EmojiStatus(
                        document_id=self.config["afk_emoji_status_id"]
                    )
                ))
            else:
                if self.config["default_emoji_status_id"]:
                    await self._client(UpdateEmojiStatusRequest(
                        emoji_status=EmojiStatus(
                            document_id=self.config["default_emoji_status_id"]
                        )
                    ))
                else:
                    await self._client(UpdateEmojiStatusRequest(
                        emoji_status=EmojiStatusEmpty()
                    ))
        except Exception:
            pass

    @loader.command()
    async def afk(self, message):
        """[причина] [время] - включить/выключить АФК режим"""
        current_state = self._db.get(__name__, "afk", False)
    
        if current_state:
            await self._disable_afk_mode()
            m = await utils.answer(message, self.strings["bt_off_afk"])
            await asyncio.sleep(5)
            await m.delete()
        else:
            args = utils.get_args_raw(message)
            reason = args
            return_time = self._parse_return_time(args)
            
            if 'время' in args.lower() and not return_time:
                return await utils.answer(message, self.strings["invalid_time_format"])
            
            if return_time:
                reason = args.replace(return_time, '').strip()
            
            reason = reason or "Не указана"
            
            self._db.set(__name__, "reason", reason)
            self._db.set(__name__, "afk", True)
            self._db.set(__name__, "gone", time.time())
            self._db.set(__name__, "notified_users", [])
            self._db.set(__name__, "return_time", return_time or "не указано")
            
            await self._client(UpdateProfileRequest(last_name=f"{self.config['prefix']}" if self.config['prefix'] else ""))

            if self._db.get(__name__, "change_bio", True):
                try:
                    await self._client(UpdateProfileRequest(about=self._db.get(__name__, "about", "")))
                except Exception:
                    pass

            await self._update_emoji_status(True)
            
            buttons = []
            if self.config["button"]:
                if self.config["feedback"]:
                    buttons.append(
                        {"text": self.strings["contact_feedback"], "callback": self._contact_feedback}
                    )
                
                buttons.append(
                    {"text": self.strings["turn_off_afk"], "callback": self._turn_off_afk}
                )
            
            if buttons:
                m = await self.inline.form(
                    f"<b>АФК режим включен</b>\n"
                    f"<emoji document_id=5445161912985724546>✏️</emoji> <b>Причина:</b> <b>{reason}</b>\n"
                    f"<emoji document_id=5287758504117940879>⌚️</emoji> <b>Время возвращения:</b> {return_time or 'не указано'}",
                    message=message,
                    reply_markup=buttons
                )
            else:
                m = await utils.answer(
                    message,
                    f"<b>АФК режим включен</b>\n"
                    f"<emoji document_id=5445161912985724546>✏️</emoji> <b>Причина:</b> <b>{reason}</b>\n"
                    f"<emoji document_id=5287758504117940879>⌚️</emoji> <b>Время возвращения:</b> {return_time or 'не указано'}"
                )

            await asyncio.sleep(5)
            await m.delete()

    async def _contact_feedback(self, call: InlineCall):
        """Отправка сообщения в feedback бота"""
        if not self.config["feedback"]:
            await call.answer("Feedback бот не настроен", show_alert=True)
            return

        try:
            await self._client.send_message(
                self.config["feedback"], 
                f"Пользователь {self._me.first_name} сейчас в АФК\n"
                f"Причина: {self._db.get(__name__, 'reason', 'Не указана')}"
            )
            await call.answer("Сообщение отправлено", show_alert=True)
        except Exception as e:
            await call.answer(f"Ошибка: {str(e)}", show_alert=True)

    async def _turn_off_afk(self, call: InlineCall):
        """Выключение АФК режима через кнопку"""
        await self._disable_afk_mode()
        await call.answer("АФК режим выключен", show_alert=True)
    
    @loader.watcher()
    async def watcher(self, message):
        """Основной обработчик АФК-режима для отправки уведомлений"""
        if not isinstance(message, types.Message):
            return

        try:
            sender = await message.get_sender()
            if sender and sender.bot:
                return
        except Exception:
            pass

        blacklist_chats = self.config["blacklist_chats"]
        
        if message.chat_id in blacklist_chats:
            return

        is_mentioned = message.mentioned
        is_private_message = getattr(message.to_id, "user_id", None) == self._me.id

        if not (is_mentioned or is_private_message):
            return

        afk_state = self._db.get(__name__, "afk", False)
        if not afk_state:
            return

        sender_id = message.from_id
        notified_users = self._db.get(__name__, "notified_users", [])
        
        if sender_id in notified_users:
            return
        
        notified_users.append(sender_id)
        self._db.set(__name__, "notified_users", notified_users)

        now = datetime.datetime.now().replace(microsecond=0)
        gone = datetime.datetime.fromtimestamp(
            self._db.get(__name__, "gone")
        ).replace(microsecond=0)
        time_diff = now - gone
        reason = self._db.get(__name__, "reason", "Не указана")
        return_time = self._db.get(__name__, "return_time", "не указано")
        zone = self.config["timezone"]

        if not self.config["afk_text"]:
            afk_message = (
                "<emoji document_id=5287613458777387650>😴</emoji> <b>Сейчас я в АФК режиме</b>\n"
                f"<emoji document_id=5287737368583876982>🌀</emoji> Был <b>онлайн</b>: <code>{time_diff}</code> назад\n"
                f"<emoji document_id=5445161912985724546>✏️</emoji> Причина: <b>{reason}</b>\n"
                f"<emoji document_id=5287758504117940879>⌚️</emoji> Время возвращения: {return_time}\n"
                f"<emoji document_id=5287758504117940879>🌍</emoji> Часовой пояс: {zone}"
            )
        else:
            afk_message = self._afk_custom_text()

        await utils.answer(message, afk_message)
