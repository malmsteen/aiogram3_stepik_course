from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

# ...


async def set_multilang_commands(bot: Bot):
    # Команды для русскоязычных пользователей
    ru_commands = [
        BotCommand(command="start", description="Запуск"),
        BotCommand(command="help", description="Помощь"),
    ]
    # Команды для англоязычных пользователей
    en_commands = [
        BotCommand(command="start", description="Launch"),
        BotCommand(command="help", description="Help"),
    ]

    scope = BotCommandScopeAllPrivateChats()

    await bot.set_my_commands(commands=ru_commands, scope=scope, language_code="ru")
    await bot.set_my_commands(commands=en_commands, scope=scope, language_code="en")
