from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.dispacher import dp
from db.models import Product

main_router = Router()
@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await Product.create(name="Test",price=123)
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
