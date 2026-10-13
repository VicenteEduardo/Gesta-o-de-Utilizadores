"""Valida credenciais e emite o token de acesso."""
from app.domain.exceptions import InvalidCredentials
from app.domain.repository import IUserRepository
from app.infrastructure.security import create_access_token, verify_password


class AuthService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentials("Credenciais inválidas.")
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials("Credenciais inválidas.")
        return create_access_token(subject=user.email)
