import asyncio
import re
from datetime import datetime, timedelta
from aiogram import Router, F, Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import null

from bot.buttons import reply, inline
from bot.buttons.inline import ok, cancel_order_inline_keyboard
from bot.handlers.main_handler import send_order_to_drivers

from bot.state import DriverRegisterState
from db.models import User, Driver, Order, OrderMessage

driver_router = Router()


# ============ driver send request to register ===========

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
    permission_date = (datetime.now() + timedelta(days=30)).date()

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
async def driver_accept_handler(query: CallbackQuery):
    if query.data == 'accept':
        # await query.answer("✅ Buyurtma qabul qilindi!", show_alert=True)
        id = query.message.caption.split('\n')[5].lstrip('#')
        order = await Order.get(id_=int(id))
        user = await User.get(id_=order.passenger_id)
        user_data = f"""Ism Sharifi: {user.full_name}\n
Telefon raqam: {user.phone_number}\n
Jinsi: {user.jinsi}\n
Yuk: {order.yuk}\n
Order type: {order.order_type}\n
Sana:{order.sana}\n
            """
        if not order.driver_id:
            await query.answer(user_data, show_alert=True)

            driver = await Driver.get(id_=int(query.message.chat.id))
            print(query.message.chat.id)
            if driver:
                driver_phone = driver.phone_number
                order_id = order.id
                visit_count = order.driver_visit_count
                await order.update(id_=order_id, driver_visit_count=visit_count + 1)
                user_data = f"""Siz <b>{driver_phone}</b> raqamidagi haydovchi bilan bog'landingizmi?
Agar bog'lanib, kelishuvga erishgan bo'lsangiz, <b>"OK"</b> tugmasini bosing.
Shunda e'loningiz barcha haydovchilardan o'chirib tashlanadi.

👁Qiziqishlar soni: <b>{order.driver_visit_count}</b>ta
<b>#{order_id} {driver.id}</b>
                    """

                await query.message.bot.send_message(chat_id=user.id, text=user_data, parse_mode='HTML',
                                                     reply_markup=ok.as_markup())

        else:
            await query.answer("allaqachon haydovchi biriktirilgan", show_alert=True)

    if query.data == 'done':
        print(True)
        message_text = query.message.text
        data = await parse_driver_info(message_text)
        await Driver.create(**data)
        message = """
                   <b>🟢 Haydovchi muvafaqqiyatli ro'yxatga olindi!</b>
                   """
        await query.message.answer(message, parse_mode='HTML')
    if query.data == 'ok':
        order_id = query.message.text.split('\n')[5].split()[0].lstrip('#').strip()
        driver_id = query.message.text.split('\n')[5].split()[1]
        drivers = await Driver.get_all()
        # order=await OrderMessage.get(id_=int(order_id))
        # message_ids = []
        order = await Order.get(int(order_id))
        # ordermessages = await OrderMessage.get_all()
        # if ordermessages:
        #     for i in ordermessages:
        #         if int(i.order_id) == int(order_id):
        #             message_ids.append(i.message_id)

        if order.driver_id:
            driver = await Driver.get(id_=int(driver_id))
            text = f"""Siz allaqachon {driver.full_name} ismli haydovchiga biriktirilgansiz ✅
📞 Telefon: +{driver.phone_number}  
🚗 Mashina modeli: {driver.car_model}  
🔢 Davlat raqami: {driver.car_number}

<b>#{order_id} #{driver.id}</b>
                        """

            await query.bot.edit_message_text(
                parse_mode='HTML',
                text=text,
                chat_id=query.message.chat.id,  # Chat ID-ni qo‘shish shart
                message_id=query.message.message_id,  # Message ID kerak!
                reply_markup=cancel_order_inline_keyboard.as_markup()
            )

        else:
            await Order.update(id_=int(order_id), driver_id=int(driver_id))
            # await delete_order_messages(drivers, query.message, message_ids)
            driver = await Driver.get(id_=int(driver_id))
            text = f"""<b>Siz {driver.full_name} ismli haydovchiga biriktirildingiz ✅</b>
Shuningdek, e'loningiz barcha haydovchilardan o‘chirildi.
📞 <b>Telefon:</b> +{driver.phone_number}  
🚗 <b>Mashina modeli:</b> {driver.car_model}  
🔢 <b>Davlat raqami:</b> {driver.car_number}
            """

            await query.message.edit_text(text, parse_mode="HTML")

            await query.message.bot.send_message(
                chat_id=driver_id,
                text="Mijoz sizning taklifingizni qabul qildi! ✅",
                parse_mode='HTML'
            )
    if query.data == 'cancel':
        message_text_split = query.message.text.split('\n')
        if len(message_text_split) == 6:
            order_id = message_text_split[5].split()[0].lstrip('#').strip()
            driver_id = message_text_split[5].split()[1].lstrip('#').strip()
            drivers = await Driver.get_all()
            order = await Order.get(id_=int(order_id))
            if order.driver_id:
                await Order.update(int(order_id), driver_id=None)
                await send_order_to_drivers(drivers, 'sakd', order.id, query.message, order.dropoff_location,
                                            order.order_type, order.sana, order.passenger_id)

                text = """
                ✅<b>Haydovchi</b> bekor qilindi va sizning <b>buyurtmangiz</b> boshqa <i>haydovchilarga</i> yuborildi
                """

                await query.message.answer(text, parse_mode="HTML")






# async def delete_order_messages(drivers, message, message_ids):
#     tasks = []
#
#     for i in range(len(message_ids)):
#         try:
#             task = message.bot.delete_message(chat_id=drivers[i].id, message_id=int(message_ids[i]))
#             tasks.append(task)
#         except Exception as e:
#             print(f"Xatolik yuz berdi: {e}")
#             continue
#
#     await asyncio.gather(*tasks)
