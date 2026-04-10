# app/webapp/middlewares.py
import logging
from aiohttp import web
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


@web.middleware
async def db_middleware(request: web.Request, handler):
    """
    Middleware для aiohttp, который:
    - берёт пул соединений из request.app['db_pool']
    - открывает новое соединение
    - начинает транзакцию
    - кладёт соединение в request['conn']
    - после обработки запроса транзакция завершается (commit/rollback)
    """
    pool: AsyncConnectionPool = request.app.get("db_pool")
    if pool is None:
        logger.error("Database pool not found in app['db_pool']")
        raise web.HTTPInternalServerError(text="Database pool not configured")

    async with pool.connection() as conn:
        async with conn.transaction():
            request["conn"] = conn
            response = await handler(request)
            return response
