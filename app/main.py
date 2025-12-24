from fastapi import FastAPI

from app.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.models import Base


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
