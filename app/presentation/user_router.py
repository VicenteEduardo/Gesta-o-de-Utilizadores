"""Rotas de utilizadores (CRUD + permissões). Finas: só chamam o service."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.user_service import UserService
from app.domain.exceptions import DomainError
from app.domain.user import User
from app.infrastructure.repository_impl import SQLUserRepository
from app.presentation.dependencies import get_current_user, get_repo, require_admin
from app.presentation.schemas import RoleUpdate, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _service(repo: SQLUserRepository) -> UserService:
    return UserService(repo)


def _out(u: User) -> UserOut:
    return UserOut(id=u.id, name=u.name, email=u.email, role=u.role, is_active=u.is_active)


def _handle(exc: DomainError):
    from app.domain.exceptions import EmailAlreadyExists, Forbidden, UserNotFound

    if isinstance(exc, UserNotFound):
        raise HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, EmailAlreadyExists):
        raise HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, Forbidden):
        raise HTTPException(status_code=403, detail=str(exc))
    raise HTTPException(status_code=400, detail=str(exc))


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, repo: SQLUserRepository = Depends(get_repo)):
    try:
        user = _service(repo).register(payload.name, payload.email, payload.password)
        return _out(user)
    except DomainError as e:
        _handle(e)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return _out(current)


@router.get("", response_model=list[UserOut])
def list_users(
    skip: int = 0, limit: int = 100,
    current: User = Depends(require_admin), repo: SQLUserRepository = Depends(get_repo),
):
    try:
        return [_out(u) for u in _service(repo).list(current, skip, limit)]
    except DomainError as e:
        _handle(e)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, current: User = Depends(get_current_user),
             repo: SQLUserRepository = Depends(get_repo)):
    try:
        return _out(_service(repo).get(user_id, current))
    except DomainError as e:
        _handle(e)


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate,
                current: User = Depends(get_current_user),
                repo: SQLUserRepository = Depends(get_repo)):
    try:
        return _out(_service(repo).update(user_id, current, payload.name, payload.email))
    except DomainError as e:
        _handle(e)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/{user_id}/role", response_model=UserOut)
def set_role(user_id: int, payload: RoleUpdate,
             current: User = Depends(require_admin),
             repo: SQLUserRepository = Depends(get_repo)):
    try:
        return _out(_service(repo).change_role(user_id, current, payload.role))
    except DomainError as e:
        _handle(e)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current: User = Depends(get_current_user),
                repo: SQLUserRepository = Depends(get_repo)):
    try:
        _service(repo).remove(user_id, current)
    except DomainError as e:
        _handle(e)
