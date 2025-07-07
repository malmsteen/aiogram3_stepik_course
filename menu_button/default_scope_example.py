from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

# ...


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="help", description="Посмотреть справку"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
