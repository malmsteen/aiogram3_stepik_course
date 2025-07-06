import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

print(__name__)

logging.basicConfig(
    level=logging.getLevelName(level="DEBUG"),
    format="[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
# BOT_TOKEN = 'BOT TOKEN HERE'
BOT_TOKEN = '5424991242:AAF3u0ik4Lizb99WJqBe0gc5ntdsFwa3s8I'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()

# Создаем первый список с кнопками
buttons_1 = [KeyboardButton(text=f'Кнопка {i + 1}') for i in range(8)]

# Распаковываем список с кнопками методом add
kb_builder.add(*buttons_1)

# Явно сообщаем билдеру сколько хотим видеть кнопок в 1-м и 2-м рядах
kb_builder.adjust(1, 3)


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Вот такая получается клавиатура',
        reply_markup=kb_builder.as_markup(resize_keyboard=True)
    )


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Вот такая получается клавиатура',
        reply_markup=kb_builder.as_markup(resize_keyboard=True)
    )

# # Создаем список списков с кнопками
# keyboard = [KeyboardButton(text=str(i)) for i in range(1, 200)]

# # Инициализируем билдер
# builder = ReplyKeyboardBuilder()


# builder.max_width = 15
# builder.add(*keyboard)


# # Создаем объект клавиатуры, добавляя в него кнопки
# my_keyboard: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)

# # my_keyboard = ReplyKeyboardMarkup(keyboard=[keyboard])


# # Этот хэндлер будет срабатывать на команду "/start"
# @dp.message(CommandStart())
# async def process_start_command(message: Message):
#     print('Какого хуя???')
#     await message.answer(
#         text='Экспериментируем с обычными кнопками',
#         reply_markup=my_keyboard
#     )


if __name__ == '__main__':
    dp.run_polling(bot)
