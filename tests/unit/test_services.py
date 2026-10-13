"""Testes unitários dos services com Fake repo (TDD sem BD)."""
import pytest

from app.application.auth_service import AuthService
from app.application.user_service import UserService
from app.domain.exceptions import EmailAlreadyExists, Forbidden
from app.domain.user import User
from app.infrastructure.security import hash_password


class FakeRepo:
    def __init__(self):
        self.data = {}
        self.seq = 1

    def create(self, user):
        user.id = self.seq
        self.seq += 1
        self.data[user.id] = user
        return user

    def get_by_id(self, uid):
        return self.data.get(uid)

    def get_by_email(self, email):
        email = email.strip().lower()
        return next((u for u in self.data.values() if u.email == email), None)

    def list_all(self, skip=0, limit=100):
        return list(self.data.values())[skip:skip + limit]

    def update(self, user):
        self.data[user.id] = user
        return user

    def delete(self, uid):
        return self.data.pop(uid, None) is not None


def make_admin(repo):
    admin = User(id=None, name="Admin", email="admin@mail.com",
                 hashed_password=hash_password("admin1234"), role="admin")
    return repo.create(admin)


def test_register_ok_e_duplicado_falha():
    repo, svc = FakeRepo(), None
    svc = UserService(repo)
    u = svc.register("Ana", "ana@mail.com", "password123")
    assert u.id == 1 and u.role == "user"
    with pytest.raises(EmailAlreadyExists):
        svc.register("Outra", "ana@mail.com", "password123")


def test_register_password_curta_falha():
    with pytest.raises(ValueError):
        UserService(FakeRepo()).register("Ana", "ana@mail.com", "curta")


def test_login_ok_e_errada_falha():
    from app.domain.exceptions import InvalidCredentials
    repo = FakeRepo()
    UserService(repo).register("Ana", "ana@mail.com", "password123")
    token = AuthService(repo).login("ana@mail.com", "password123")
    assert token.count(".") == 2  # JWT tem 3 partes
    with pytest.raises(InvalidCredentials):
        AuthService(repo).login("ana@mail.com", "errada999")


def test_permissoes_list_e_role():
    repo = FakeRepo()
    svc = UserService(repo)
    admin = make_admin(repo)
    ana = svc.register("Ana", "ana@mail.com", "password123")
    # user comum não lista
    with pytest.raises(Forbidden):
        svc.list(ana)
    assert len(svc.list(admin)) == 2
    # user comum não muda role
    with pytest.raises(Forbidden):
        svc.change_role(ana.id, ana, "admin")
    promoted = svc.change_role(ana.id, admin, "admin")
    assert promoted.role == "admin"
