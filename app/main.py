"""Ponto de entrada da API: cria a app, regista rotas e erros globais."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.infrastructure.database import Base, engine
from app.infrastructure.models import UserModel  # noqa: F401 — regista a tabela
from app.presentation.auth_router import router as auth_router
from app.presentation.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(auth_router)
app.include_router(user_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
