"""Exceções de domínio (tratamento de erros uniforme)."""


class DomainError(Exception):
    pass


class UserNotFound(DomainError):
    pass


class EmailAlreadyExists(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class Forbidden(DomainError):
    pass
