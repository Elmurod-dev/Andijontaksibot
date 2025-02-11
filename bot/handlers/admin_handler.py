from datetime import datetime
import re

from aiogram.types import CallbackQuery

from aiogram import Router,F

from db.models import Driver

admin_router=Router()
async def parse_driver_info(info):
    data = {}

    data['id'] = int(re.search(r"ID: (\d+)", info).group(1))

    data['phone_number'] = re.search(r"Telefon raqam: (\+[\d]+)", info).group(1)

    data['full_name'] = re.search(r"Ism Sharifi: (\w+)", info).group(1)

    data['car_model'] = re.search(r"Avtomobil: (\w+)", info).group(1)

    data['car_number'] = re.search(r"Mashina raqami: (\w+)", info).group(1)

    permission_date = re.search(r"Permission date: (\d{4}-\d{2}-\d{2})", info).group(1)
    data['permission_date'] = datetime.strptime(permission_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    # Status

    return data

@admin_router.callback_query()
async def admin_handler(query: CallbackQuery):
    if query.data == 'done':
        message_text=query.message.text
        data=await parse_driver_info(message_text)
        await Driver.create(**data)
        message = """
           <b>🟢 Haydovchi muvafaqqiyatli ro'yxatga olindi!</b>
           """

        await query.message.answer(message, parse_mode='HTML')

@admin_router.callback_query()
async def admin_routerd(query: CallbackQuery) -> None:
    if query.data == "test":
        print("admin roueter")