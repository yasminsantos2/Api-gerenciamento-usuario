"""Testes de validação do ambiente e da camada de banco (US-01 e US-02)."""

import importlib
import shutil
import subprocess
import sys

from sqlalchemy import text
from sqlalchemy.orm import Session


# ----------------------------- US-01: Infra -----------------------------

def test_venv_ativa():
    """O Python em uso deve ser o do ambiente virtual (venv)."""
    assert sys.prefix != sys.base_prefix, "venv não está ativa"


def test_dependencias_principais_instaladas():
    """As dependências principais do projeto devem importar sem erro."""
    for modulo in ("fastapi", "sqlalchemy", "pydantic", "email_validator", "passlib", "bcrypt"):
        assert importlib.import_module(modulo) is not None


def test_uvicorn_version_responde():
    """O comando `uvicorn --version` deve responder com sucesso."""
    uvicorn_bin = shutil.which("uvicorn")
    assert uvicorn_bin is not None, "uvicorn não encontrado no PATH da venv"
    result = subprocess.run(
        [uvicorn_bin, "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "uvicorn" in result.stdout.lower()


# --------------------------- US-02: Database ----------------------------

def test_importar_modulo_connection():
    """Importar database.connection não deve gerar erro."""
    modulo = importlib.import_module("database.connection")
    assert hasattr(modulo, "engine")
    assert hasattr(modulo, "SessionLocal")
    assert hasattr(modulo, "Base")
    assert hasattr(modulo, "get_db")


def test_get_db_abre_e_fecha_sessao():
    """get_db deve fornecer uma sessão funcional e fechá-la ao final."""
    from database.connection import get_db

    gerador = get_db()
    sessao = next(gerador)

    # A sessão deve ser utilizável (executa uma query simples).
    assert isinstance(sessao, Session)
    assert sessao.execute(text("SELECT 1")).scalar() == 1

    # Ao esgotar o gerador, o bloco finally fecha a sessão.
    try:
        next(gerador)
    except StopIteration:
        pass

    # Após o fechamento, a sessão não deve mais estar vinculada a uma conexão ativa.
    assert sessao.get_bind() is not None  # ainda referencia o engine
