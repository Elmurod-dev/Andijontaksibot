import asyncio
import logging
import sys
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.dispacher import TOKEN
from bot.handlers import dp
# from bot.handlers.employee_handler import base_handler
from bot.middilwares import all_middleware, PermissionDateMiddleware
from db.utils import db
from db.models import *

dp.update.middleware(PermissionDateMiddleware())
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # await bot.delete_webhook()
    # await base_handler(bot,dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())