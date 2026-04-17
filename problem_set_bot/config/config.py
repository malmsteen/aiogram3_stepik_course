import logging
import os
from dataclasses import dataclass


from environs import Env

logger = logging.getLogger(__name__)


@dataclass
class BotSettings:
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseSettings:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class RedisSettings:
    host: str
    port: int
    db: int
    password: str
    username: str


@dataclass
class LoggSettings:
    level: str
    format: str


@dataclass
class TexliveSettings:
    host: str
    port: int
    fipiurl: str


@dataclass
class ProxySettings:
    url: str  # например, "socks5://user:pass@ip:port"
    enabled: bool


@dataclass
class WebAppSettings:
    host: str
    port: int
    base_url: str


@dataclass
class Config:
    bot: BotSettings
    db: DatabaseSettings
    redis: RedisSettings
    log: LoggSettings
    tex: TexliveSettings
    proxy: ProxySettings
    webapp: WebAppSettings


def load_config(path: str | None = None) -> Config:
    env = Env()

    if path:
        if not os.path.exists(path):
            logger.warning(".env file not found at '%s', skipping...", path)
        else:
            logger.info("Loading .env from '%s'", path)

    env.read_env(path)

    token = env("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN must not be empty")

    raw_ids = env.list("ADMIN_IDS", default=[])

    try:
        admin_ids = [int(x) for x in raw_ids]
    except ValueError as e:
        raise ValueError(f"ADMIN_IDS must be integers, got: {raw_ids}") from e

    db = DatabaseSettings(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
    )

    redis = RedisSettings(
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        db=env.int("REDIS_DATABASE"),
        password=env("REDIS_PASSWORD", default=""),
        username=env("REDIS_USERNAME", default=""),
    )

    webapp = WebAppSettings(
        host=env("WEBAPP_HOST", default="0.0.0.0"),
        port=env.int("WEBAPP_PORT", default=5000),
        base_url=env("BASE_URL"),
    )

    logg_settings = LoggSettings(level=env("LOG_LEVEL"), format=env("LOG_FORMAT"))

    logger.info("Configuration loaded successfully")

    tex = TexliveSettings(
        host=env("TEXLIVE_HOST"), port=env("TEXLIVE_PORT"), fipiurl=env("HREF_PREF")
    )

    proxy_enabled = env.bool("PROXY_ENABLED", default=False)
    proxy_url = env("PROXY_URL", default="")
    if proxy_enabled and not proxy_url:
        raise ValueError("PROXY_URL must be set when PROXY_ENABLED=True")

    proxy = ProxySettings(enabled=proxy_enabled, url=proxy_url)

    return Config(
        bot=BotSettings(token=token, admin_ids=admin_ids),
        db=db,
        redis=redis,
        log=logg_settings,
        tex=tex,
        proxy=proxy,
        webapp=webapp,
    )
