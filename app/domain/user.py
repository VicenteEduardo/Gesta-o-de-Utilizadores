"""Entidade central do sistema: um utilizador com perfil de acesso.

É uma classe simples, sem dependências de frameworks — as regras de
identidade e de permissão vivem aqui para não se espalharem pelo código.
"""
from dataclasses import dataclass
from typing import Optional

USER_ROLES = ("admin", "user")


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
        if len(self.name.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres.")
        if "@" not in self.email:
            raise ValueError("Email inválido.")
        if self.role not in USER_ROLES:
            raise ValueError(f"Perfil deve ser um de {USER_ROLES}.")

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def can_manage(self, other: "User") -> bool:
        """Um admin gere qualquer conta; um utilizador comum, só a própria."""
        return self.is_admin or self.id == other.id
