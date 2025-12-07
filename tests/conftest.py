import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.user import User

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    # Удалить старый файл, если есть
    if TEST_DATABASE_URL.startswith("sqlite"):
        path = TEST_DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(path):
            os.remove(path)

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        future=True,
    )

    # Создание таблиц
    Base.metadata.create_all(bind=engine)

    # Переопределение get_db для приложения
    app = create_app()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Делаем app и TestingSessionLocal доступными через yield
    yield app, TestingSessionLocal

    # После тестов
    Base.metadata.drop_all(bind=engine)
    if TEST_DATABASE_URL.startswith("sqlite"):
        path = TEST_DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture()
def app(setup_test_db):
    app, _ = setup_test_db
    return app


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def db_session(setup_test_db):
    _, TestingSessionLocal = setup_test_db
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_user(db_session):
    # Проверяем, не создан ли уже такой пользователь
    existing = db_session.query(User).filter(User.email == "test@example.com").first()
    if existing:
        return existing

    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user):
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}
