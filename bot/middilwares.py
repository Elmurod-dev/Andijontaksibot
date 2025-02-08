from aiogram.utils.i18n import FSMI18nMiddleware


async def all_middleware(dp , i18n):
    dp.update.middleware(FSMI18nMiddleware(i18n))

from aiogram import BaseMiddleware
from aiogram.types import Message
from datetime import datetime
from db import db  # import the global db session
from db.models import Driver

class PermissionMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event: Message, data: dict):
        # Haydovchini DB orqali tekshirish
        driver_login = event.from_user.username
        driver = await db._session.execute(
            db._session.query(Driver).filter_by(login=driver_login)
        )
        driver = driver.scalars().first()

        if not driver:
            await event.answer("Siz ro'yxatdan o'tmagansiz.")
            return

        # Ruxsat muddati tugaganini tekshirish
        if driver.permission_date < datetime.now():
            await event.answer("Sizning ruxsat muddati tugagan. Iltimos, yangilang.")
            return

        # Muvaffaqiyatli bo'lsa davom ettirish
        data["driver"] = driver
        return await handler(event, data)
