"""US-03 - Entities: modelo ORM User.

Critérios: tabela mapeada corretamente; email é único; timestamps definidos.
"""

import time

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.connection import Base
from entities.user import User


@pytest.fixture()
def session():
    """Sessão isolada usando um banco SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_tabela_mapeada_corretamente():
    """A entidade deve mapear a tabela 'users' com todas as colunas exigidas."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    colunas = {c["name"] for c in inspect(engine).get_columns("users")}

    assert User.__tablename__ == "users"
    assert colunas == {
        "id",
        "name",
        "email",
        "password",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_id_e_primary_key_autoincrement(session):
    """O id deve ser preenchido automaticamente (PK autoincrement)."""
    user = User(name="Ana", email="ana@example.com", password="secret")
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.id is not None


def test_email_e_unico(session):
    """Inserir dois usuários com o mesmo email deve falhar (UNIQUE)."""
    session.add(User(name="Ana", email="dup@example.com", password="x"))
    session.commit()

    session.add(User(name="Bia", email="dup@example.com", password="y"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_email_tem_indice():
    """O email deve possuir índice único."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    indices = inspect(engine).get_indexes("users")
    assert any(
        ix["column_names"] == ["email"] and ix["unique"] for ix in indices
    )


def test_is_active_default_true(session):
    """is_active deve assumir True por padrão quando não informado."""
    user = User(name="Ana", email="ana2@example.com", password="x")
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.is_active is True


def test_timestamps_definidos_na_criacao(session):
    """created_at e updated_at devem ser preenchidos na inserção."""
    user = User(name="Ana", email="ana3@example.com", password="x")
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.created_at is not None
    assert user.updated_at is not None


def test_updated_at_muda_no_update(session):
    """updated_at deve ser atualizado automaticamente ao alterar o registro."""
    user = User(name="Ana", email="ana4@example.com", password="x")
    session.add(user)
    session.commit()
    session.refresh(user)
    original = user.updated_at

    # Garante diferença de tempo perceptível (resolução de 1s no SQLite).
    time.sleep(1.1)

    user.name = "Ana Atualizada"
    session.commit()
    session.refresh(user)

    assert user.updated_at >= original
