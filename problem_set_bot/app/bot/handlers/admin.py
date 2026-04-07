import logging

from contextlib import suppress
from aiogram import Router
from aiogram import Bot, F
from aiogram.types import ContentType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from app.bot.enums.roles import UserRole
from app.bot.filters.filters import UserRoleFilter
from app.infrastructure.database.db import (
    change_user_banned_status_by_id,
    change_user_banned_status_by_username,
    get_statistics,
    get_user_banned_status_by_id,
    get_user_banned_status_by_username,
    change_user_alive_status,
    broadcast_log,
    get_all_alive_users,
)
import asyncio
from psycopg import AsyncConnection
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from app.bot.states.states import BroadcastState

logger = logging.getLogger(__name__)

admin_router = Router()

admin_router.message.filter(UserRoleFilter(UserRole.ADMIN))


# Этот хэндлер будет срабатывать на команду /help для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command("help"))
async def process_admin_help_command(message: Message, i18n: dict):
    await message.answer(text=i18n.get("/help_admin"))


# Этот хэндлер будет срабатывать на команду /statistics для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command("statistics"))
async def process_admin_statistics_command(
    message: Message, conn: AsyncConnection, i18n: dict[str, str]
):
    statistics = await get_statistics(conn)
    await message.answer(
        text=i18n.get("statistics").format(
            "\n".join(
                f"{i}. <b>{stat[0]}</b>: {stat[1]}"
                for i, stat in enumerate(statistics, 1)
            )
        )
    )


# Этот хэндлер будет срабатывать на команду /ban для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command("ban"))
async def process_ban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str],
) -> None:
    args = command.args

    if not args:
        await message.reply(i18n.get("empty_ban_answer"))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith("@"):
        banned_status = await get_user_banned_status_by_username(
            conn, username=arg_user[1:]
        )
    else:
        await message.reply(text=i18n.get("incorrect_ban_arg"))
        return

    if banned_status is None:
        await message.reply(i18n.get("no_user"))
    elif banned_status:
        await message.reply(i18n.get("already_banned"))
    else:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(
                conn, user_id=int(arg_user), banned=True
            )
        else:
            await change_user_banned_status_by_username(
                conn, username=arg_user[1:], banned=True
            )
        await message.reply(text=i18n.get("successfully_banned"))


# Этот хэндлер будет срабатывать на команду /unban для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command("unban"))
async def process_unban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str],
) -> None:
    args = command.args

    if not args:
        await message.reply(i18n.get("empty_unban_answer"))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith("@"):
        banned_status = await get_user_banned_status_by_username(
            conn, username=arg_user[1:]
        )
    else:
        await message.reply(text=i18n.get("incorrect_unban_arg"))
        return

    if banned_status is None:
        await message.reply(i18n.get("no_user"))
    elif banned_status:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(
                conn, user_id=int(arg_user), banned=False
            )
        else:
            await change_user_banned_status_by_username(
                conn, username=arg_user[1:], banned=False
            )
        await message.reply(text=i18n.get("successfully_unbanned"))
    else:
        await message.reply(i18n.get("not_banned"))


test_uids = [7400223163, 1400239171, 8704055030]


@admin_router.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext, i18n: dict):
    """Вход в режим рассылки."""
    await state.set_state(BroadcastState.waiting_for_content)
    await message.answer(i18n.get("broadcast_active"))


@admin_router.message(Command("cancel"), BroadcastState.waiting_for_content)
async def cancel_broadcast(message: Message, state: FSMContext, i18n: dict):
    await state.clear()
    await message.answer(i18n.get("cancel_broadcast"))


@admin_router.message(BroadcastState.waiting_for_content)
async def process_broadcast_content(
    message: Message,
    bot: Bot,
    state: FSMContext,
    conn: AsyncConnection,
    i18n: dict,
):
    status_msg = await message.answer(i18n.get("broadcasting"))

    user_ids = await get_all_alive_users(conn)

    if not user_ids:
        await status_msg.edit_text(i18n.get("no_alive"))
        await state.clear()
        return

    success = 0
    for uid in test_uids:
        try:
            if message.content_type in (
                ContentType.PHOTO,
                ContentType.VIDEO,
                ContentType.DOCUMENT,
                ContentType.AUDIO,
            ):
                await bot.copy_message(
                    chat_id=uid,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
            else:
                await bot.send_message(chat_id=uid, text=message.text)

            await broadcast_log(conn, uid)

            success += 1
        except TelegramForbiddenError:
            await change_user_alive_status(conn, is_alive=False, user_id=uid)

        except TelegramBadRequest as e:
            if "user not found" in str(e) or "chat not found" in str(e):
                await change_user_alive_status(conn, is_alive=False, user_id=uid)
            else:
                logger.error(f"Ошибка при отправке {uid}: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке {uid}: {e}")
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        i18n.get("broadcast_completed").format(success, len(user_ids))
    )
    await state.clear()
