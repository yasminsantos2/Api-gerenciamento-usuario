"""US-07 - Repository: funções de acesso ao banco (CRUD).

Critério: cada função executa contra o banco; email duplicado é detectado;
update altera só campos enviados.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.connection import Base
from repository import user_repository as repo
from repository.user_repository import EmailAlreadyExistsError
from routes.schemas import UserCreate, UserUpdate


@pytest.fixture()
def session():
    """Sessão isolada usando um banco SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def _novo_usuario(session, email="ana@example.com", password="segredo123"):
    return repo.create_user(
        session, UserCreate(name="Ana", email=email, password=password)
    )


def test_create_user_persiste_e_hasheia_senha(session):
    user = _novo_usuario(session)
    assert user.id is not None
    assert user.password != "segredo123"  # senha foi hasheada


def test_create_user_email_duplicado_gera_conflito(session):
    _novo_usuario(session, email="dup@example.com")
    with pytest.raises(EmailAlreadyExistsError):
        _novo_usuario(session, email="dup@example.com")


def test_get_user(session):
    user = _novo_usuario(session)
    encontrado = repo.get_user(session, user.id)
    assert encontrado is not None
    assert encontrado.id == user.id


def test_get_user_inexistente_retorna_none(session):
    assert repo.get_user(session, 999) is None


def test_list_users_paginado(session):
    for i in range(5):
        _novo_usuario(session, email=f"user{i}@example.com")
    pagina = repo.list_users(session, skip=1, limit=2)
    assert len(pagina) == 2


def test_update_user_altera_so_campos_enviados(session):
    user = _novo_usuario(session)
    email_original = user.email

    atualizado = repo.update_user(session, user.id, UserUpdate(name="Novo Nome"))
    assert atualizado.name == "Novo Nome"
    assert atualizado.email == email_original  # não foi alterado


def test_update_user_rehasheia_senha(session):
    user = _novo_usuario(session)
    hash_antigo = user.password

    atualizado = repo.update_user(
        session, user.id, UserUpdate(password="novaSenha456")
    )
    assert atualizado.password != hash_antigo
    assert atualizado.password != "novaSenha456"


def test_update_user_inexistente_retorna_none(session):
    assert repo.update_user(session, 999, UserUpdate(name="x")) is None


def test_delete_user(session):
    user = _novo_usuario(session)
    assert repo.delete_user(session, user.id) is True
    assert repo.get_user(session, user.id) is None


def test_delete_user_inexistente_retorna_false(session):
    assert repo.delete_user(session, 999) is False
