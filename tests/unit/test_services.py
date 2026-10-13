"""Casos de uso testados sem base de dados, contra um repositório em memória."""
import pytest

from app.application.auth_service import AuthService
from app.application.user_service import UserService
from app.domain.exceptions import EmailAlreadyExists, Forbidden, InvalidCredentials
from app.domain.user import User
from app.infrastructure.security import hash_password


class FakeRepo:
    """Guarda utilizadores num dicionário; implementa o essencial do contrato."""

    def __init__(self):
        self.data = {}
        self.seq = 1

    def create(self, user):
        user.id = self.seq
        self.seq += 1
        self.data[user.id] = user
        return user

    def get_by_id(self, user_id):
        return self.data.get(user_id)

    def get_by_email(self, email):
        wanted = email.strip().lower()
        return next((u for u in self.data.values() if u.email == wanted), None)

    def list_all(self, skip=0, limit=100):
        return list(self.data.values())[skip:skip + limit]

    def update(self, user):
        self.data[user.id] = user
        return user

    def delete(self, user_id):
        return self.data.pop(user_id, None) is not None


def make_admin(repo):
    return repo.create(
        User(
            id=None,
            name="Admin",
            email="admin@mail.com",
            hashed_password=hash_password("admin1234"),
            role="admin",
        )
    )


def test_register_ok_e_duplicado_falha():
    service = UserService(FakeRepo())
    user = service.register("Ana", "ana@mail.com", "password123")
    assert user.id == 1
    assert user.role == "user"
    with pytest.raises(EmailAlreadyExists):
        service.register("Outra", "ana@mail.com", "password123")


def test_register_password_curta_falha():
    with pytest.raises(ValueError):
        UserService(FakeRepo()).register("Ana", "ana@mail.com", "curta")


def test_login_ok_e_errada_falha():
    repo = FakeRepo()
    UserService(repo).register("Ana", "ana@mail.com", "password123")

    token = AuthService(repo).login("ana@mail.com", "password123")
    assert token.count(".") == 2  # um JWT tem três partes separadas por ponto

    with pytest.raises(InvalidCredentials):
        AuthService(repo).login("ana@mail.com", "password-errada")


def test_permissoes_list_e_role():
    repo = FakeRepo()
    service = UserService(repo)
    admin = make_admin(repo)
    ana = service.register("Ana", "ana@mail.com", "password123")

    with pytest.raises(Forbidden):
        service.list(ana)
    assert len(service.list(admin)) == 2

    with pytest.raises(Forbidden):
        service.change_role(ana.id, ana, "admin")
    assert service.change_role(ana.id, admin, "admin").role == "admin"
