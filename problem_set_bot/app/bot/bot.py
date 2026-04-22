import logging

import psycopg_pool
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.bot.handlers.admin import admin_router
from app.bot.handlers.others import others_router
from app.bot.handlers.settings import settings_router
from app.bot.handlers.user import user_router
from app.bot.i18n.translator import get_translations
from app.bot.middlewares.database import DataBaseMiddleware
from app.bot.middlewares.i18n import TranslatorMiddleware
from app.bot.middlewares.lang_settings import LangSettingsMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.statistics import ActivityCounterMiddleware
from app.infrastructure.database.connection import get_pg_pool
from config.config import Config
from redis.asyncio import Redis

from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

import asyncio
from app.webapp import run_webapp

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main(config: Config) -> None:
    logger.info("Starting bot...")
    # 1. Создаем клиент отдельно
    redis_client = Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        username=config.redis.username,
        decode_responses=True,  # Важно для работы с текстом/JSON
    )

    # 2. Передаем его в хранилище FSM
    storage = RedisStorage(redis=redis_client)

    if config.proxy.enabled:
        if config.proxy.url.startswith("socks"):
            connector = ProxyConnector.from_url(config.proxy.url)
            session = AiohttpSession(connector=connector)
        else:
            # HTTP/HTTPS прокси
            session = AiohttpSession(proxy=config.proxy.url)
    else:
        session = AiohttpSession()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.bot.token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # Создаём пул соединений с Postgres
    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )

    asyncio.create_task(
        run_webapp(
            host=config.webapp.host,
            port=config.webapp.port,
            db_pool=db_pool,
            redis_client=redis_client,
            bot_token=config.bot.token,
            bot=bot,
            base_url=config.webapp.base_url,
        )
    )

    # Получаем словарь с переводами
    translations = get_translations()
    # формируем список локалей из ключей словаря с переводами
    # locales = list(translations.keys())
    locales = ["ru"]

    texlive = config.tex

    # Подключаем роутеры в нужном порядке
    logger.info("Including routers...")
    dp.include_routers(settings_router, admin_router, user_router, others_router)

    # Подключаем миддлвари в нужном порядке
    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware())
    dp.update.middleware(ShadowBanMiddleware())
    dp.update.middleware(ActivityCounterMiddleware())
    # dp.update.middleware(LangSettingsMiddleware())
    dp.update.middleware(TranslatorMiddleware())

    # Запускаем поллинг
    try:
        await dp.start_polling(
            bot,
            db_pool=db_pool,
            translations=translations,
            locales=locales,
            admin_ids=config.bot.admin_ids,
            texlive=texlive,
            storage=storage,
            redis=redis_client,
            base_url=config.webapp.base_url,
        )
    except Exception as e:
        logger.exception(e)
    finally:
        # Закрываем пул соединений
        await db_pool.close()
        logger.info("Connection to Postgres closed")
