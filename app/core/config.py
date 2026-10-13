"""Configuração da aplicação lida de variáveis de ambiente (ver `.env.example`)."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "API de Gestão de Utilizadores"
    app_version: str = "1.0.0"
    database_url: str = Field(default="sqlite:///./users.db")
    jwt_secret: str = Field(default="dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


settings = Settings()
