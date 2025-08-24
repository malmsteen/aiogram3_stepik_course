import logging
from contextlib import suppress

from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, ChatMemberUpdated, Message, CallbackQuery
from app.bot.enums.roles import UserRole
from app.bot.filters.filters import IsDigitCallbackData
from app.bot.keyboards.menu_button import get_main_menu_commands
from app.bot.keyboards.keyboards import create_sections_keyboard
from app.bot.states.states import LangSG
from app.infrastructure.latex.latex import make_pdf


from app.infrastructure.database.db import (
    add_user,
    change_user_alive_status,
    get_user,
    get_user_lang,
    get_problem_texts
)
from psycopg.connection_async import AsyncConnection

logger = logging.getLogger(__name__)

# Инициализируем роутер уровня модуля
user_router = Router()


# Этот хэндлер срабатывает на команду /start
@user_router.message(CommandStart())
async def process_start_command(
    message: Message, 
    conn: AsyncConnection, 
    bot: Bot, 
    i18n: dict[str, str], 
    state: FSMContext, 
    admin_ids: list[int],
    translations: dict
):
    user_row = await get_user(conn, user_id=message.from_user.id)
    if user_row is None:
        if message.from_user.id in admin_ids:
            user_role = UserRole.ADMIN
        else:
            user_role = UserRole.USER

        await add_user(
            conn,
            user_id=message.from_user.id,
            username=message.from_user.username,
            language=message.from_user.language_code,
            role=user_role
        )
    else:
        user_role = UserRole(user_row[4])
        await change_user_alive_status(
            conn, 
            is_alive=True, 
            user_id=message.from_user.id, 
        )

    if await state.get_state() == LangSG.lang:
        data = await state.get_data()
        with suppress(TelegramBadRequest):
            msg_id = data.get("lang_settings_msg_id")
            if msg_id:
                await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=msg_id)
        user_lang = await get_user_lang(conn, user_id=message.from_user.id)
        i18n = translations.get(user_lang)
    
    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n, role=user_role),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.from_user.id
        )
    )

    await message.answer(text=i18n.get("/start"))
    await state.clear()


# Этот хэндлер срабатывает на команду /help
@user_router.message(Command(commands="help"))
async def process_help_command(message: Message, i18n: dict[str, str]):
    await message.answer(text=i18n.get("/help"))


# Этот хэндлер будет срабатывать на блокировку бота пользователем
@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated, conn: AsyncConnection):
    logger.info("User %d has blocked the bot", event.from_user.id)
    await change_user_alive_status(conn, user_id=event.from_user.id, is_alive=False)

# Этот хэндлер срабатывает на команду /sections
@user_router.message(Command(commands="sections"))
async def process_sections_command(message: Message):
    keyboard = create_sections_keyboard()
    await message.answer(
        text='Выбирете тему из списка, и документ отправится на печать',
        reply_markup=keyboard,
    )

# срабатывает на нажатие кнопки с темой
@user_router.callback_query(IsDigitCallbackData())
async def process_section_press(callback: CallbackQuery, conn: AsyncConnection, texlive):
    num = callback.data
    callback.answer()
    if int(num) >= 5:
        num = str(int(num)+1)
    problems = await get_problem_texts(conn, num) 
    await callback.message.edit_text(
        text=f"⚙️✨ Компиляция началась...",
        reply_markup=create_sections_keyboard())
    
    pdf_doc = await make_pdf(problems, texlive)    
    # await message.answer()
    await callback.message.edit_text(
        text="✅ Готово! Можете выбрать еще",
        reply_markup=create_sections_keyboard(),
        show_alert=False)
    await callback.message.answer_document(
        document=pdf_doc
        # text=num,
        # reply_markup=callback.message.reply_markup
    )
