"""Camada de acesso ao banco (CRUD) para a entidade User.

Isola todas as queries para que as rotas não dependam diretamente do ORM.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import hash_password
from entities.user import User
from routes.schemas import UserCreate, UserUpdate


class EmailAlreadyExistsError(Exception):
    """Levantada quando o email informado já está cadastrado (conflito)."""


def create_user(db: Session, user_in: UserCreate) -> User:
    """Cria um usuário, hasheando a senha e tratando email duplicado."""
    user = User(
        name=user_in.name,
        email=user_in.email,
        password=hash_password(user_in.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyExistsError("Email já cadastrado.") from exc
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    """Retorna o usuário pelo id, ou None se não existir."""
    return db.get(User, user_id)


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Lista usuários de forma paginada."""
    stmt = select(User).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User | None:
    """Atualiza apenas os campos enviados; re-hasheia a senha se informada."""
    user = db.get(User, user_id)
    if user is None:
        return None

    data = user_in.model_dump(exclude_unset=True)
    if "password" in data:
        data["password"] = hash_password(data["password"])

    for field, value in data.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyExistsError("Email já cadastrado.") from exc
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Remove o usuário; retorna True se removido, False se não existir."""
    user = db.get(User, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
