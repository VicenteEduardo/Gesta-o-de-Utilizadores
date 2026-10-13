"""Erros de negócio. A camada HTTP traduz cada um no status adequado."""


class DomainError(Exception):
    """Base para todos os erros de negócio."""


class UserNotFound(DomainError):
    pass


class EmailAlreadyExists(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class Forbidden(DomainError):
    pass
