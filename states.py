from aiogram.fsm.state import State, StatesGroup

class Diagnostics(StatesGroup):
    brand = State()
    year = State()
    symptom = State()
    confirm = State()

class Booking(StatesGroup):
    name = State()
    phone = State()
    time = State()
    confirm = State()
