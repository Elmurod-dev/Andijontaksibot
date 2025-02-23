# from aiogram.types import InlineKeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder
#
#
# def admin_inline():
#     ikb = InlineKeyboardBuilder()
#     ikb.add(InlineKeyboardButton(text='Admin',url='http://t.me/ElmurodNarzullayev'),
#             InlineKeyboardButton(text='Statistika',callback_data='statistik'))
#     return ikb.as_markup(resize=True)
#
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

admin_done_inline_keyboard = InlineKeyboardBuilder()
admin_done_inline_keyboard.add(
    InlineKeyboardButton(text="✅ Done", callback_data="done"),
)

driver_accept_inline_keyboard = InlineKeyboardBuilder()
driver_accept_inline_keyboard.add(
    InlineKeyboardButton(text='✅ Qabul qilish', callback_data='accept')
)
ok = InlineKeyboardBuilder()
ok.add(
    InlineKeyboardButton(text='Ok', callback_data='ok')
)

cancel_order_inline_keyboard = InlineKeyboardBuilder()
cancel_order_inline_keyboard.add(
    InlineKeyboardButton(text='❌ Bekor qilish', callback_data='cancel')
)
