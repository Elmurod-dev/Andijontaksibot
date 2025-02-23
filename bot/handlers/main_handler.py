from aiogram import html, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.buttons import inline
from bot.buttons.reply import contact_btn, generate_btn
from bot.state import OrderState, OrderPochtaState
from db.models import User, Order, Driver, OrderMessage
import re
import asyncio

main_router = Router()


@main_router.message(F.text == "❌ bekor qilish")
@main_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    data = ("👤 Yo'lovchi", "🚖 Haydovchi")
    desigin = (2,)
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=generate_btn(data, desigin))


@main_router.message(F.text == "👤 Yo'lovchi")
async def role_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Assalomu alaykum!\nBizning botimizdan foydalanganingiz uchun katta rahmat.Alloh yo‘lingizni ochiq qilsin. Safaringiz bexatar bo‘lsin. Oq yo‘l!")
    await state.set_state(OrderState.phone_number)
    await message.answer(f"Iltimos Telefon raqamingizni yuboring", reply_markup=contact_btn())


@main_router.message(OrderState.phone_number, lambda message: message.contact is not None)
async def contact_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(phone_number=message.contact.phone_number)
    await state.set_state(OrderState.name)
    await message.answer("Ismingiz?")


@main_router.message(OrderState.name)
async def name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(OrderState.order_type)
    data = ["O‘zim ketaman", "Pochta yuboraman", "❌ bekor qilish"]
    design = (2,)
    await message.answer("Tanlang: ", reply_markup=generate_btn(data, design))


@main_router.message(OrderState.order_type, F.text == "O‘zim ketaman")
async def name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(order_type=message.text)
    await state.set_state(OrderState.count)
    data = ["1", "2", "3", "4", "❌ bekor qilish"]
    design = (2,)
    await message.answer("Necha kishi ketmoqchisiz?", reply_markup=generate_btn(data, design))


@main_router.message(OrderState.count, F.text.in_(["1", "2", "3", "4"]))
async def name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(count=message.text)
    await state.set_state(OrderState.jinsi)
    data = ["👱🏻‍♂️ Erkak", "👩🏻 Ayol", "❌ bekor qilish"]
    design = (2,)
    await message.answer("Jinsingiz?", reply_markup=generate_btn(data, design))


@main_router.message(OrderState.jinsi, F.text.in_(["👱🏻‍♂️ Erkak", "👩🏻 Ayol"]))
async def name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(jinsi=message.text)
    await state.set_state(OrderState.manzil)
    data = ("Andijon -> Toshkent", "Toshkent -> Andijon", "❌ bekor qilish")
    design = (2,)
    await message.answer("Qayerdan qayerga borasiz?", reply_markup=generate_btn(data, design))


@main_router.message(OrderState.manzil, F.text.in_(["Andijon -> Toshkent", "Toshkent -> Andijon"]))
async def name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(manzil=message.text)
    await state.set_state(OrderState.yuk)
    data = ("yuk yuq", "❌ bekor qilish")
    design = (1,)
    await message.answer("Yuk Bormi? Agar bulsa rasmini yuboring", reply_markup=generate_btn(data, design))


@main_router.message(OrderState.yuk)
async def name_handler(message: Message, state: FSMContext) -> None:
    if message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(yuk=file_id)
        await state.set_state(OrderState.sana)
        await message.answer("Ketish sanasini yuboring?\nquyidagi shakilda(sana,oy) Masalan: 12,02", reply_markup=None)
    elif message.text == "yuk yuq":
        await state.update_data(yuk=message.text)
        await state.set_state(OrderState.sana)
        await message.answer("Ketish sanasini yuboring?\nquyidagi shakilda(sana,oy) Masalan: 12,02", reply_markup=None)


@main_router.message(OrderState.sana)
async def name_handler(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    pattern = r"^\d{1,2},\d{1,2}$"
    if not re.match(pattern, text):
        await message.answer("❌ Sana noto‘g‘ri formatda. To‘g‘ri shakl: 12,02")
        await state.set_state(OrderState.sana)
        return
    day, month = map(int, text.split(","))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        await message.answer("❌ Sana noto‘g‘ri. Oy 1-12 va kun 1-31 oralig‘ida bo‘lishi kerak.")
        await state.set_state(OrderState.sana)
        return
    await state.update_data(sana=text)
    data = await state.get_data()
    phone_number = data["phone_number"]
    name = data["name"]
    jinsi = data["jinsi"]
    order_type = data["order_type"]
    manzil = data["manzil"]
    yuk = data["yuk"]
    count = int(data["count"])
    sana = data["sana"]
    user = await User.get(id_=message.from_user.id)
    if not user:
        await User.create(id=message.from_user.id, full_name=message.from_user.full_name, jinsi=jinsi, name=name,
                          phone_number=phone_number)
    elif user:
        await User.update(id_=message.from_user.id, name=name, phone_number=phone_number)
    order = await Order.create(passenger_id=message.from_user.id, dropoff_location=manzil, order_type=order_type,
                               yuk=yuk, count=count, sana=sana)
    await state.clear()
    await message.answer("Tez orada siz bilan bog'lanamiz😊\nKetish soatini haydovchi bilan kelishib olasiz.")
    drivers = await Driver.get_all()
    await send_order_to_drivers(drivers, name, order.id, message, address=manzil, order_type=order_type, date=sana,
                                user_id=user.id)


@main_router.message(F.text == "Pochta yuboraman")
async def order_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(order_type=message.text)
    await state.set_state(OrderPochtaState.name)
    await message.answer("Pochta Yuboruvchi ismi?")


@main_router.message(OrderPochtaState.name)
async def order_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(OrderPochtaState.phone_number)
    await message.answer("Pochta yuboruvchi Telefon raqamini yuboring: Misol (938772345)")


@main_router.message(OrderPochtaState.phone_number)
async def order_handler(message: Message, state: FSMContext) -> None:
    phone_number = message.text.strip()
    if re.match(r"^\d{9}$", phone_number):
        await state.update_data(phone_number=phone_number)
        await state.set_state(OrderPochtaState.manzil)
        data = ("Andijon -> Toshkent", "Toshkent -> Andijon", "❌ bekor qilish")
        design = (2,)
        await message.answer("Qayerdan qayerga Pochta yuborasiz?", reply_markup=generate_btn(data, design))
    else:
        await state.set_state(OrderPochtaState.phone_number)
        await message.answer("Notug'ri format kiritildi\nTo'g'ri format (938772345) kabi bulishi kerak")


@main_router.message(OrderPochtaState.manzil, F.text.in_(["Andijon -> Toshkent", "Toshkent -> Andijon"]))
async def order_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(manzil=message.text)
    await state.set_state(OrderPochtaState.yuk)
    await message.answer("Yuk Rasmini Yuboring", reply_markup=None)


@main_router.message(OrderPochtaState.yuk)
async def order_handler(message: Message, state: FSMContext) -> None:
    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(yuk=photo_id)
        await state.set_state(OrderPochtaState.sana)
        await message.answer("Ketish sanasini yuboring?\nquyidagi shakilda(sana,oy) Masalan: 12,02", reply_markup=None)
    else:
        await state.set_state(OrderPochtaState.yuk)
        await message.answer("Iltimos yuk rasmini yuboring")


async def send_order_to_drivers(drivers, user, order_id, message, address, order_type, date, user_id):
    tasks = []
    months = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr",
              "Dekabr"]
    day, month = date.split(",")
    month = months[int(month) - 1]

    caption = f"""🟢 Yangi buyurtma
<b>{address}</b>
<b>{user}</b>
<i>{order_type}</i>
<code>{day}-{month}</code>
<b>#{order_id}</b>

Batafsil ma'lumot uchun tugmani bosing
    """

    photo_id = 'AgACAgIAAxkBAAIDkWeomc4R__E7PiOOEcTv0mWKMMgSAALg5zEbUBtASVphMHWCgjbzAQADAgADeQADNgQ' \
        if address.split()[0] == 'Andijon' else \
        'AgACAgIAAxkBAAIDjmeomauPtqZELcxQ8S_dPKTdnaJKAALf5zEbUBtASXjJaqwmUSejAQADAgADeQADNgQ'

    for driver in drivers:
        if driver.is_active:
            tasks.append(
                message.bot.send_photo(
                    chat_id=driver.id,
                    photo=photo_id,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=inline.driver_accept_inline_keyboard.as_markup()
                )
            )

    await asyncio.gather(*tasks)



    # tasks.append(
    #     OrderMessage.create( order_id=order_id, user_id=user_id,message_id=str(msg.message_id))
    # )

    await asyncio.gather(*tasks)


@main_router.message(OrderPochtaState.sana)
async def name_handler(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    pattern = r"^\d{1,2},\d{1,2}$"
    if not re.match(pattern, text):
        await message.answer("❌ Sana noto‘g‘ri formatda. To‘g‘ri shakl: 12,02")
        await state.set_state(OrderState.sana)
        return
    day, month = map(int, text.split(","))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        await message.answer("❌ Sana noto‘g‘ri. Oy 1-12 va kun 1-31 oralig‘ida bo‘lishi kerak.")
        await state.set_state(OrderState.sana)
        return
    await state.update_data(sana=text)
    data = await state.get_data()
    phone_number = "+998" + data["phone_number"]
    name = data["name"]
    order_type = data["order_type"]
    manzil = data["manzil"]
    yuk = data["yuk"]
    sana = data["sana"]
    user = await User.get(id_=message.from_user.id)
    if not user:
        await User.create(id=message.from_user.id, full_name=message.from_user.full_name, name=name,
                          phone_number=phone_number)
    elif user:
        await User.update(id_=message.from_user.id, name=name, phone_number=phone_number)
    order = await Order.create(passenger_id=message.from_user.id, dropoff_location=manzil, order_type=order_type,
                               yuk=yuk, sana=sana)
    await state.clear()
    await message.answer("Tez orada siz bilan bog'lanamiz😊\nKetish soatini haydovchi bilan kelishib olasiz.")
    drivers = await Driver.get_all()
    await send_order_to_drivers(drivers, name, order.id, message, address=manzil, order_type=order_type, date=sana,
                                user_id=user.id)


@main_router.message(F.photo)
async def send_image_code(message: Message):
    (await message.reply(text=f"Photo ID: {message.photo[-1].file_id}"))
