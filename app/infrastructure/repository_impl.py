"""Implementação SQLAlchemy do IUserRepository (LSP: substituível pela interface)."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.repository import IUserRepository
from app.domain.user import User
from app.infrastructure.models import UserModel


def _to_entity(m: UserModel) -> User:
    return User(
        id=m.id, name=m.name, email=m.email,
        hashed_password=m.hashed_password, role=m.role, is_active=m.is_active,
    )


class SQLUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        model = UserModel(
            name=user.name, email=user.email.lower(),
            hashed_password=user.hashed_password, role=user.role, is_active=user.is_active,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_entity(model)

    def get_by_id(self, user_id: int) -> Optional[User]:
        m = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return _to_entity(m) if m else None

    def get_by_email(self, email: str) -> Optional[User]:
        m = self.db.query(UserModel).filter(UserModel.email == email.strip().lower()).first()
        return _to_entity(m) if m else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        rows = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [_to_entity(m) for m in rows]

    def update(self, user: User) -> User:
        m = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        assert m is not None
        m.name = user.name
        m.email = user.email.lower()
        m.hashed_password = user.hashed_password
        m.role = user.role
        m.is_active = user.is_active
        self.db.commit()
        self.db.refresh(m)
        return _to_entity(m)

    def delete(self, user_id: int) -> bool:
        m = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not m:
            return False
        self.db.delete(m)
        self.db.commit()
        return True
