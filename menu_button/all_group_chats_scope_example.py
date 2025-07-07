from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats

# ...


async def set_group_chat_commands(bot: Bot):
    commands = [
        BotCommand(command="rules", description="Правила чата"),
        BotCommand(command="report", description="Пожаловаться на спам"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllGroupChats())
