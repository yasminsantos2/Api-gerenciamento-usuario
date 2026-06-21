"""Camada de segurança: hashing e verificação de senha.

Isola o uso do bcrypt para que o restante da aplicação dependa apenas de
hash_password() e verify_password(), sem conhecer detalhes do algoritmo.
"""

from passlib.context import CryptContext

# bcrypt opera sobre no máximo 72 bytes; entradas maiores são truncadas.
_MAX_BCRYPT_BYTES = 72

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate(password: str) -> str:
    """Garante que a senha respeite o limite de 72 bytes do bcrypt."""
    encoded = password.encode("utf-8")
    if len(encoded) <= _MAX_BCRYPT_BYTES:
        return password
    # Trunca em 72 bytes, descartando bytes incompletos de caracteres multibyte.
    return encoded[:_MAX_BCRYPT_BYTES].decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return _pwd_context.hash(_truncate(password))


def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash informado."""
    return _pwd_context.verify(_truncate(password), hashed)
