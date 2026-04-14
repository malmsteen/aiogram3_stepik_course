import logging
from contextlib import suppress
import os
import json
from app.bot.states.states import TaskSelectionSG

from aiogram import Bot, Router, F
from aiogram.enums import BotCommandScopeType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, ChatMemberUpdated, Message, CallbackQuery
from app.bot.enums.roles import UserRole
from app.bot.filters.filters import IsDigitCallbackData, HexIdsInMessage, FloatAns
from app.bot.keyboards.menu_button import get_main_menu_commands
from app.bot.keyboards.keyboards import (
    sections_keyboard,
    web_sections_keyboard,
    webapp_keyboard,
    answer_keyboard,
    cart_management_keyboard,
    test_keyboard,
)
from app.bot.states.states import LangSG
from app.infrastructure.latex.latex import (
    make_pdf,
    make_pdf_all,
    make_problems_pdf,
    make_variant,
)
from app.infrastructure.latex.util import remove_user_files


from app.infrastructure.database.db import (
    add_user,
    change_user_alive_status,
    get_user,
    get_user_lang,
    get_problem_texts,
    get_all_problem_types,
    get_problems_by_ids,
    get_problem_ids_by_position,
    add_problem_answer,
    get_variant,
)
from psycopg.connection_async import AsyncConnection
from redis.asyncio import Redis

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
    translations: dict,
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
            role=user_role,
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
                await bot.edit_message_reply_markup(
                    chat_id=message.from_user.id, message_id=msg_id
                )
        user_lang = await get_user_lang(conn, user_id=message.from_user.id)
        i18n = translations.get(user_lang)

    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n, role=user_role),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT, chat_id=message.from_user.id
        ),
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
async def process_sections_command(message: Message, i18n: dict[str, str]):
    keyboard = sections_keyboard()
    await message.answer(
        text=i18n.get("/sections"),
        reply_markup=keyboard,
    )


# срабатывает на нажатие кнопки с темой
@user_router.callback_query(IsDigitCallbackData())
async def process_section_press(
    callback: CallbackQuery, conn: AsyncConnection, texlive, i18n: dict[str, str]
):
    num = callback.data
    await callback.answer()

    await callback.message.edit_text(
        text=i18n.get("compiling"), reply_markup=sections_keyboard()
    )

    if int(num) <= 19:
        problems = await get_problem_texts(conn, num)
        pdf_doc = await make_pdf(problems, texlive)
    elif int(num) == 20:
        problems = await get_all_problem_types(conn)
        pdf_doc = await make_pdf_all(problems, texlive)
    else:
        problems = await get_variant(conn)
        pdf_doc = await make_variant(problems, texlive)

    # await message.answer()
    await callback.message.edit_text(
        text=i18n.get("compilation_done"),
        reply_markup=sections_keyboard(),
        show_alert=False,
    )
    await callback.message.answer_document(
        document=pdf_doc
        # text=num,
        # reply_markup=callback.message.reply_markup
    )


@user_router.callback_query(IsDigitCallbackData())
async def process_genenerate_press(
    callback: CallbackQuery, conn: AsyncConnection, texlive, i18n: dict[str, str]
):
    num = callback.data
    await callback.answer()

    await callback.message.edit_text(
        text=i18n.get("compiling"), reply_markup=sections_keyboard()
    )


@user_router.message(Command(commands="problems"), HexIdsInMessage())
async def process_problems_command(
    message: Message, source_ids: list[str], conn: AsyncConnection, i18n, texlive
):
    user_id = message.from_user.id
    if not all([len(source_id) >= 3 for source_id in source_ids]):
        await message.answer(text=i18n.get("small_id"))
        return

    problems = await get_problems_by_ids(conn, source_ids)
    logger.debug(f"Source ids: {source_ids}")
    logger.debug(f"Problems: {problems}")
    await message.answer(text=i18n.get("compiling"))
    pdf_doc = await make_problems_pdf(problems, user_id, texlive)
    await message.answer(text=i18n.get("compilation_done"))
    await message.answer_document(
        document=pdf_doc
        # text=num,
        # reply_markup=callback.message.reply_markup
    )
    await remove_user_files(user_id)


@user_router.message(Command(commands="problems"))
async def process_problems(message: Message, i18n: dict[str, str]):
    await message.answer(text=i18n.get("/problems"))


@user_router.message(Command(commands="addanswer"))
async def process_answer_adding(message: Message, i18n: dict[str, str]):
    await message.answer(
        text=i18n.get("/addanswer"),
        # reply_markup=answer_keyboard()
    )


# отсылка ответа
@user_router.message(F.photo, HexIdsInMessage())
async def process_photo_ans(
    message: Message, i18n: dict, conn: AsyncConnection, source_ids: list[str]
):
    if len(message.caption) < 3:
        await message.answer(text=i18n.get("small_id"))
        return

    await add_problem_answer(
        conn,
        source_id=source_ids[0],
        user_id=message.from_user.id,
        answer=message.photo[0].file_id,
        problem_type="long",
    )
    await message.answer(text=i18n.get("ans_been_sent"))
    logger.debug(
        f"Вы прислали фото-ответ, file_id={message.photo[0].file_id} к задаче {source_ids[0]}. Отправлен"
    )


@user_router.message(HexIdsInMessage(), FloatAns())
async def process_text_ans(
    message: Message,
    i18n: dict,
    conn: AsyncConnection,
    float_num: str,
    source_ids: list[str],
):
    if len(source_ids[0]) < 3:
        await message.answer(text=i18n.get("small_id"))
        return

    await add_problem_answer(
        conn,
        source_id=source_ids[0],
        user_id=message.from_user.id,
        answer=float_num,
        problem_type="short",
    )
    await message.answer(text=i18n.get("ans_been_sent"))
    logger.debug(f"Ваш ответ {float_num} к задаче {source_ids[0]}. Отправлен")


# @user_router.message(Command("tasks"))
# async def cmd_tasks(message: Message):
#     # Адрес, который выдала Tuna (возьмите из логов или tuna.log)

#     BASE_URL = "https://4dhjz4-37-113-214-206.ru.tuna.am/tasks"

#     position = 13  # номер темы (позиции) - можно сделать динамическим
#     user_id = message.from_user.id

#     # Формируем полный URL
#     webapp_url = f"{BASE_URL}/{position}"

#     # Создаём кнопку с WebApp

#     await message.answer(
#         "Нажмите кнопку ниже, чтобы открыть список задач и выбрать нужные для печати:",
#         reply_markup=web_sections_keyboard(webapp_url=webapp_url),
#         # reply_markup=webapp_keyboard(webapp_url=webapp_url),
#     )

BASE_URL = "https://vs7yfk-37-113-214-170.ru.tuna.am"
TASKS_URL = f"{BASE_URL}/tasks"
CART_URL = f"{BASE_URL}/cart"


@user_router.message(Command("choose"))
async def cmd_tasks(message: Message, redis: Redis):
    if not redis:
        await message.answer("Ошибка: Redis не доступен")
        return

    user_id = message.from_user.id
    cart_json = await redis.get(f"cart:{user_id}")
    cart = json.loads(cart_json) if cart_json else []

    keyboard = web_sections_keyboard(base_url=TASKS_URL, cart=cart)

    await message.answer(
        "📚 Выберите тему, чтобы добавить задачи в корзину.\n"
        "Уже выбранные задачи будут отмечены галочками.\n\n",
        reply_markup=keyboard,
    )


@user_router.message(Command("cart"))
async def cmd_cart(message: Message, redis: Redis):
    user_id = message.from_user.id
    cart_json = await redis.get(f"cart:{user_id}")
    cart = json.loads(cart_json) if cart_json else []
    size = len(cart)

    if size == 0:
        await message.answer("📭 Корзина пуста. Используйте /choose для выбора задач.")
        return

    keyboard = cart_management_keyboard(
        cart_size=size, base_cart_url=CART_URL, cart=cart
    )
    await message.answer(
        f"📦 В корзине {size} задач.\n"
        "Вы можете отредактировать список (снять/отметить задачи) или сразу отправить на печать.",
        reply_markup=keyboard,
    )


@user_router.callback_query(F.data == "print_cart")
async def print_cart_callback(
    callback: CallbackQuery,
    redis: Redis,
    conn: AsyncConnection,
    texlive,
    i18n: dict,
):
    user_id = callback.from_user.id
    cart_json = await redis.get(f"cart:{user_id}")
    cart = json.loads(cart_json) if cart_json else []

    if not cart:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    keyboard = cart_management_keyboard(
        cart_size=len(cart), base_cart_url=CART_URL, cart=cart
    )

    # await message.answer()
    await callback.message.edit_text(
        text=i18n.get("compiling"),
        reply_markup=keyboard,
        show_alert=False,
    )
    problems = await get_problems_by_ids(conn, cart)
    pdf_doc = await make_problems_pdf(problems, user_id, texlive)

    await callback.message.edit_text(
        text=i18n.get("compilation_done"),
        reply_markup=keyboard,
        show_alert=False,
    )
    await callback.message.answer_document(document=pdf_doc)

    await callback.answer()


@user_router.callback_query(F.data == "clear_cart")
async def clear_cart_callback(callback: CallbackQuery, redis: Redis):
    user_id = callback.from_user.id
    await redis.delete(f"cart:{user_id}")
    await callback.answer("Корзина очищена", show_alert=True)
    # Можно также отредактировать сообщение или отправить новое
    await callback.message.edit_text(
        "🗑️ Корзина очищена. Используйте /choose для выбора задач."
    )


@user_router.message(F.web_app_data)
async def handle_webapp_data(message: Message, redis: Redis, conn: AsyncConnection):
    logger.info(f"Получены данные: {message.web_app_data.data}")
    data = json.loads(message.web_app_data.data)
    logger.info(f"Разобранные данные: {data}")
    task_ids = data.get("task_ids", [])
    position = data.get(
        "position"
    )  # будет только для /tasks/{position}, для /cart — None

    user_id = message.from_user.id
    cart_key = f"cart:{user_id}"
    cart_json = await redis.get(cart_key)
    current_cart = set(json.loads(cart_json)) if cart_json else set()

    if position:
        # Режим: добавление/удаление задач из конкретной темы
        tasks_in_topic = await get_problem_ids_by_position(conn, position)
        topic_ids = {task["source_id"] for task in tasks_in_topic}

        current_cart -= topic_ids
        current_cart.update(task_ids)
        new_cart = list(current_cart)
        await redis.set(cart_key, json.dumps(new_cart), ex=604800)  # 7 дней
        await message.answer(f"📦 Теперь в корзине {len(new_cart)} задач.")
    else:
        # Режим: полная замена корзины (из /cart)
        await redis.set(cart_key, json.dumps(task_ids), ex=604800)
        await message.answer(f"✅ Корзина обновлена.\n📦 Теперь {len(task_ids)} задач.")


@user_router.message(F.web_app_data)
async def handle_webapp_data(
    message: Message, state: FSMContext, conn: AsyncConnection
):
    logger.info(f"📩 Получены данные из WebApp: {message.web_app_data.data}")
    await message.answer("✅ Данные получены!")


@user_router.message(Command("done"))
async def compile_selected_tasks(
    message: Message, state: FSMContext, conn: AsyncConnection, texlive
):
    user_data = await state.get_data()
    selected_tasks = user_data.get("selected_tasks", [])

    if not selected_tasks:
        await message.answer("❌ Корзина пуста. Используйте /choose для выбора задач.")
        return

    await message.answer(f"📦 Начинаю компиляцию {len(selected_tasks)} задач...")

    problems = await get_problems_by_ids(conn, selected_tasks)
    pdf_doc = await make_problems_pdf(problems, message.from_user.id, texlive)

    await message.answer_document(document=pdf_doc, caption="✅ Ваш PDF готов!")

    await state.update_data(selected_tasks=[])
    await state.clear()


@user_router.message(Command("selected"))
async def show_selected(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_tasks = user_data.get("selected_tasks", [])

    if not selected_tasks:
        await message.answer("📭 Корзина пуста. Используйте /choose для выбора.")
        return

    tasks_preview = "\n".join(selected_tasks[:20])
    await message.answer(
        f"📦 Выбрано задач: {len(selected_tasks)}\n"
        f"ID задач:\n{tasks_preview}" + ("\n..." if len(selected_tasks) > 20 else "")
    )


@user_router.message(Command("test"))
async def cmd_test(message: Message):
    # Базовый URL без /tasks (корневой)
    # замените на ваш домен
    test_url = f"{BASE_URL}/test"
    keyboard = test_keyboard(url=test_url)
    await message.answer("Нажмите кнопку для теста:", reply_markup=keyboard)
