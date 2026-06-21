"""US-06 - Schemas: schemas Pydantic de entrada/saída.

Critério: UserOut nunca contém password; email inválido levanta
ValidationError; PATCH aceita campos parciais.
"""

from datetime import datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from routes.schemas import UserCreate, UserOut, UserUpdate


def test_userout_nao_possui_campo_password():
    """O schema de saída não deve declarar o campo password."""
    assert "password" not in UserOut.model_fields


def test_userout_ignora_password_de_objeto_orm():
    """Mesmo lendo um objeto com password, UserOut não o expõe."""
    obj = SimpleNamespace(
        id=1,
        name="Ana",
        email="ana@example.com",
        password="hash-secreto",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    out = UserOut.model_validate(obj)
    assert "password" not in out.model_dump()


def test_email_invalido_levanta_validation_error():
    """Um email malformado deve levantar ValidationError."""
    with pytest.raises(ValidationError):
        UserCreate(name="Ana", email="nao-eh-email", password="123")


def test_email_valido_e_aceito():
    """Um email válido deve ser aceito normalmente."""
    user = UserCreate(name="Ana", email="ana@example.com", password="123")
    assert user.email == "ana@example.com"


def test_patch_aceita_campos_parciais():
    """UserUpdate deve permitir enviar apenas parte dos campos."""
    parcial = UserUpdate(name="Novo Nome")
    enviados = parcial.model_dump(exclude_unset=True)
    assert enviados == {"name": "Novo Nome"}


def test_patch_aceita_corpo_vazio():
    """UserUpdate com todos os campos ausentes deve ser válido."""
    vazio = UserUpdate()
    assert vazio.model_dump(exclude_unset=True) == {}


def test_userout_le_de_objeto_orm():
    """from_attributes=True permite construir UserOut a partir de objeto ORM."""
    obj = SimpleNamespace(
        id=1,
        name="Ana",
        email="ana@example.com",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    out = UserOut.model_validate(obj)
    assert out.id == 1
    assert out.email == "ana@example.com"
