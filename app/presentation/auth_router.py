"""Rota de autenticação: aceita JSON e form OAuth2 (para o Swagger)."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.application.auth_service import AuthService
from app.domain.exceptions import InvalidCredentials
from app.infrastructure.repository_impl import SQLUserRepository
from app.presentation.dependencies import get_repo
from app.presentation.schemas import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login_json(payload: LoginIn, repo: SQLUserRepository = Depends(get_repo)):
    try:
        token = AuthService(repo).login(payload.email, payload.password)
        return TokenOut(access_token=token)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/token", response_model=TokenOut, include_in_schema=False)
def login_form(form: OAuth2PasswordRequestForm = Depends(),
               repo: SQLUserRepository = Depends(get_repo)):
    try:
        token = AuthService(repo).login(form.username, form.password)
        return TokenOut(access_token=token)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
