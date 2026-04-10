# app/webapp/server.py
import aiohttp_jinja2
import jinja2
import logging
from aiohttp import web
from psycopg_pool import AsyncConnectionPool
from .middlewares import db_middleware
from .handlers import tasks_page, select_tasks  # если нужен POST

logger = logging.getLogger(__name__)


async def run_webapp(
    host: str,
    port: int,
    db_pool: AsyncConnectionPool,
) -> None:
    """Запускает aiohttp сервер в существующем event loop (не блокирует)."""
    app = web.Application(middlewares=[db_middleware])
    app["db_pool"] = db_pool

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("app/webapp/templates"))
    # Роуты
    app.router.add_get("/tasks/{position}", tasks_page)
    # если нужен POST-обработчик:
    # app.router.add_post('/api/select', select_tasks)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()

    logger.info(f"WebApp server started on http://{host}:{port}")
    # сервер работает в фоне, runner не останавливается
