__version__ = (2, 4, 2)

import asyncio
import datetime
import time
import re

from telethon import types
from telethon.tl.functions.account import UpdateProfileRequest, UpdateEmojiStatusRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import EmojiStatus, EmojiStatusEmpty

from .. import loader, utils
from ..inline.types import InlineCall

class UnknownAFKMod(loader.Module):
    """"""

    async def client_ready(self, client, db):
        self._me = await client.get_me()
        self._premium = self._me.premium
        if not self._db.get(__name__, "notified_users"):
            self._db.set(__name__, "notified_users", [])

    strings = {
        "name": "UnknownAFK",
        "bt_off_afk": "🚫 <b>АФК</b> режим <b>отключен</b>!",
        "invalid_time_format": "❌ <b>Неверный формат времени!</b>\n📝 Используйте формат <code>16:30</code>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
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
                doc=lambda: "Кастомный текст афк. Используй {time} для времени, {reason} для причины и {return_time} для времени возвращения",
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
                True,
                doc=lambda: "Добавить кнопку отключения АФК режима?",
                validator=loader.validators.Boolean(),
            )
        )

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
        now = datetime.datetime.now().replace(microsecond=0)
        gone = datetime.datetime.fromtimestamp(
            self._db.get(__name__, "gone")
        ).replace(microsecond=0)

        time = now - gone
        reason = self._db.get(__name__, "reason")
        return_time = self._db.get(__name__, "return_time", "не указано")
        
        return (
            ""
            + self.config["afk_text"].format(
                time=time,
                reason=reason,
                return_time=return_time
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
            self._db.set(__name__, "afk", False)
            self._db.set(__name__, "gone", None)
            self._db.set(__name__, "notified_users", [])
            self._db.set(__name__, "return_time", None)
            
            if self._db.get(__name__, "change_name", False):
                await message.client(UpdateProfileRequest(last_name=" "))
                
            if self._db.get(__name__, "change_bio", False):
                try:
                    await message.client(UpdateProfileRequest(about=self._db.get(__name__, "about", "")))
                except Exception:
                    pass

            await self._update_emoji_status(False)
            m = await utils.answer(message, "<emoji document_id=5287611315588707430>❌</emoji> <b>АФК режим выключен</b>")
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
            
            try:
                if self._db.get(__name__, "change_name", True):
                    await self._client(UpdateProfileRequest(last_name=""))
            except Exception:
                pass

            if self._db.get(__name__, "change_bio", True):
                try:
                    await self._client(UpdateProfileRequest(about=self._db.get(__name__, "about", "")))
                except Exception:
                    pass

            await self._update_emoji_status(True)
            m = await utils.answer(
                message,
                f"<b>АФК режим включен</b>\n"
                f"<emoji document_id=5445161912985724546>✏️</emoji> <b>Причина:</b> <b>{reason}</b>\n"
                f"<emoji document_id=5287758504117940879>⌚️</emoji> <b>Примерное время возвращения:</b> {return_time or 'не указано'}"
            )

        await asyncio.sleep(5)
        await m.delete()


    @loader.watcher()
    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return

        if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.id:
            afk_state = self._db.get(__name__, "afk", False)
            if not afk_state:
                return

            sender_id = message.from_id
            
            notified_users = self._db.get(__name__, "notified_users", [])
            
            if sender_id in notified_users:
                return
                
            notified_users.append(sender_id)
            self._db.set(__name__, "notified_users", notified_users)

            if not self.config["afk_text"]:
                now = datetime.datetime.now().replace(microsecond=0)
                gone = datetime.datetime.fromtimestamp(
                    self._db.get(__name__, "gone")
                ).replace(microsecond=0)
                time = now - gone
                reason = self._db.get(__name__, "reason")
                return_time = self._db.get(__name__, "return_time", "не указано")

                await utils.answer(
                    message,
                    "<emoji document_id=5287613458777387650>😴</emoji> <b>Сейчас я в АФК режиме</b>\n"
                    f"</b><emoji document_id=5287737368583876982>🌀</emoji> Был <b>онлайн</b>: <code>{time}</code> назад\n"
                    f"<emoji document_id=5445161912985724546>✏️</emoji> Причина: <b>{reason}</b>\n"
                    f"<emoji document_id=5287758504117940879>⌚️</emoji> Примерное время возвращения: {return_time}"
                )
            else:
                await utils.answer(message, self._afk_custom_text())