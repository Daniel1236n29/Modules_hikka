# Name: deff2
# meta developer: @daniilmods
# код взял от @mqone
# ---------------------------------------------------------------------------------

from .. import loader


@loader.tds
class deff2(loader.Module):
    """Отправляет деффа2"""

    strings = {"name": "гс и кружки2"}

    async def могуcmd(self, message):
        """почему свинью? потому что я могу [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/3",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def левcmd(self, message):
        """ ты по телефоныэу леф толстой а деле хуй простой [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/4",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def ракеткаcmd(self, message):
        """наша задача это заными схемами [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/5",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def анимкcmd(self, message):
        """Э, анимешник баля [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/ajskalqpwoe/12",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def овцаcmd(self, message):
        """ты там соли перекурила? [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/7",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def обоснуйcmd(self, message):
        """ты обоснуй свои слова [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/8",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def мамуcmd(self, message):
        """маму тыою ебал на твоейже волосатой жопе [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/12",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def гаражекcmd(self, message):
        """гаражек [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/13",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def роблоксcmd(self, message):
        """Проебал акк робоокса [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/14",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return
     
    async def 2метраcmd(self, message):
        """я 2 метра ростом [гс]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/15",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return
     
    async def оксимиронcmd(self, message):
        """Я сру под оксимирона [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/17",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def кирилcmd(self, message):
        """кирил [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/18",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return

    async def котикcmd(self, message):
        """кот [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/19",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return
     
    async def славяниcmd(self, message):
        """хз [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/20",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return
     
    async def нечеловекcmd(self, message):
        """зкленый слон [кружок]"""

        reply = await message.get_reply_message()
        await message.delete()
        await message.client.send_file(
            message.to_id,
            "https://t.me/gs_and_crygi/21",
            voice_note=True,
            reply_to=reply.id if reply else None,
        )
        return