"""US-04 - Database: criação do schema.

Critério: ao chamar init_db() o arquivo app.db é criado com a tabela users.
"""

import os

from sqlalchemy import inspect


def test_init_db_cria_app_db_com_tabela_users(tmp_path, monkeypatch):
    """init_db() deve criar o arquivo app.db contendo a tabela 'users'."""
    # Executa em um diretório temporário para não tocar o app.db real.
    monkeypatch.chdir(tmp_path)

    from sqlalchemy import create_engine
    import database.connection as connection

    # Aponta o engine para um app.db dentro do diretório temporário.
    engine = create_engine(
        "sqlite:///./app.db", connect_args={"check_same_thread": False}
    )
    monkeypatch.setattr(connection, "engine", engine)

    connection.init_db()

    db_path = tmp_path / "app.db"
    assert db_path.exists(), "app.db não foi criado"
    assert "users" in inspect(engine).get_table_names()
