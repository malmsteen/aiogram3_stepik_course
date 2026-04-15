# app/webapp/handlers.py
import logging
from aiohttp import web
import aiohttp_jinja2
from app.infrastructure.database.db import (
    get_problem_texts,
    get_problems_by_ids,
    webapp_get_problem_ids_by_position,
)
import json

logger = logging.getLogger(__name__)


@aiohttp_jinja2.template("test.html")
async def test_page(request):
    return {}


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
        "title": f"Тема {position}",  # или можно брать название из списка sections, если передать
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


async def api_update_cart(request):
    data = await request.json()
    user_id = data.get("user_id")
    cart = data.get("cart", [])
    position = data.get("position")
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
