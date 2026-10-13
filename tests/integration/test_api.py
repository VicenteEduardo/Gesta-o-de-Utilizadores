"""Testes de integração: exercem a API real sobre SQLite em memória.

Cada teste recebe uma BD isolada (fixture `client`), por isso não há
dependência de ordem nem estado partilhado entre testes.
"""
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.infrastructure.models import UserModel  # noqa: F401 — regista a tabela
from app.infrastructure.security import hash_password
from app.main import app

ADMIN_EMAIL = "admin@mail.com"
ADMIN_PASSWORD = "admin1234"


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()
    db.add(
        UserModel(
            name="Admin",
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            role="admin",
        )
    )
    db.commit()
    db.close()

    def override_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def login(client: TestClient, email: str, password: str) -> Dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def register(client: TestClient, name="Ana", email="ana@mail.com", password="password123") -> dict:
    response = client.post(
        "/users", json={"name": name, "email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_register_and_login_flow(client):
    user = register(client)
    headers = login(client, "ana@mail.com", "password123")

    profile = client.get("/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["id"] == user["id"]
    assert profile.json()["role"] == "user"


def test_register_duplicate_email_returns_409(client):
    register(client)
    response = client.post(
        "/users", json={"name": "Outra", "email": "ana@mail.com", "password": "password123"}
    )
    assert response.status_code == 409


def test_register_invalid_payload_returns_422(client):
    response = client.post(
        "/users", json={"name": "A", "email": "not-an-email", "password": "curta"}
    )
    assert response.status_code == 422


def test_login_with_wrong_password_returns_401(client):
    register(client)
    response = client.post(
        "/auth/login", json={"email": "ana@mail.com", "password": "password-errada"}
    )
    assert response.status_code == 401


def test_regular_user_cannot_list_users(client):
    register(client)
    headers = login(client, "ana@mail.com", "password123")
    assert client.get("/users", headers=headers).status_code == 403


def test_admin_lists_users(client):
    register(client)
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)

    response = client.get("/users", headers=admin)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_user_updates_own_profile(client):
    user = register(client)
    headers = login(client, "ana@mail.com", "password123")

    response = client.put(f"/users/{user['id']}", json={"name": "Ana Silva"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Ana Silva"


def test_admin_promotes_user_to_admin(client):
    user = register(client)
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)

    response = client.patch(
        f"/users/{user['id']}/role", json={"role": "admin"}, headers=admin
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_admin_deletes_user(client):
    user = register(client)
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)

    assert client.delete(f"/users/{user['id']}", headers=admin).status_code == 204
    assert client.get(f"/users/{user['id']}", headers=admin).status_code == 404


def test_unauthenticated_request_returns_401(client):
    assert client.get("/users/me").status_code == 401
