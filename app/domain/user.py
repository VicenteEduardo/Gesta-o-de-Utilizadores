"""Entidade de domínio pura: sem FastAPI, sem SQLAlchemy (DIP + SRP)."""
from dataclasses import dataclass
from typing import Optional

VALID_ROLES = ("admin", "user")


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    hashed_password: str
    role: str = "user"
    is_active: bool = True

    def __post_init__(self) -> None:
        self.email = self.email.strip().lower()
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres.")
        if "@" not in self.email:
            raise ValueError("Email inválido.")
        if self.role not in VALID_ROLES:
            raise ValueError(f"Role deve ser uma de {VALID_ROLES}.")

    def can_manage(self, other: "User") -> bool:
        """Regra de permissão: admin gere todos, user gere só a si."""
        return self.role == "admin" or self.id == other.id
