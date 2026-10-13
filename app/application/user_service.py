"""Casos de uso de utilizadores (Application). Depende só da interface (DIP)."""
from typing import List

from app.domain.exceptions import EmailAlreadyExists, Forbidden, UserNotFound
from app.domain.repository import IUserRepository
from app.domain.user import User
from app.infrastructure.security import hash_password


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    def register(self, name: str, email: str, password: str) -> User:
        if len(password) < 8:
            raise ValueError("Password deve ter pelo menos 8 caracteres.")
        if self.repo.get_by_email(email):
            raise EmailAlreadyExists("Email já registado.")
        user = User(id=None, name=name.strip(), email=email,
                    hashed_password=hash_password(password), role="user")
        return self.repo.create(user)

    def get(self, user_id: int, current: User) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("Utilizador não encontrado.")
        if not current.can_manage(user):
            raise Forbidden("Sem permissão.")
        return user

    def list(self, current: User, skip: int = 0, limit: int = 100) -> List[User]:
        if current.role != "admin":
            raise Forbidden("Apenas admins listam utilizadores.")
        return self.repo.list_all(skip, limit)

    def update(self, user_id: int, current: User, name: str = None, email: str = None) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("Utilizador não encontrado.")
        if not current.can_manage(user):
            raise Forbidden("Sem permissão.")
        if name is not None:
            if len(name.strip()) < 2:
                raise ValueError("Nome deve ter pelo menos 2 caracteres.")
            user.name = name.strip()
        if email is not None:
            other = self.repo.get_by_email(email)
            if other and other.id != user.id:
                raise EmailAlreadyExists("Email já registado.")
            user.email = email.strip().lower()
        return self.repo.update(user)

    def change_role(self, user_id: int, current: User, role: str) -> User:
        if current.role != "admin":
            raise Forbidden("Apenas admins gerem permissões.")
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("Utilizador não encontrado.")
        if role not in ("admin", "user"):
            raise ValueError("Role deve ser 'admin' ou 'user'.")
        user.role = role
        return self.repo.update(user)

    def remove(self, user_id: int, current: User) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("Utilizador não encontrado.")
        if not current.can_manage(user):
            raise Forbidden("Sem permissão.")
        self.repo.delete(user_id)
