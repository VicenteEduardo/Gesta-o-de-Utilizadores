"""Dependências partilhadas das rotas: repositório e utilizador autenticado."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.domain.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repository_impl import SQLUserRepository
from app.infrastructure.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_repo(db: Session = Depends(get_db)) -> SQLUserRepository:
    return SQLUserRepository(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: SQLUserRepository = Depends(get_repo),
) -> User:
    try:
        email = decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user = repo.get_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não existe.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(current: User = Depends(get_current_user)) -> User:
    if not current.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação reservada a administradores.",
        )
    return current
