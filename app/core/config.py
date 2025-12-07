# app/core/config.py
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "Product Roadmap API"
    API_V1_PREFIX: str = ""  # корень: /roadmaps, /milestones, /stats, /auth

    # Безопасность
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # База данных
    DATABASE_URL: AnyUrl | str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
