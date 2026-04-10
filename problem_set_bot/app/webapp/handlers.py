# app/webapp/handlers.py
import logging
from aiohttp import web
import aiohttp_jinja2
from app.infrastructure.database.db import get_problem_texts

logger = logging.getLogger(__name__)


@aiohttp_jinja2.template("tasks.html")
async def tasks_page(request: web.Request):
    """
    GET /tasks/{position}?user_id=12345
    """
    conn = request["conn"]
    position = int(request.match_info.get("position", 13))
    user_id = int(request.query.get("user_id", 0))

    if user_id == 0:
        raise web.HTTPBadRequest(text="Missing user_id")

    tasks = await get_problem_texts(conn, position)

    # Шаблон получит эти переменные
    return {
        "position": position,
        "user_id": user_id,
        "tasks": tasks,
    }


async def select_tasks(request: web.Request) -> web.Response:
    """
    POST /api/select
    Альтернативный эндпоинт, если не использовать tg.sendData в бота.
    """
    conn = request["conn"]
    data = await request.json()
    # Здесь можно сохранить выбор, например:
    # for task_id in data["task_ids"]:
    #     await add_problem_answer(conn, ...)
    logger.info(
        f"User {data.get('user_id')} selected {len(data.get('task_ids', []))} tasks"
    )
    return web.json_response({"status": "ok"})
