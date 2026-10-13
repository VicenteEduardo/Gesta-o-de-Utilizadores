"""Segurança: hash + JWT."""
from app.infrastructure.security import create_access_token, decode_token, hash_password, verify_password


def test_hash_e_verify():
    h = hash_password("password123")
    assert h != "password123"
    assert verify_password("password123", h) is True
    assert verify_password("outra", h) is False


def test_jwt_roundtrip():
    token = create_access_token("ana@mail.com")
    assert decode_token(token) == "ana@mail.com"
