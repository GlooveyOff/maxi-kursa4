import os
# тесты гоняем на sqlite, поэтому env подменяем до импорта приложения
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Регистрирует юзера и возвращает заголовки с токеном."""
    client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "tester",
        "password": "secret123",
        "full_name": "Test User",
    })
    resp = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "secret123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
