"""Rotas HTTP para o recurso de usuários.

A camada de rotas só conversa com o repository; não acessa o ORM diretamente.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from repository import user_repository as repo
from repository.user_repository import EmailAlreadyExistsError
from routes.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """Cria um usuário. Retorna 201 com UserOut ou 409 se o email já existir."""
    try:
        return repo.create_user(db, user_in)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado.",
        )
