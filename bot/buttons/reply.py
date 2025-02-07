from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder




def contact_btn():
    rkb = ReplyKeyboardBuilder()
    rkb.add(
        KeyboardButton(text="📞 Share contact ",request_contact=True)
    )
    return rkb.as_markup(resize_keyboard=True)

def generate_btn(data, just_list):
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[KeyboardButton(text=i) for i in data])
    rkb.adjust(*just_list)
    return rkb.as_markup(resize_keyboard=True)
