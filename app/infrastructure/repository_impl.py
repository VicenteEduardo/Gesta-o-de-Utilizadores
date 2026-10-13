"""Adaptador SQLAlchemy de persistência de utilizadores."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.exceptions import UserNotFound
from app.domain.repository import IUserRepository
from app.domain.user import User
from app.infrastructure.models import UserModel


def to_entity(row: UserModel) -> User:
    return User(
        id=row.id,
        name=row.name,
        email=row.email,
        hashed_password=row.hashed_password,
        role=row.role,
        is_active=row.is_active,
    )


class SQLUserRepository(IUserRepository):
    """Implementação concreta de IUserRepository sobre SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        row = UserModel(
            name=user.name,
            email=user.email.lower(),
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return to_entity(row)

    def get_by_id(self, user_id: int) -> Optional[User]:
        row = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return to_entity(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        row = (
            self.db.query(UserModel)
            .filter(UserModel.email == email.strip().lower())
            .first()
        )
        return to_entity(row) if row else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        rows = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [to_entity(row) for row in rows]

    def update(self, user: User) -> User:
        row = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if row is None:
            raise UserNotFound("Utilizador não encontrado.")
        row.name = user.name
        row.email = user.email.lower()
        row.hashed_password = user.hashed_password
        row.role = user.role
        row.is_active = user.is_active
        self.db.commit()
        self.db.refresh(row)
        return to_entity(row)

    def delete(self, user_id: int) -> bool:
        row = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if row is None:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
