"""Hash de passwords (bcrypt) e emissão/validação de tokens JWT."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    lifetime = expires_minutes if expires_minutes is not None else settings.jwt_expire_minutes
    payload = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=lifetime),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str:
    """Devolve o subject (email) ou levanta ValueError se o token for inválido."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Token inválido ou expirado.") from exc
    email = payload.get("sub")
    if not email:
        raise ValueError("Token inválido ou expirado.")
    return email
