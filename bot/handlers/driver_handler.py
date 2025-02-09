import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.buttons import reply, inline
from bot.state import DriverRegisterState
from db.models import User, Driver, Order

driver_router = Router()


# ============ driver send request to register ===========
@driver_router.message(F.text == "🚖 Haydovchi")
async def driver_handler(message: Message, state: FSMContext) -> None:
    user = await Driver.get(id_=message.from_user.id)
    if not user:
        await message.answer("Ma'lumotlaringiz topilmadi!\nIltimos telefon raqamingizni yuboring!",
                             reply_markup=reply.contact_btn())
        await state.set_state(DriverRegisterState.phone_number)


@driver_router.message(DriverRegisterState.phone_number, lambda message: message.contact is not None)
async def driver_contact_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(phone_number=message.contact.phone_number)
    await state.set_state(DriverRegisterState.full_name)
    await message.answer("Ism Sharifingiz? (to'liq yozilishi shart)")


@driver_router.message(DriverRegisterState.full_name)
async def driver_fullname_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(fullname=message.text)
    await state.set_state(DriverRegisterState.car_model)
    await message.answer("Avtomobilingiz rusumi? Masalan: Chevrolet Nexia 3")


@driver_router.message(DriverRegisterState.car_model)
async def driver_car_model(message: Message, state: FSMContext) -> None:
    await state.update_data(car_model=message.text)
    await state.set_state(DriverRegisterState.car_number)
    await message.answer("Avtomobilingiz raqami?\nMasalan: 10|E266|QA")


@driver_router.message(DriverRegisterState.car_number)
async def driver_car_number(message: Message, state: FSMContext) -> None:
    await state.update_data(car_number=message.text)
    data = await state.get_data()
    phone_number = data['phone_number']
    car_model = data['car_model']
    car_number = data['car_number']
    full_name = data['fullname']
    permission_date = (datetime.datetime.now() + datetime.timedelta(days=30)).date()

    message_txt = f"""Yangi Haydovchi 🚖

<b>ID:</b> <code>{message.from_user.id}</code>  
<b>Telefon raqam:</b> <i>+{phone_number}</i>  
<b>Ism Sharifi:</b> <u>{full_name}</u>  
<b>Avtomobil:</b> {car_model}  
<b>Mashina raqami:</b> <b>{car_number}</b>  

<b>Permission date:</b> <i>{permission_date}</i> gacha

🔔 <b>Adminlar tomonidan ko'rib chiqiladi!</b>
    """
    await message.answer(message_txt, parse_mode='HTML')
    await message.bot.send_message(
        chat_id=5647453083,
        text=message_txt,
        parse_mode="HTML",
        reply_markup=inline.admin_done_inline_keyboard.as_markup()
    )

#  =========================== callback query =============================

@driver_router.callback_query()
async def driver_callback_handler(query: CallbackQuery) -> None:
    data = query.data
    if data == 'accept':
        print(query.message.text)
        print(True)
        # order=Order.get()
