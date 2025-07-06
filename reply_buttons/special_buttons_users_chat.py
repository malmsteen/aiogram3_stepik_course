import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
    KeyboardButtonRequestUsers,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()
# Создаем кнопки
request_user_btn = KeyboardButton(
    text="Выбрать пользователя",
    request_user=KeyboardButtonRequestUser(
        request_id=42,
        user_is_premium=False
    )
)
request_users_btn = KeyboardButton(
    text="Выбрать пользователей",
    request_users=KeyboardButtonRequestUsers(
        request_id=77,
        user_is_premium=False,
        max_quantity=3
    )
)
request_chat_btn = KeyboardButton(
    text="Выбрать чат",
    request_chat=KeyboardButtonRequestChat(
        request_id=1408,
        chat_is_channel=False,
        chat_is_forum=False
    )
)
# Добавляем кнопки в билдер
kb_builder.row(request_user_btn, request_users_btn, request_chat_btn, width=1)
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


# Этот хэндлер будет срабатывать на выбор пользователя из списка
@dp.message(F.user_shared)
async def process_user_shared(message: Message):
    print(message.model_dump_json(indent=4, exclude_none=True))


# Этот хэндлер будет срабатывать на выбор пользователей из списка
@dp.message(F.users_shared)
async def process_users_shared(message: Message):
    print(message.model_dump_json(indent=4, exclude_none=True))


# Этот хэндлер будет срабатывать на выбор чата из списка
@dp.message(F.chat_shared)
async def process_chat_shared(message: Message):
    print(message.model_dump_json(indent=4, exclude_none=True))


if __name__ == '__main__':
    dp.run_polling(bot)