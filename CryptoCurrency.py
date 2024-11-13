# meta developer: @shrimp_mod

from telethon import events
from .. import loader, utils
import aiohttp
import json

@loader.tds
class CryptoCurrencyMod(loader.Module):
    """Модуль для отображения текущего курса криптовалют"""
    strings = {"name": "CryptoCurrency"}

    async def get_exchange_rates(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://open.er-api.com/v6/latest/USD") as resp:
                data = await resp.json()
                return data['rates']['RUB'], data['rates']['EUR']

    @loader.command(
        doc="Показать текущий курс криптовалюты."
    )
    async def crypto(self, message):
        """Показывает текущий курс криптовалюты в рублях, долларах и евро"""
        query = utils.get_args_raw(message)
        if not query:
            return await utils.answer(message, "Пожалуйста, укажите тикер или название криптовалюты.")

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coinlore.net/api/tickers/?start=0&limit=100") as resp:
                data = await resp.json()

        coin = next((item for item in data['data'] if query.lower() in item['name'].lower() or query.lower() in item['symbol'].lower()), None)

        if not coin:
            return await utils.answer(message, f"Криптовалюта '{query}' не найдена.")

        price_usd = float(coin['price_usd'])
        usd_rub_rate, usd_eur_rate = await self.get_exchange_rates()
        
        price_rub = price_usd * usd_rub_rate
        price_eur = price_usd * usd_eur_rate

        response = f"💰 {coin['name']} ({coin['symbol']})\n\n"
        response += f"USD: ${price_usd:.2f}\n"
        response += f"RUB: ₽{price_rub:.2f}\n"
        response += f"EUR: €{price_eur:.2f}\n"

        await utils.answer(message, response)
