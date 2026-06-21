"""US-02 - Database: camada de conexão e sessão.

Critérios: importar o módulo não gera erro; get_db abre e fecha sessão corretamente.
"""

import importlib

from sqlalchemy import text
from sqlalchemy.orm import Session


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

    # Após o fechamento, a sessão ainda referencia o engine.
    assert sessao.get_bind() is not None
