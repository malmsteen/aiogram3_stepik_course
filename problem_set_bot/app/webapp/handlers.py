# app/webapp/handlers.py

from aiohttp import web
from aiogram.utils.web_app import safe_parse_webapp_init_data
import aiohttp_jinja2
from app.infrastructure.database.db import (
    get_problem_texts,
    get_problems_by_ids,
    webapp_get_problem_ids_by_position,
)
import json, hmac, hashlib, logging, time
from urllib.parse import parse_qsl
from app.bot.keyboards.keyboards import sections

logger = logging.getLogger(__name__)


@aiohttp_jinja2.template("test.html")
async def test_page(request):
    return {}


@aiohttp_jinja2.template("choose.html")
async def choose_page(request: web.Request):
    cart_param = request.query.get("cart", "")
    cart_ids = cart_param.split(",") if cart_param else []
    return {"sections": sections, "cart_str": cart_param, "cart_size": len(cart_ids)}


@aiohttp_jinja2.template("tasks.html")
async def tasks_page(request: web.Request):
    """
    GET /tasks/{position}?cart=id1,id2,id3
    Показывает задачи для указанной позиции, отмечает те, что уже в корзине (из параметра cart)
    """
    conn = request["conn"]
    position = int(request.match_info.get("position", 13))
    cart_param = request.query.get("cart", "")
    cart_ids = cart_param.split(",") if cart_param else []

    tasks = await get_problem_texts(conn, position)
    for task in tasks:
        task["checked"] = task["source_id"] in cart_ids

    return {
        "title": sections[position - 1],
        "tasks": tasks,
        "position": position,
    }


@aiohttp_jinja2.template("tasks.html")
async def cart_page(request: web.Request):
    conn = request["conn"]
    cart_param = request.query.get("cart", "")  # читаем корзину из URL
    cart_ids = cart_param.split(",") if cart_param else []

    if not cart_ids:
        tasks = []
    else:
        tasks = await get_problems_by_ids(conn, cart_ids)
        for task in tasks:
            task["checked"] = True

    return {
        "title": "✏️ Редактирование корзины",
        "tasks": tasks,  # ← передаём задачи, а не пустой список
        "position": 0,
    }


def validate_init_data(init_data, bot_token):
    if not init_data:
        return None, "empty_init_data"
    try:
        parsed = safe_parse_webapp_init_data(token=bot_token, init_data=init_data)
        if parsed and parsed.user:
            return {"id": parsed.user.id}, "safe_parse_ok"
    except Exception as exc:
        logger.warning("safe_parse_webapp_init_data failed: %s", exc)

    data = dict(parse_qsl(init_data, keep_blank_values=True))

    # Убираем hash, т.к. подпись считается ТОЛЬКО по остальным полям
    got_hash = data.pop("hash", "")
    auth_date_raw = data.get("auth_date", "0")
    try:
        auth_date = int(auth_date_raw)
    except (TypeError, ValueError):
        return None, "bad_auth_date_format"

    if not got_hash:
        return None, "hash_missing"
    age_seconds = int(time.time() - auth_date)
    if age_seconds > 86400:
        return None, f"auth_date_too_old:{age_seconds}"

    # Все параметры вписываем в одну строку
    data_check_string = "\n".join(f"{k}={data[k]}" for k in sorted(data.keys()))

    # Делаем секретный ключ по правилам Telegram (https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    # Читаем подпись и сравниваем с тем хешем, что пришел в initData
    calc_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calc_hash, got_hash):
        return None, "hash_mismatch"

    if "user" not in data:
        return None, "user_missing"
    return json.loads(data["user"]), "manual_parse_ok"


async def api_update_cart(request):
    data = await request.json()
    init_data = data.get("initData")
    cart = data.get("cart", [])
    if not isinstance(cart, list) or len(cart) > 500:
        return web.json_response({"error": "Invalid cart data"}, status=400)
    position = data.get("position")

    # Получаем токен из приложения
    bot_token = request.app.get("bot_token")
    if not bot_token:
        logger.error("BOT_TOKEN not configured in app")
        return web.json_response({"error": "Server configuration error"}, status=500)

    user, reason = validate_init_data(init_data, bot_token)
    if not user or "id" not in user:
        parsed = dict(parse_qsl(init_data or "", keep_blank_values=True))
        auth_date_raw = parsed.get("auth_date")
        now = int(time.time())
        try:
            age = now - int(auth_date_raw) if auth_date_raw else None
        except (TypeError, ValueError):
            age = "invalid"
        logger.warning(
            "Invalid init data in /api/update_cart: reason=%s len=%s has_hash=%s has_user=%s auth_age=%s position=%s cart_size=%s",
            reason,
            len(init_data or ""),
            "hash" in parsed,
            "user" in parsed,
            age,
            position,
            len(cart),
        )
        return web.json_response({"error": "Invalid init data"}, status=401)
    user_id = user["id"]

    redis = request.app.get("redis")
    if not redis:
        return web.json_response(
            {"status": "error", "message": "Redis not configured"}, status=500
        )

    cart_key = f"cart:{user_id}"
    current_cart_json = await redis.get(cart_key)
    current_cart = json.loads(current_cart_json) if current_cart_json else []

    if position:
        # Получаем все source_id задач этой позиции
        conn = request.get("conn")
        topic_ids = set(await webapp_get_problem_ids_by_position(conn, position))
        # Удаляем все задачи этой темы из корзины (сохраняя порядок остальных)
        new_cart = [item for item in current_cart if item not in topic_ids]
        # Добавляем новые выбранные задачи в конец
        new_cart.extend(cart)
    else:
        new_cart = cart

    await redis.set(cart_key, json.dumps(new_cart), ex=604800)
    return web.json_response({"status": "ok"})


async def api_get_cart(request: web.Request):
    data = await request.json()
    user_id = data.get("user_id")
    redis = request.app.get("redis")
    if not redis:
        return web.json_response(
            {"status": "error", "message": "Redis not configured"}, status=500
        )
    cart_json = await redis.get(f"cart:{user_id}")
    cart = json.loads(cart_json) if cart_json else []
    return web.json_response({"cart": cart})


# app/webapp/handlers.py


async def api_get_cart_tasks(request):
    data = await request.json()
    user_id = data.get("user_id")
    redis = request.app.get("redis")
    conn = request.get("conn")
    if not redis or not conn:
        return web.json_response({"error": "Server error"}, status=500)

    cart_json = await redis.get(f"cart:{user_id}")
    cart_ids = json.loads(cart_json) if cart_json else []
    if not cart_ids:
        return web.json_response({"tasks": []})

    tasks = await get_problems_by_ids(conn, cart_ids)  # возвращает список словарей
    # Сортируем задачи в соответствии с порядком cart_ids
    task_dict = {task["source_id"]: task for task in tasks}
    sorted_tasks = [task_dict[tid] for tid in cart_ids if tid in task_dict]
    for task in sorted_tasks:
        task["checked"] = True
    return web.json_response({"tasks": sorted_tasks})


# async def select_tasks(request: web.Request) -> web.Response:
#     """
#     POST /api/select (не используется, оставлен для совместимости)
#     """
#     conn = request["conn"]
#     data = await request.json()
#     logger.info(
#         f"User {data.get('user_id')} selected {len(data.get('task_ids', []))} tasks"
#     )
#     return web.json_response({"status": "ok"})
