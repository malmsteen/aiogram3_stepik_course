from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

# ...


async def set_private_chat_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Показать меню"),
        BotCommand(command="profile", description="Мой профиль"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
