"""US-01 - Infra: setup do projeto e ambiente.

Critérios: venv ativa; pip install roda sem erro; uvicorn --version responde.
"""

import importlib
import subprocess
import sys


def test_venv_ativa():
    """O Python em uso deve ser o do ambiente virtual (venv)."""
    assert sys.prefix != sys.base_prefix, "venv não está ativa"


def test_dependencias_principais_instaladas():
    """As dependências principais do projeto devem importar sem erro."""
    for modulo in ("fastapi", "sqlalchemy", "pydantic", "email_validator", "passlib", "bcrypt"):
        assert importlib.import_module(modulo) is not None


def test_uvicorn_version_responde():
    """O comando `uvicorn --version` deve responder com sucesso."""
    result = subprocess.run(
        [sys.executable, "-m", "uvicorn", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "uvicorn" in result.stdout.lower()
