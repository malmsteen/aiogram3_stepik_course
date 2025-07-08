import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Создаем объекты бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Создаем объекты инлайн-кнопок
button_1 = InlineKeyboardButton(
    text="КНОПКА 1", callback_data="button_1_click"
)
button_2 = InlineKeyboardButton(
    text="КНОПКА 2", callback_data="button_2_click"
)

# Создаем объект инлайн-клавиатуры
keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])


# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру с инлайн-кнопками
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text="Это инлайн-кнопки. Нажми на любую!", reply_markup=keyboard
    )


# # Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# # с data `button_1_click` или `button_2_click`
# @dp.callback_query(F.data.in_(["button_1_click", "button_2_click"]))
# async def process_buttons_click(callback: CallbackQuery):
#     await callback.answer()


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data `button_1_click`
@dp.callback_query(F.data == 'button_1_click')
async def process_button_1_click(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Была нажата КНОПКА 1',
        reply_markup=callback.message.reply_markup
    )


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data `button_2_click`
@dp.callback_query(F.data == 'button_2_click')
async def process_button_2_click(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Была нажата КНОПКА 2',
        reply_markup=callback.message.reply_markup
    )


if __name__ == "__main__":
    dp.run_polling(bot)
