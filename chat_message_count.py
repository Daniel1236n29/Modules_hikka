__version__ = (2, 0, 1)
# meta developer: @stupid_alien_mods
#----------------------------------------------------------------------------
from .. import loader, utils
import hikkatl

@loader.tds
class ChatMessageCounterMod(loader.Module):
    """Подсчет сообщений пользователей в чате или ЛС и вывод списка молчунов"""
    strings = {"name": "ChatMessageCounter"}

    async def client_ready(self, client, db):
        self._client = client
        self._me = await client.get_me()

    async def get_message_count(self, chat_id, user_id, is_private=False):
        """Подсчет сообщений для чатов и ЛС"""
        if is_private:
            total_count = 0
            offset_id = 0

            while True:
                #если лс
                history = await self._client(hikkatl.functions.messages.GetHistoryRequest(
                    peer=chat_id,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=100,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))

                if not history.messages:
                    break

                user_messages = [msg for msg in history.messages if getattr(msg.from_id, 'user_id', msg.from_id) == user_id]
                total_count += len(user_messages)
                offset_id = history.messages[-1].id

            return total_count
        else:
#если чат
            results = await self._client(hikkatl.functions.messages.SearchRequest(
                peer=chat_id,
                q=" ",
                filter=hikkatl.types.InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=0,
                max_id=0,
                min_id=0,
                from_id=user_id,
                hash=0
            ))
            return results.count

    async def get_chat_participants(self, chat_id):
        """Получение всех участников чата"""
        participants = await self._client.get_participants(chat_id)
        return participants

    def get_user_link(self, user):
        """Возвращает корректную ссылку для пользователей в ЛС"""
        if user.username:
            return f"@{user.username}"
        return f"{user.first_name}"

    @loader.unrestricted
    async def mymsgcmd(self, message):
        """Подсчитывает все ваши сообщения в чате или ЛС. Использование: .mymsg"""
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = chat.title if hasattr(chat, 'title') else chat.first_name

        await utils.answer(message, "Начинаю подсчет ваших сообщений... Это может занять некоторое время.")
        
        count = await self.get_message_count(chat_id, self._me.id, is_private=is_private)
        
        await utils.answer(message, f"Вы отправили {count} сообщений за всё время в чате или ЛС '{chat_title}'.")

    @loader.unrestricted
    async def usermsgcmd(self, message):
        """Подсчитывает все сообщения указанного пользователя в чате или ЛС. Использование: .usermsg <реплай или @username>"""
        args = utils.get_args_raw(message)
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = chat.title if hasattr(chat, 'title') else chat.first_name

        if message.is_reply:
            reply_message = await message.get_reply_message()
            user = await self._client.get_entity(reply_message.sender_id)
        elif args:
            try:
                user = await self._client.get_entity(args)
            except Exception:
                await utils.answer(message, "Не удалось найти пользователя. Убедитесь, что вы ввели правильный @username или ID.")
                return
        else:
            await utils.answer(message, "Пожалуйста, укажите @username, ID или сделайте реплай на сообщение пользователя.")
            return

        username = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        await utils.answer(message, f"Начинаю подсчет сообщений пользователя {username}.")

        count = await self.get_message_count(chat_id, user.id, is_private=is_private)
        
        await utils.answer(message, f"Пользователь {username} отправил {count} сообщений за всё время в чате или ЛС '{chat_title}'.")

    @loader.unrestricted
    async def allmsgcmd(self, message):
        """Подсчитывает сообщения всех участников в чате или ЛС и сортирует от большего к меньшему. Использование: .allmsg"""
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = chat.title if hasattr(chat, 'title') else chat.first_name

        await utils.answer(message, f"Начинаю подсчет сообщений всех пользователей в '{chat_title}'... Это может занять некоторое время.")

        participants = await self.get_chat_participants(chat_id)

        if not participants:
            await utils.answer(message, "Не удалось получить участников чата.")
            return

        users_message_count = []
        
        for user in participants:
            username = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

            try:
                message_count = await self.get_message_count(chat_id, user.id, is_private=is_private)
            except Exception:
                message_count = 0

            users_message_count.append((username, message_count))

        users_message_count.sort(key=lambda x: x[1], reverse=True)

        result_message = f"Статистика сообщений в чате '{chat_title}':\n\n"
        for username, count in users_message_count:
            result_message += f"{username}: {count} сообщений\n"

        await utils.answer(message, result_message)

    @loader.unrestricted
    async def silentcmd(self, message):
        """Выводит список пользователей, которые не отправили ни одного сообщения. Использование: .silent"""
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = chat.title if hasattr(chat, 'title') else chat.first_name

        await utils.answer(message, f"Ищу молчунов в '{chat_title}'... Это может занять некоторое время.")

        participants = await self.get_chat_participants(chat_id)

        if not participants:
            await utils.answer(message, "Не удалось получить участников чата.")
            return

        silent_users = []

        for user in participants:
            username = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            try:
                message_count = await self.get_message_count(chat_id, user.id, is_private=is_private)
            except Exception:
                message_count = 0

            if message_count == 0:
                silent_users.append(username)

        if silent_users:
            result_message = f"Молчуны (0 сообщений) в чате '{chat_title}':\n\n"
            result_message += ", ".join(silent_users)
        else:
            result_message = f"Нет молчунов в чате '{chat_title}'!"

        await utils.answer(message, result_message)
