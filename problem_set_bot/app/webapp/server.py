# app/webapp/server.py
import logging
import aiohttp_jinja2
import jinja2
from aiohttp import web
from psycopg_pool import AsyncConnectionPool
from .middlewares import db_middleware
from .handlers import (
    tasks_page,
    cart_page,
    test_page,
    api_update_cart,
    api_get_cart,
    api_get_cart_tasks,
)
from aiogram.fsm.storage.redis import RedisStorage

logger = logging.getLogger(__name__)


async def run_webapp(
    host: str, port: int, db_pool: AsyncConnectionPool, redis_client
) -> None:
    app = web.Application(middlewares=[db_middleware])
    app["db_pool"] = db_pool
    app["redis"] = redis_client

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("app/webapp/templates"))

    app.router.add_get("/test", test_page)
    app.router.add_get("/tasks/{position}", tasks_page)
    app.router.add_get("/cart", cart_page)
    app.router.add_post("/api/update_cart", api_update_cart)
    app.router.add_post("/api/get_cart", api_get_cart)
    app.router.add_post("/api/get_cart_tasks", api_get_cart_tasks)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()

    logger.info(f"WebApp server started on http://{host}:{port}")
