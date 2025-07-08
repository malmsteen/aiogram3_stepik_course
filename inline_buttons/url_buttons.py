import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

# Создаем объекты бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Создаем объекты инлайн-кнопок
url_button_1 = InlineKeyboardButton(
    text='Курс "Телеграм-боты на Python и AIOgram"', url="https://stepik.org/120924"
)
url_button_2 = InlineKeyboardButton(
    text="Продвинутый курс по ботам", url="https://stepik.org/course/153850/"
)
url_button_3 = InlineKeyboardButton(
    text="Документация Telegram Bot API", url="https://core.telegram.org/bots/api"
)

# Создаем объект инлайн-клавиатуры
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[url_button_1], [url_button_2], [url_button_3]]
)


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру c url-кнопками
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Это инлайн-кнопки с параметром "url"', reply_markup=keyboard
    )


# Создаем объекты инлайн-кнопок
group_name = "aiogram_stepik_course"
url_button_3 = InlineKeyboardButton(
    text='Группа "Телеграм-боты на AIOgram"', url=f"tg://resolve?domain={group_name}"
)

user_id = 173901673
url_button_4 = InlineKeyboardButton(
    text="Автор курса на Степике по телеграм-ботам", url=f"tg://user?id={user_id}"
)

channel_name = "toBeAnMLspecialist"
url_button_5 = InlineKeyboardButton(
    text='Канал "Стать специалистом по машинному обучению"',
    url=f"https://t.me/{channel_name}",
)

# Создаем объект инлайн-клавиатуры
keyboard_2 = InlineKeyboardMarkup(
    inline_keyboard=[[url_button_3], [url_button_4], [url_button_5]]
)


# Этот хэндлер будет срабатывать на команду "/other"
# и отправлять в чат клавиатуру c url-кнопками
@dp.message(Command(commands="other"))
async def process_other_command(message: Message):
    await message.answer(
        text='Это инлайн-кнопки с параметром "url"', reply_markup=keyboard_2
    )


if __name__ == "__main__":
    dp.run_polling(bot)
