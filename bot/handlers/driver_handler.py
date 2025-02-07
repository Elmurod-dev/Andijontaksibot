from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.dispacher import dp

driver_router = Router()
@driver_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
