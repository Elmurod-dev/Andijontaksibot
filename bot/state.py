from aiogram.fsm.state import StatesGroup, State


class OrderState(StatesGroup):
    phone_number = State()
    name = State()
    jinsi = State()
    order_type = State()
    manzil = State()
    yuk = State()
    count = State()
    sana = State()

class OrderPochtaState(StatesGroup):
    sana = State()
    manzil = State()
    yuk = State()
    phone_number = State()
    name = State()
    order_type = State()

class DriverRegisterState(StatesGroup):
    phone_number = State()
    full_name = State()
    car_model=State()
    car_number = State()


