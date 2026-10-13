"""Regras de negócio da gestão de utilizadores.

Esta camada só conhece a interface IUserRepository — nunca o SQLAlchemy —
por isso pode ser testada com um repositório em memória.
"""
from typing import List, Optional

from app.domain.exceptions import EmailAlreadyExists, Forbidden, UserNotFound
from app.domain.repository import IUserRepository
from app.domain.user import User
from app.infrastructure.security import hash_password

MIN_PASSWORD_LENGTH = 8


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    def register(self, name: str, email: str, password: str) -> User:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."
            )
        if self.repo.get_by_email(email):
            raise EmailAlreadyExists("Email já registado.")
        return self.repo.create(
            User(
                id=None,
                name=name.strip(),
                email=email,
                hashed_password=hash_password(password),
                role="user",
            )
        )

    def get(self, user_id: int, current: User) -> User:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound("Utilizador não encontrado.")
        if not current.can_manage(user):
            raise Forbidden("Sem permissão para ver este utilizador.")
        return user

    def list(self, current: User, skip: int = 0, limit: int = 100) -> List[User]:
        if current.role != "admin":
            raise Forbidden("Apenas administradores listam utilizadores.")
        return self.repo.list_all(skip, limit)

    def update(
        self,
        user_id: int,
        current: User,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> User:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound("Utilizador não encontrado.")
        if not current.can_manage(user):
            raise Forbidden("Sem permissão para editar este utilizador.")
        if name is not None:
            if len(name.strip()) < 2:
                raise ValueError("Nome deve ter pelo menos 2 caracteres.")
            user.name = name.strip()
        if email is not None:
            taken_by = self.repo.get_by_email(email)
            if taken_by is not None and taken_by.id != user.id:
                raise EmailAlreadyExists("Email já registado.")
            user.email = email.strip().lower()
        return self.repo.update(user)

    def change_role(self, user_id: int, current: User, role: str) -> User:
        if current.role != "admin":
            raise Forbidden("Apenas administradores gerem permissões.")
        if role not in ("admin", "user"):
            raise ValueError("Perfil deve ser 'admin' ou 'user'.")
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound("Utilizador não encontrado.")
        user.role = role
        return self.repo.update(user)

    def remove(self, user_id: int, current: User) -> None:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound("Utilizador não encontrado.")
        if not current.can_manage(user):
            raise Forbidden("Sem permissão para eliminar este utilizador.")
        self.repo.delete(user_id)
