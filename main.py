import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_CHAT_ID
from keyboards import *
from states import Diagnostics, Booking
from texts import *
from ai_service import ask_chatgpt
from db import init_db, save_booking
from keep_alive import keep_alive

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())

@dp.callback_query(F.data == "menu_services")
async def show_services(call: CallbackQuery):
    await call.message.edit_text("Выберите категорию услуг:", reply_markup=services_menu())

@dp.callback_query(F.data.startswith("service_"))
async def service_detail(call: CallbackQuery):
    service_name = call.data.split("_", 1)[1]
    text = SERVICES.get(service_name, "Описание не найдено")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться на диагностику", callback_data="booking_start")],
        [InlineKeyboardButton(text="Назад к услугам", callback_data="menu_services")]
    ])
    await call.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "menu_diagnostics")
async def start_diagnostics(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Начнём диагностику. Укажите марку автомобиля:")
    await state.set_state(Diagnostics.brand)

@dp.message(Diagnostics.brand)
async def diag_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Год выпуска?")
    await state.set_state(Diagnostics.year)

@dp.message(Diagnostics.year)
async def diag_year(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите год числом (например 2012)")
        return
    await state.update_data(year=message.text)
    await message.answer("Опишите симптомы: когда появляется неисправность? (на холодную, при повороте, на скорости и т.д.)")
    await state.set_state(Diagnostics.symptom)

@dp.message(Diagnostics.symptom)
async def diag_symptom(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(symptom=message.text)
    prompt = f"Марка: {data['brand']}, год: {data['year']}. Симптомы: {message.text}. Дай предположительные причины и предложи запись."
    answer = await ask_chatgpt(prompt)
    await message.answer(answer, reply_markup=booking_confirm_keyboard())
    await state.clear()

@dp.callback_query(F.data == "menu_booking")
@dp.callback_query(F.data == "booking_start")
async def start_booking(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Давайте запишем вас на сервис. Как вас зовут?")
    await state.set_state(Booking.name)

@dp.message(Booking.name)
async def booking_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Ваш номер телефона:")
    await state.set_state(Booking.phone)

@dp.message(Booking.phone)
async def booking_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Желаемая дата/время? (например, завтра в 10:00)")
    await state.set_state(Booking.time)

@dp.message(Booking.time)
async def booking_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    data = await state.get_data()
    summary = f"Имя: {data['name']}\nТелефон: {data['phone']}\nВремя: {data['time']}"
    await message.answer(f"Проверьте данные:\n{summary}", reply_markup=booking_confirm_keyboard())
    await state.set_state(Booking.confirm)

@dp.callback_query(F.data == "booking_confirm", Booking.confirm)
async def confirm_booking(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    save_booking(call.from_user.id, data['name'], data['phone'], data['time'])
    await bot.send_message(ADMIN_CHAT_ID,
        f"Новая запись!\nИмя: {data['name']}\nТел: {data['phone']}\nВремя: {data['time']}")
    await call.message.edit_text("✅ Вы записаны! Мы свяжемся с вами в ближайшее время.")
    await state.clear()

@dp.callback_query(F.data == "menu_contacts")
async def contacts(call: CallbackQuery):
    await call.message.edit_text(CONTACTS_TEXT, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_main")]]))

@dp.callback_query(F.data == "menu_faq")
async def faq(call: CallbackQuery):
    await call.message.edit_text("Частые вопросы:", reply_markup=faq_menu())

@dp.callback_query(F.data.startswith("faq_"))
async def faq_answer(call: CallbackQuery):
    q = call.data[4:]
    answer = FAQ.get(q, "Ответ не найден")
    await call.message.edit_text(f"<b>{q}</b>\n\n{answer}", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад к вопросам", callback_data="menu_faq")]]))

@dp.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(WELCOME_TEXT, reply_markup=main_menu())

@dp.message(F.text)
async def free_chat(message: Message):
    answer = await ask_chatgpt(message.text)
    await message.answer(answer)

async def main():
    init_db()
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
