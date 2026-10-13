"""Modelos SQLAlchemy (Infra). Separados da entidade de domínio (OCP)."""
from sqlalchemy import Boolean, Column, Integer, String

from app.infrastructure.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
