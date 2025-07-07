from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChatAdministrators

# ...

# ID чата, для админов которого устанавливаем команды
ADMIN_CHAT_ID = -1001234567890


async def set_admin_commands_for_chat(bot: Bot):
    commands = [
        BotCommand(command="ban", description="Забанить пользователя"),
        BotCommand(command="unban", description="Разбанить пользователя"),
    ]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeChatAdministrators(chat_id=ADMIN_CHAT_ID),
    )
