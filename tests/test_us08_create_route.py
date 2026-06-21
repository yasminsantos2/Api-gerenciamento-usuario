"""US-08 - Routes: endpoint POST /users/.

Critério: 201 no sucesso; 409 em email repetido; resposta sem password.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.connection import Base, get_db
from routes.user_routes import router


@pytest.fixture()
def client():
    """Cliente de teste com banco SQLite em memória isolado por teste."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


def test_post_users_retorna_201(client):
    resp = client.post(
        "/users/",
        json={"name": "Ana", "email": "ana@example.com", "password": "segredo123"},
    )
    assert resp.status_code == 201


def test_post_users_resposta_sem_password(client):
    resp = client.post(
        "/users/",
        json={"name": "Ana", "email": "ana2@example.com", "password": "segredo123"},
    )
    body = resp.json()
    assert "password" not in body
    assert body["email"] == "ana2@example.com"
    assert body["id"] is not None


def test_post_users_email_duplicado_retorna_409(client):
    payload = {"name": "Ana", "email": "dup@example.com", "password": "segredo123"}
    primeira = client.post("/users/", json=payload)
    assert primeira.status_code == 201

    segunda = client.post("/users/", json=payload)
    assert segunda.status_code == 409


def test_post_users_email_invalido_retorna_422(client):
    resp = client.post(
        "/users/",
        json={"name": "Ana", "email": "nao-eh-email", "password": "segredo123"},
    )
    assert resp.status_code == 422
