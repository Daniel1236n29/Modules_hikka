__version__ = (3, 1, 2)

# meta developer: @shrimp_mod

from .. import loader, utils
import hikkatl

@loader.tds
class CMCMod(loader.Module):
    """Подсчет сообщений, медиа и статистики пользователей в чате"""
    strings = {"name": "CMC"}

    async def client_ready(self, client, db):
        self._client = client
        self._me = await client.get_me()

    async def get_message_stats(self, chat_id, user_id, is_private=False):
        """Подсчет сообщений и медиа для чатов и ЛС"""
        stats = {
            "total_messages": 0,
            "stickers": 0,
            "gifs": 0,
            "photos": 0,
            "videos": 0,
            "voice": 0,
            "video_notes": 0,
            "documents": 0,
            "total_media": 0
        }
        
        offset_id = 0
        limit = 0

        while True:
            if is_private:
                history = await self._client(hikkatl.functions.messages.GetHistoryRequest(
                    peer=chat_id,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))
                messages = history.messages
            else:
                messages = await self._client(hikkatl.functions.messages.SearchRequest(
                    peer=chat_id,
                    q="",
                    filter=hikkatl.types.InputMessagesFilterEmpty(),
                    min_date=None,
                    max_date=None,
                    offset_id=offset_id,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    from_id=user_id,
                    hash=0
                ))
                messages = messages.messages

            if not messages:
                break

            for msg in messages:
                if getattr(msg.from_id, 'user_id', msg.from_id) == user_id:
                    stats["total_messages"] += 1
                    
                    if msg.sticker:
                        stats["stickers"] += 1
                        stats["total_media"] += 1
                    elif msg.gif:
                        stats["gifs"] += 1
                        stats["total_media"] += 1
                    elif msg.photo:
                        stats["photos"] += 1
                        stats["total_media"] += 1
                    elif msg.video:
                        stats["videos"] += 1
                        stats["total_media"] += 1
                    elif msg.voice:
                        stats["voice"] += 1
                        stats["total_media"] += 1
                    elif msg.video_note:
                        stats["video_notes"] += 1
                        stats["total_media"] += 1
                    elif msg.document:
                        stats["documents"] += 1
                        stats["total_media"] += 1

            offset_id = messages[-1].id

        return stats

    async def get_chat_participants(self, chat_id):
        """Получение всех участников чата"""
        return await self._client.get_participants(chat_id)

    async def get_chat_total_stats(self, chat_id):
        """Получение общей статистики чата"""
        stats = {
            "total_messages": 0,
            "total_members": 0,
            "admins": 0,
            "deleted_accounts": 0,
            "media_messages": 0
        }
        
        participants = await self.get_chat_participants(chat_id)
        stats["total_members"] = len(participants)
        stats["deleted_accounts"] = len([u for u in participants if u.deleted])
        stats["admins"] = len([u for u in participants if u.participant and getattr(u.participant, 'admin_rights', None)])


        messages = await self._client(hikkatl.functions.messages.SearchRequest(
            peer=chat_id,
            q="",
            filter=hikkatl.types.InputMessagesFilterEmpty(),
            min_date=None,
            max_date=None,
            offset_id=0,
            add_offset=0,
            limit=0,
            max_id=0,
            min_id=0,
            hash=0
        ))
        
        stats["total_messages"] = messages.count

        media_messages = await self._client(hikkatl.functions.messages.SearchRequest(
            peer=chat_id,
            q="",
            filter=hikkatl.types.InputMessagesFilterPhotoVideo(),
            min_date=None,
            max_date=None,
            offset_id=0,
            add_offset=0,
            limit=0,
            max_id=0,
            min_id=0,
            hash=0
        ))
        
        stats["media_messages"] = media_messages.count

        return stats

    @loader.unrestricted
    async def mymsgcmd(self, message):
        """Подсчитывает все ваши сообщения и медиафайлы."""
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = getattr(chat, 'title', None) or f"this {'chat' if is_private else 'channel'}"

        await utils.answer(message, "Начинаю подсчет ваших сообщений...\n Это может занять некоторое время.")
        
        stats = await self.get_message_stats(chat_id, self._me.id, is_private=is_private)
        
        result = (
            f"<emoji document_id=5886412370347036129>👤</emoji> Ваша статистика в <u>'{chat_title}'</u>:\n\n"
            f"<emoji document_id=5886436057091673541>💬</emoji> Всего сообщений: <b>{stats['total_messages']}</b>\n"
            f"<emoji document_id=5931472654660800739>📊</emoji> Всего медиаконтента: <b>{stats['total_media']}</b>\n"
            f"└ <emoji document_id=6030466823290360017>🖼</emoji> Стикеров: <b>{stats['stickers']}</b>\n"
            f"└ <emoji document_id=5944777041709633960>🎞</emoji> GIF: <b>{stats['gifs']}</b>\n"
            f"└ <emoji document_id=6048390817033228573>📷</emoji> Фото: <b>{stats['photos']}</b>\n"
            f"└ <emoji document_id=5944753741512052670>📷</emoji> Видео: <b>{stats['videos']}</b>\n"
            f"└ <emoji document_id=6030722571412967168>🎤</emoji> Голосовых: <b>{stats['voice']}</b>\n"
            f"└ <emoji document_id=5944753741512052670>📷</emoji> Кружков: <b>{stats['video_notes']}</b>\n"
            f"└ <emoji document_id=6039630677182254664>📂</emoji> Файлов: <b>{stats['documents']}</b>"
        )
        
        await utils.answer(message, result)

    @loader.unrestricted
    async def usermsgcmd(self, message):
        """Подсчитывает все сообщения и медиафайлы указанного пользователя. Использование: .usermsg <реплай или @username>"""
        args = utils.get_args_raw(message)
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = getattr(chat, 'title', None) or f"this {'chat' if is_private else 'channel'}"

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

        await utils.answer(message, f"Начинаю подсчет сообщений пользователя {username}...")

        stats = await self.get_message_stats(chat_id, user.id, is_private=is_private)
        
        result = (
            f"<emoji document_id=5886412370347036129>👤</emoji> Статистика {username} в <u>'{chat_title}'</u>:\n\n"
            f"<emoji document_id=5886436057091673541>💬</emoji> Всего сообщений: <b>{stats['total_messages']}</b>\n"
            f"<emoji document_id=5931472654660800739>📊</emoji> Всего медиаконтента: <b>{stats['total_media']}</b>\n\n"
            f"└ <emoji document_id=6030466823290360017>🖼</emoji> Стикеров: <b>{stats['stickers']}</b>\n"
            f"└ <emoji document_id=5944777041709633960>🎞</emoji> GIF: <b>{stats['gifs']}</b>\n"
            f"└ <emoji document_id=6048390817033228573>📷</emoji> Фото: <b>{stats['photos']}</b>\n"
            f"└ <emoji document_id=5944753741512052670>📷</emoji> Видео: <b>{stats['videos']}</b>\n"
            f"└ <emoji document_id=6030722571412967168>🎤</emoji> Голосовых: <b>{stats['voice']}</b>\n"
            f"└ <emoji document_id=5944753741512052670>📷</emoji> Кружков: <b>{stats['video_notes']}</b>\n"
            f"└ <emoji document_id=6039630677182254664>📂</emoji> Файлов: <b>{stats['documents']}</b>"
        )
        
        await utils.answer(message, result)

    @loader.unrestricted
    async def allmsgcmd(self, message):
        """Подсчитывает сообщения всех участников."""
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        is_private = chat_id == self._me.id or getattr(chat, 'first_name', None) is not None
        chat_title = getattr(chat, 'title', None) or f"this {'chat' if is_private else 'channel'}"

        await utils.answer(message, f"Начинаю подсчет сообщений всех пользователей в <u>'{chat_title}'</u>...\n Это может занять некоторое время.")

        participants = await self.get_chat_participants(chat_id)

        if not participants:
            await utils.answer(message, "Не удалось получить участников чата.")
            return

        users_message_count = []
        
        for user in participants:
            if user.deleted:
                continue
                
            username = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

            try:
                messages = await self._client(hikkatl.functions.messages.SearchRequest(
                    peer=chat_id,
                    q="",
                    filter=hikkatl.types.InputMessagesFilterEmpty(),
                    min_date=None,
                    max_date=None,
                    offset_id=0,
                    add_offset=0,
                    limit=0,
                    max_id=0,
                    min_id=0,
                    from_id=user.id,
                    hash=0
                ))
                message_count = messages.count
            except Exception:
                message_count = 0

            if message_count > 0: 
                users_message_count.append((username, message_count))

        users_message_count.sort(key=lambda x: x[1], reverse=True)

        result = f"Статистика сообщений в <u>'{chat_title}'</u>:\n\n"
        for username, count in users_message_count:
            result += f"<emoji document_id=5886412370347036129>👤</emoji> {username}: <emoji document_id=5886436057091673541>💬</emoji><b>{count}</b> сообщений\n"

        await utils.answer(message, result)

    @loader.unrestricted
    async def chatstatscmd(self, message):
        """Показывает полную статистику чата."""
        chat_id = message.peer_id
        chat = await self._client.get_entity(chat_id)
        chat_title = getattr(chat, 'title', None) or "this channel"

        await utils.answer(message, f"Собираю статистику чата <u>'{chat_title}'</u>...")

        stats = await self.get_chat_total_stats(chat_id)
        
        result = (
            f"<emoji document_id=5931472654660800739>📊</emoji> Статистика чата <u>'{chat_title}'</u>:\n\n"
            f"<emoji document_id=5942877472163892475>👥</emoji> Участников: <b>{stats['total_members']}</b>\n"
            f"└ <emoji document_id=5778423822940114949>🛡</emoji> Администраторов: <b>{stats['admins']}</b>\n"
            f"└ <emoji document_id=5872829476143894491>🚫</emoji> Удаленных аккаунтов: <b>{stats['deleted_accounts']}</b>\n\n"
            f"<emoji document_id=5886436057091673541>💬</emoji> Всего сообщений: <b>{stats['total_messages']}</b>\n"
            f"└ <emoji document_id=6048390817033228573>📷</emoji> Медиа сообщений: <b>{stats['media_messages']}</b>\n"
        )

        await utils.answer(message, result)
