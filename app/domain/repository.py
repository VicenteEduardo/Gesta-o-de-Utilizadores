"""Contrato de persistência de utilizadores.

Os casos de uso programam contra esta interface; a implementação concreta
(SQLAlchemy, memória, etc.) é injectada de fora.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.user import User


class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        raise NotImplementedError
