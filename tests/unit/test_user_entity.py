"""Testes unitários: entidade (primeiro passo do TDD: Red)."""
import pytest

from app.domain.user import User


def test_user_email_normalizado():
    u = User(id=1, name="Ana", email="ANA@Mail.com", hashed_password="x")
    assert u.email == "ana@mail.com"


def test_user_nome_curto_falha():
    with pytest.raises(ValueError):
        User(id=1, name="A", email="a@mail.com", hashed_password="x")


def test_user_role_invalida_falha():
    with pytest.raises(ValueError):
        User(id=1, name="Ana", email="a@mail.com", hashed_password="x", role="super")


def test_can_manage_admin_e_dono():
    admin = User(id=1, name="Admin", email="a@mail.com", hashed_password="x", role="admin")
    ana = User(id=2, name="Ana", email="ana@mail.com", hashed_password="x")
    bob = User(id=3, name="Bob", email="bob@mail.com", hashed_password="x")
    assert admin.can_manage(ana) is True
    assert ana.can_manage(ana) is True
    assert ana.can_manage(bob) is False
