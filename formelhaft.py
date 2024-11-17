__version__ = (1, 0, 0)

# meta developer: @shrimp_mod

from .. import loader, utils
from telethon.tl.types import Message
import asyncio

@loader.tds
class TemplateResponderMod(loader.Module):
    """Модуль для автоматических ответов по шаблонам"""
    
    strings = {
        "name": "TemplateResponder",
        "template_saved": "✅ Шаблон {} успешно сохранен: {}",
        "template_deleted": "✅ Шаблон {} успешно удален",
        "template_not_found": "❌ Шаблон {} не найден",
        "no_templates": "❌ Нет сохраненных шаблонов",
        "current_templates": "📝 Текущие шаблоны:\n\n{}",
        "auto_enabled": "✅ Автоответчик включен в этом чате с шаблоном {}",
        "auto_disabled": "❌ Автоответчик выключен в этом чате",
        "active_chats": "📊 Активные чаты с автоответчиком:\n\n{}",
        "invalid_template": "❌ Укажите номер шаблона и текст\nПример: .settemplate 1 Ответ: {retext}",
        "template_list_item": "Шаблон {}: {}"
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.auto_chats = self._db.get(self.strings["name"], "auto_chats", {})
        self.templates = self._db.get(self.strings["name"], "templates", {})

    def get_template(self, number):
        return self.templates.get(str(number))

    def save_templates(self):
        self._db.set(self.strings["name"], "templates", self.templates)

    def save_auto_chats(self):
        self._db.set(self.strings["name"], "auto_chats", self.auto_chats)

    async def send_and_delete(self, message, text, delay=3):
        reply = await utils.answer(message, text)
        await asyncio.sleep(delay)
        await reply.delete()

    async def settemplatecmd(self, message):
        """Установить шаблон. Использование: .settemplate <номер> <текст шаблона>"""
        args = utils.get_args_raw(message).split(maxsplit=1)
        
        if len(args) != 2 or not args[0].isdigit():
            await utils.answer(message, self.strings["invalid_template"])
            return

        template_num = args[0]
        template_text = args[1]
        
        self.templates[template_num] = template_text
        self.save_templates()
        
        await utils.answer(
            message,
            self.strings["template_saved"].format(template_num, template_text)
        )

    async def deltemplatecmd(self, message):
        """Удалить шаблон. Использование: .deltemplate <номер>"""
        args = utils.get_args_raw(message)
        
        if not args or not args.isdigit():
            await utils.answer(message, "❌ Укажите номер шаблона")
            return

        if args in self.templates:
            del self.templates[args]
            self.save_templates()
            await utils.answer(message, self.strings["template_deleted"].format(args))
        else:
            await utils.answer(message, self.strings["template_not_found"].format(args))

    async def templatescmd(self, message):
        """Показать все шаблоны"""
        if not self.templates:
            await utils.answer(message, self.strings["no_templates"])
            return

        templates_text = ""
        for num, text in sorted(self.templates.items(), key=lambda x: int(x[0])):
            templates_text += self.strings["template_list_item"].format(num, text) + "\n"

        await utils.answer(
            message,
            self.strings["current_templates"].format(templates_text)
        )

    async def autooncmd(self, message):
        """Включить автоответчик в чате. Использование: .autoon <номер шаблона>"""
        args = utils.get_args_raw(message)
        
        if not args or not args.isdigit():
            await utils.answer(message, "❌ Укажите номер шаблона")
            return

        if args not in self.templates:
            await utils.answer(message, self.strings["template_not_found"].format(args))
            return

        chat = str(message.chat_id)
        self.auto_chats[chat] = args
        self.save_auto_chats()
        
        await self.send_and_delete(
            message, 
            self.strings["auto_enabled"].format(args)
        )

    async def autooffcmd(self, message):
        """Выключить автоответчик в чате"""
        chat = str(message.chat_id)
        
        if chat in self.auto_chats:
            del self.auto_chats[chat]
            self.save_auto_chats()
        
        await self.send_and_delete(message, self.strings["auto_disabled"])

    async def autochatscmd(self, message):
        """Показать список чатов с активным автоответчиком"""
        if not self.auto_chats:
            await utils.answer(message, "❌ Нет активных чатов с автоответчиком")
            return

        chats_info = []
        for chat_id, template in self.auto_chats.items():
            try:
                chat = await self._client.get_entity(int(chat_id))
                chat_name = chat.title if hasattr(chat, 'title') else chat.first_name
                template_text = self.templates.get(template, "Шаблон не найден")
                chats_info.append(f"• {chat_name}:\nШаблон {template}: {template_text}")
            except Exception:
                template_text = self.templates.get(template, "Шаблон не найден")
                chats_info.append(f"• Чат {chat_id}:\nШаблон {template}: {template_text}")

        await utils.answer(
            message,
            self.strings["active_chats"].format("\n".join(chats_info))
        )

    async def watcher(self, message):
        if message.out:
            return
        
        chat = str(message.chat_id)
        if chat not in self.auto_chats:
            return

        template_num = self.auto_chats[chat]
        template = self.get_template(template_num)
        
        if template and message.text:
            response = template.replace("{retext}", message.text)
            await message.reply(response)