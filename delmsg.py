# ———————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————                                                
#          _____                    _____                    _____                    _____                    _____                    _____  
#         /\    \                  /\    \                  /\    \                  /\    \                  /\    \                  /\    \ 
#        /::\    \                /::\    \                /::\____\                /::\    \                /::\    \                /::\____\
#       /::::\    \              /::::\    \              /::::|   |                \:::\    \               \:::\    \              /:::/    /
#      /::::::\    \            /::::::\    \            /:::::|   |                 \:::\    \               \:::\    \            /:::/    / 
#     /:::/\:::\    \          /:::/\:::\    \          /::::::|   |                  \:::\    \               \:::\    \          /:::/    /  
#    /:::/  \:::\    \        /:::/__\:::\    \        /:::/|::|   |                   \:::\    \               \:::\    \        /:::/    /   
#   /:::/    \:::\    \      /::::\   \:::\    \      /:::/ |::|   |                   /::::\    \              /::::\    \      /:::/    /    
#  /:::/    / \:::\    \    /::::::\   \:::\    \    /:::/  |::|   | _____    ____    /::::::\    \    ____    /::::::\    \    /:::/    /     
# /:::/    /   \:::\ ___\  /:::/\:::\   \:::\    \  /:::/   |::|   |/\    \  /\   \  /:::/\:::\    \  /\   \  /:::/\:::\    \  /:::/    /      
#/:::/____/     \:::|    |/:::/  \:::\   \:::\____\/:: /    |::|   /::\____\/::\   \/:::/  \:::\____\/::\   \/:::/  \:::\____\/:::/____/       
#\:::\    \     /:::|____|\::/    \:::\  /:::/    /\::/    /|::|  /:::/    /\:::\  /:::/    \::/    /\:::\  /:::/    \::/    /\:::\    \       
# \:::\    \   /:::/    /  \/____/ \:::\/:::/    /  \/____/ |::| /:::/    /  \:::\/:::/    / \/____/  \:::\/:::/    / \/____/  \:::\    \      
#  \:::\    \ /:::/    /            \::::::/    /           |::|/:::/    /    \::::::/    /            \::::::/    /            \:::\    \     
#   \:::\    /:::/    /              \::::/    /            |::::::/    /      \::::/____/              \::::/____/              \:::\    \    
#    \:::\  /:::/    /               /:::/    /             |:::::/    /        \:::\    \               \:::\    \               \:::\    \   
#     \:::\/:::/    /               /:::/    /              |::::/    /          \:::\    \               \:::\    \               \:::\    \  
#      \::::::/    /               /:::/    /               /:::/    /            \:::\    \               \:::\    \               \:::\    \ 
#       \::::/    /               /:::/    /               /:::/    /              \:::\____\               \:::\____\               \:::\____\
#        \::/____/                \::/    /                \::/    /                \::/    /                \::/    /                \::/    /
#         ~~                       \/____/                  \/____/                  \/____/                  \/____/                  \/____/ 
#————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# meta developer: @stupid_alien_mods

from hikka import loader, utils
from hikkatl.errors import MessageIdInvalidError
from hikkatl import functions, types

@loader.tds
class DeleteMessagesMod(loader.Module):
    """Модуль для удаления определённого количества сообщений пользователя"""
    strings = {
        "name": "DeleteMessagesMod",
        "invalid_number": "❗ Укажите корректное количество сообщений для удаления.",
        "deleted": "✅ Удалено {count} сообщений."
    }

    async def delcmd(self, message):
        """Удалить указанное количество сообщений пользователя. Использование: .del <количество>"""
        args = utils.get_args_raw(message)

        if not args.isdigit():
            await utils.answer(message, self.strings["invalid_number"])
            return

        count = int(args)


        results = await message.client(functions.messages.SearchRequest(
            peer=message.peer_id,  
            q=" ", 
            filter=types.InputMessagesFilterEmpty(), 
            min_date=None,
            max_date=None,
            offset_id=0,
            add_offset=0,
            limit=count + 1,  
            max_id=0,
            min_id=0,
            from_id=types.InputPeerSelf(),
            hash=0
        ))

        if not results.messages:
            await utils.answer(message, self.strings["invalid_number"])
            return

        messages = [msg.id for msg in results.messages]

        deleted_count = 0

        for msg_id in messages:
            try:
                await message.client.delete_messages(message.chat_id, [msg_id])
                deleted_count += 1
            except MessageIdInvalidError:
                pass  

        await utils.answer(message, self.strings["deleted"].format(count=deleted_count-1))  

