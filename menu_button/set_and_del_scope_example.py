import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    Message,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Команды для скоупа по умолчанию
DEFAULT_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="help", description="Справка"),
]

# Команды для персонального меню
PERSONAL_COMMANDS = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="profile", description="Мой профиль"),
    BotCommand(command="settings", description="Настройки"),
    BotCommand(command="delpersonal", description="❌ Удалить персональное меню"),
]

router = Router()


# Этот хэндлер срабатывает на команду /start и устанавливает персональные
# команды для пользователя, который её отправил
@router.message(CommandStart())
async def process_start_command(message: Message, bot: Bot):
    # Создаем скоуп для конкретного чата
    scope = BotCommandScopeChat(chat_id=message.chat.id)

    # Устанавливаем персональные команды
    await bot.set_my_commands(commands=PERSONAL_COMMANDS, scope=scope)

    await message.answer(
        "Вам установлены персональные команды!\n"
        "Нажмите на кнопку 'Menu' или введите '/', чтобы увидеть их.\n"
        "Чтобы вернуть стандартные команды, используйте /delpersonal"
    )


# Этот хэндлер срабатывает на команду /delpersonal и удаляет
# персональные команды для пользователя
@router.message(Command("delpersonal"))
async def process_del_personal_command(message: Message, bot: Bot):
    # Создаем тот же скоуп, что и при установке
    scope = BotCommandScopeChat(chat_id=message.chat.id)

    # Удаляем команды для этого скоупа
    await bot.delete_my_commands(scope)

    await message.answer(
        "Персональные команды удалены. Теперь вы снова видите команды по умолчанию."
    )


# Эта функция сработает при запуске скрипта и установит дефолтный скоуп команд
async def on_startup(bot: Bot):
    logging.info("Starting bot... Setting up default commands.")
    await bot.set_my_commands(DEFAULT_COMMANDS, BotCommandScopeDefault())


# Эта функция сработает при остановке бота и удалит дефолтные команды
async def on_shutdown(bot: Bot):
    logging.info("Bot stopping... Removing the default commands.")
    await bot.delete_my_commands(BotCommandScopeDefault())


async def main():
    if not BOT_TOKEN:
        logging.error(
            "The bot token was not found. Set the BOT_TOKEN environment variable."
        )
        return

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
               "%(lineno)d - %(name)s - %(message)s",
    )

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем функции на события запуска и остановки бота
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Подключаем роутер
    dp.include_router(router)

    # Запускаем поллинг
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
