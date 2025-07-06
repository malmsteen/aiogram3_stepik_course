from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    USER: SecretStr = Field(
        default=os.getenv("REDIS_USERNAME", "default"),
        description="Redis username",
    )


def get_settings() -> Settings:
    settings = Settings()
    print(f"Redis user: {settings.USER.get_secret_value()}")
    settings.USER = SecretStr(os.getenv("REDIS_USERNAME", "default"))
    print(f"Redis user: {settings.USER.get_secret_value()}")
    return settings


if __name__ == "__main__":
    settings = get_settings()
    print(settings.USER.get_secret_value())