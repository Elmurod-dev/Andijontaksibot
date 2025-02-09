from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.utils.i18n import FSMI18nMiddleware

from db.models import Driver


async def all_middleware(dp, i18n):
    dp.update.middleware(FSMI18nMiddleware(i18n))


class PermissionDateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        print({type(event)})

        if isinstance(event, Update):
            if event.message:
                print("shu event")
                user = await Driver.get(id_=event.message.from_user.id)
                if user:

                    if user.permission_date < datetime.utcnow():
                        await Driver.update(id_=user.id, is_active=False)
                        await event.message.answer(
                            "Sizning vaqtningiz tugagan. Yangi ro'yxatdan o'tish uchun admin bilan bog'laning.")
                    else:
                        await Driver.update(id_=user.id, is_active=True)
                        return

            elif event.callback_query:
                print("CallbackQuery.")
                user = await Driver.get(id_=event.callback_query.from_user.id)
                if user:
                    if user.permission_date < datetime.utcnow():
                        await Driver.update(id_=user.id,is_active=False)
                        await event.callback_query.answer(
                            "Sizning vaqtningiz tugagan. Yangi ro'yxatdan o'tish uchun admin bilan bog'laning. +998941142110")
                    else:
                        await Driver.update(id_=user.id, is_active=True)
                        return
            else:
                print("Boshqacha")
                return await handler(event, data)

        return await handler(event, data)
