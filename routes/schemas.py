"""Schemas Pydantic de entrada/saída, separados da entidade ORM."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Dados de entrada para criação de usuário."""

    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Dados de atualização (PATCH); todos os campos são opcionais."""

    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserOut(BaseModel):
    """Dados de saída do usuário; nunca expõe a senha."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
