"""US-05 - Core/Security: hash de senha.

Critério: hash != texto puro; verify_password retorna True para senha correta
e False caso contrário.
"""

from core.security import hash_password, verify_password


def test_hash_diferente_do_texto_puro():
    """O hash gerado não pode ser igual à senha em texto puro."""
    senha = "minhaSenha123"
    hashed = hash_password(senha)
    assert hashed != senha
    assert senha not in hashed


def test_verify_password_senha_correta():
    """verify_password deve retornar True para a senha correta."""
    senha = "minhaSenha123"
    hashed = hash_password(senha)
    assert verify_password(senha, hashed) is True


def test_verify_password_senha_incorreta():
    """verify_password deve retornar False para senha incorreta."""
    hashed = hash_password("minhaSenha123")
    assert verify_password("senhaErrada", hashed) is False


def test_hashes_diferentes_para_mesma_senha():
    """Cada hash usa salt próprio, logo dois hashes da mesma senha diferem."""
    senha = "minhaSenha123"
    assert hash_password(senha) != hash_password(senha)


def test_limite_72_bytes_tratado():
    """Senhas maiores que 72 bytes devem ser tratadas sem gerar erro."""
    senha_longa = "a" * 100
    hashed = hash_password(senha_longa)
    assert verify_password(senha_longa, hashed) is True
