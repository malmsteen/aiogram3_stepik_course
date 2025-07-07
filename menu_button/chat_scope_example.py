from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

# ...

# ID чата, для которого устанавливаем команды
TARGET_CHAT_ID = -1001234567890


async def set_commands_for_specific_chat(bot: Bot):
    commands = [
        BotCommand(command="vip_feature", description="Эксклюзивная функция"),
        BotCommand(command="support", description="Вызвать поддержку"),
    ]
    await bot.set_my_commands(
        commands=commands, scope=BotCommandScopeChat(chat_id=TARGET_CHAT_ID)
    )
