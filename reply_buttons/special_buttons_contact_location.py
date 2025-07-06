import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()
# Создаем кнопки
contact_btn = KeyboardButton(
    text='Отправить телефон',
    request_contact=True
)
geo_btn = KeyboardButton(
    text='Отправить геолокацию',
    request_location=True
)
# Добавляем кнопки в билдер
kb_builder.row(contact_btn, geo_btn, width=1)
# Создаем объект клавиатуры
keyboard: ReplyKeyboardMarkup = kb_builder.as_markup(
    resize_keyboard=True
)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Экспериментируем со специальными кнопками',
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на отправку контакта
@dp.message(F.contact)
async def process_contact(message: Message):
    await message.answer(
        text=f'Ваш телефон: {message.contact.phone_number}',
    )
    print(message.model_dump_json(indent=4, exclude_none=True))


# Этот хэндлер будет срабатывать на отправку локации
@dp.message(F.location)
async def process_location(message: Message):
    await message.answer(
        text=f'Ваши координаты: {message.location.latitude, message.location.longitude}',
    )
    print(message.model_dump_json(indent=4, exclude_none=True))


if __name__ == '__main__':
    dp.run_polling(bot)
