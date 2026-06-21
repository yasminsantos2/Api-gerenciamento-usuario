"""US-09 - Routes: endpoint GET /users/ (paginação).

Critério: retorna lista paginada; skip/limit funcionam; nenhum password exposto.
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


def _criar_usuarios(client, quantidade):
    for i in range(quantidade):
        resp = client.post(
            "/users/",
            json={
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "password": "segredo123",
            },
        )
        assert resp.status_code == 201


def test_get_users_retorna_lista(client):
    _criar_usuarios(client, 3)
    resp = client.get("/users/")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 3


def test_get_users_lista_vazia(client):
    resp = client.get("/users/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_users_limit_funciona(client):
    _criar_usuarios(client, 5)
    resp = client.get("/users/?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_users_skip_funciona(client):
    _criar_usuarios(client, 5)
    todos = client.get("/users/?limit=100").json()
    pulados = client.get("/users/?skip=2&limit=100").json()
    assert len(pulados) == 3
    assert pulados[0]["id"] == todos[2]["id"]


def test_get_users_sem_password(client):
    _criar_usuarios(client, 2)
    body = client.get("/users/").json()
    for item in body:
        assert "password" not in item


def test_get_users_validacao_parametros_invalidos(client):
    # skip negativo e limit fora do intervalo devem ser rejeitados (422).
    assert client.get("/users/?skip=-1").status_code == 422
    assert client.get("/users/?limit=0").status_code == 422
    assert client.get("/users/?limit=1000").status_code == 422
