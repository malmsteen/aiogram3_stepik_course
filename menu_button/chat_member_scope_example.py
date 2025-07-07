from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChatMember

# ...

# ID чата и пользователя
CHAT_ID = 123456789  # Может быть ID группы или личного чата с ботом
USER_ID = 987654321  # ID того самого пользователя


async def set_personal_commands(bot: Bot):
    commands = [
        BotCommand(command="godmode", description="Режим бога"),
        BotCommand(command="broadcast", description="Сделать рассылку"),
    ]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeChatMember(chat_id=CHAT_ID, user_id=USER_ID),
    )
