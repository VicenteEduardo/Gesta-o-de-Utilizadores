"""Entry point FastAPI + tratamento global de erros."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.infrastructure.database import Base, engine
from app.infrastructure.models import UserModel  # noqa: F401 (regista tabela)
from app.presentation.auth_router import router as auth_router
from app.presentation.user_router import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Gestão de Utilizadores", version="1.0.0")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(auth_router)
app.include_router(user_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
