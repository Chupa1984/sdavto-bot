from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import SERVICES, FAQ

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="🛠 Услуги и цены", callback_data="menu_services")],
        [InlineKeyboardButton(text="🔧 Диагностика по симптомам", callback_data="menu_diagnostics")],
        [InlineKeyboardButton(text="📅 Запись", callback_data="menu_booking")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="menu_contacts")],
        [InlineKeyboardButton(text="❓ Частые вопросы", callback_data="menu_faq")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def services_menu():
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"service_{name}")] for name in SERVICES]
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def faq_menu():
    buttons = [[InlineKeyboardButton(text=q, callback_data=f"faq_{q}")] for q in FAQ]
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def booking_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="booking_confirm")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="back_main")]
    ])
