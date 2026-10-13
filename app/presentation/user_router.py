"""Endpoints de gestão de utilizadores.

Regras de acesso:
- Registo é público, mas cria sempre contas com perfil `user`.
- Leitura/alteração: o próprio utilizador ou um admin.
- Listagem e alteração de perfil (`role`): só admin.
"""
from typing import List, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.user_service import UserService
from app.domain.exceptions import (
    DomainError,
    EmailAlreadyExists,
    Forbidden,
    UserNotFound,
)
from app.domain.user import User
from app.infrastructure.repository_impl import SQLUserRepository
from app.presentation.dependencies import get_current_user, get_repo, require_admin
from app.presentation.schemas import RoleUpdate, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def to_response(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )


def raise_as_http(exc: DomainError) -> NoReturn:
    if isinstance(exc, UserNotFound):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, EmailAlreadyExists):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, Forbidden):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


def service_for(repo: SQLUserRepository) -> UserService:
    return UserService(repo)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, repo: SQLUserRepository = Depends(get_repo)):
    """Regista um novo utilizador (perfil `user`)."""
    try:
        user = service_for(repo).register(payload.name, payload.email, payload.password)
    except EmailAlreadyExists as exc:
        raise_as_http(exc)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return to_response(user)


@router.get("/me", response_model=UserOut)
def read_me(current: User = Depends(get_current_user)):
    """Devolve o perfil do utilizador autenticado."""
    return to_response(current)


@router.get("", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current: User = Depends(require_admin),
    repo: SQLUserRepository = Depends(get_repo),
):
    """Lista utilizadores (só admin, com paginação)."""
    try:
        users = service_for(repo).list(current, skip=skip, limit=limit)
    except Forbidden as exc:
        raise_as_http(exc)
    return [to_response(user) for user in users]


@router.get("/{user_id}", response_model=UserOut)
def read_user(
    user_id: int,
    current: User = Depends(get_current_user),
    repo: SQLUserRepository = Depends(get_repo),
):
    """Consulta um utilizador pelo id."""
    try:
        user = service_for(repo).get(user_id, current)
    except DomainError as exc:
        raise_as_http(exc)
    return to_response(user)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    current: User = Depends(get_current_user),
    repo: SQLUserRepository = Depends(get_repo),
):
    """Actualiza nome/email de um utilizador."""
    try:
        user = service_for(repo).update(user_id, current, payload.name, payload.email)
    except DomainError as exc:
        raise_as_http(exc)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return to_response(user)


@router.patch("/{user_id}/role", response_model=UserOut)
def change_user_role(
    user_id: int,
    payload: RoleUpdate,
    current: User = Depends(require_admin),
    repo: SQLUserRepository = Depends(get_repo),
):
    """Altera o perfil de um utilizador (`admin`/`user`). Só admin."""
    try:
        user = service_for(repo).change_role(user_id, current, payload.role)
    except DomainError as exc:
        raise_as_http(exc)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return to_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current: User = Depends(get_current_user),
    repo: SQLUserRepository = Depends(get_repo),
) -> None:
    """Elimina um utilizador."""
    try:
        service_for(repo).remove(user_id, current)
    except DomainError as exc:
        raise_as_http(exc)
