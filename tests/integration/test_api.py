"""Integração: sobe a API em SQLite memória e testa o fluxo real (Green)."""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.infrastructure.models import UserModel  # noqa
from app.infrastructure.security import hash_password
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def seed_admin():
    db = TestingSession()
    if not db.query(UserModel).filter_by(email="admin@mail.com").first():
        db.add(UserModel(name="Admin", email="admin@mail.com",
                         hashed_password=hash_password("admin1234"), role="admin"))
        db.commit()
    db.close()


def auth(email, password):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_fluxo_completo():
    seed_admin()
    # 1. registar
    r = client.post("/users", json={"name": "Ana", "email": "ana@mail.com", "password": "password123"})
    assert r.status_code == 201, r.text
    ana_id = r.json()["id"]
    # 2. duplicado -> 409
    r = client.post("/users", json={"name": "Ana", "email": "ana@mail.com", "password": "password123"})
    assert r.status_code == 409
    # 3. validação -> 422
    r = client.post("/users", json={"name": "A", "email": "bad", "password": "curta"})
    assert r.status_code == 422
    # 4. login + me
    h = auth("ana@mail.com", "password123")
    r = client.get("/users/me", headers=h)
    assert r.status_code == 200 and r.json()["email"] == "ana@mail.com"
    # 5. user comum não lista -> 403
    assert client.get("/users", headers=h).status_code == 403
    # 6. admin lista
    ha = auth("admin@mail.com", "admin1234")
    r = client.get("/users", headers=ha)
    assert r.status_code == 200 and len(r.json()) >= 2
    # 7. atualizar próprio nome
    r = client.put(f"/users/{ana_id}", json={"name": "Ana Silva"}, headers=h)
    assert r.status_code == 200 and r.json()["name"] == "Ana Silva"
    # 8. promover a admin
    r = client.patch(f"/users/{ana_id}/role", json={"role": "admin"}, headers=ha)
    assert r.status_code == 200 and r.json()["role"] == "admin"
    # 9. eliminar
    r = client.delete(f"/users/{ana_id}", headers=ha)
    assert r.status_code == 204
    assert client.get(f"/users/{ana_id}", headers=ha).status_code == 404


def test_login_invalido_401():
    r = client.post("/auth/login", json={"email": "no@mail.com", "password": "xpto12345"})
    assert r.status_code == 401
