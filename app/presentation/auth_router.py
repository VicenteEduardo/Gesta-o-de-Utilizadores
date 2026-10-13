"""Autenticação: recebe credenciais e devolve o token de acesso.

Aceita JSON (`/login`, o mais cómodo para clientes) e formulário OAuth2
(`/token`, o que o botão "Authorize" do Swagger usa).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.auth_service import AuthService
from app.domain.exceptions import InvalidCredentials
from app.infrastructure.repository_impl import SQLUserRepository
from app.presentation.dependencies import get_repo
from app.presentation.schemas import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


def issue_token(repo: SQLUserRepository, email: str, password: str) -> TokenOut:
    try:
        return TokenOut(access_token=AuthService(repo).login(email, password))
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, repo: SQLUserRepository = Depends(get_repo)):
    return issue_token(repo, payload.email, payload.password)


@router.post("/token", response_model=TokenOut, include_in_schema=False)
def login_for_swagger(
    form: OAuth2PasswordRequestForm = Depends(),
    repo: SQLUserRepository = Depends(get_repo),
):
    return issue_token(repo, form.username, form.password)
