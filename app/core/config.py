from secrets import token_urlsafe

from pydantic import AnyUrl, BaseSettings, SecretStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "Product Roadmap API"
    API_V1_PREFIX: str = ""  # корень: /roadmaps, /milestones, /stats, /auth

    # Безопасность
    # По умолчанию генерируем случайный ключ для dev/test.
    # В проде обязательно задаём SECRET_KEY через переменную окружения или .env.
    SECRET_KEY: SecretStr = SecretStr(token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # База данных
    DATABASE_URL: AnyUrl | str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
