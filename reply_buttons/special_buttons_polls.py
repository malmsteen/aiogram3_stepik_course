import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import PollType
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    KeyboardButtonPollType,
    Message,
    PollAnswer,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Инициализируем билдер
kb_builder = ReplyKeyboardBuilder()
# Создаем кнопки
poll_quiz_btn = KeyboardButton(
    text='Создать опрос/викторину',
    request_poll=KeyboardButtonPollType()
)
poll_btn = KeyboardButton(
    text='Создать опрос',
    request_poll=KeyboardButtonPollType(type=PollType.REGULAR)
)
quiz_btn = KeyboardButton(
    text='Создать викторину',
    request_poll=KeyboardButtonPollType(type=PollType.QUIZ)
)
# Добавляем кнопки в билдер
kb_builder.row(poll_quiz_btn, poll_btn, quiz_btn,  width=1)
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


# Этот хэндлер будет срабатывать на отправку викторины
@dp.message(F.poll.type == PollType.QUIZ)
async def process_poll_quiz(message: Message):
    await message.answer_poll(
        question=message.poll.question,
        options=[opt.text for opt in message.poll.options],
        is_anonymous=True,
        type=message.poll.type,
        correct_option_id=message.poll.correct_option_id,
        explanationf=message.poll.explanation,
        explanation_entities=message.poll.explanation_entities,
        message_effect_id='5104841245755180586'
    )


# Этот хэндлер будет срабатывать на отправку опроса
@dp.message(F.poll.type == PollType.REGULAR)
async def process_poll_reqular(message: Message):
    await message.answer_poll(
        question=message.poll.question,
        options=[opt.text for opt in message.poll.options],
        is_anonymous=True,
        type=message.poll.type,
        allows_multiple_answers=message.poll.allows_multiple_answers,
        message_effect_id='5107584321108051014'
    )


# Этот хэндлер будет срабатывать на отправку опроса ответа в опросе/викторине
@dp.poll_answer()
async def process_answer_poll(poll_answer: PollAnswer):
    print(poll_answer.model_dump_json(indent=4, exclude_none=True))


if __name__ == '__main__':
    dp.run_polling(bot)
