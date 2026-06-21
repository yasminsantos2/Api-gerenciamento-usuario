"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.connection import init_db
from routes.user_routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas (app.db) na inicialização.
    init_db()
    yield


app = FastAPI(title="API Gerenciamento de Usuário", lifespan=lifespan)
app.include_router(router)
