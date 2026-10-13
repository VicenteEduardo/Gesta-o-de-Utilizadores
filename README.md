# API de Gestão de Utilizadores

API REST em Python (FastAPI) para registo de utilizadores, autenticação com JWT
e gestão de permissões por perfil (`admin` / `user`).

## Objectivo

Disponibilizar uma API REST de gestão de utilizadores — registo, autenticação
e controlo de acessos — construída como referência de boas práticas em Python:

**Âmbito funcional**

- CRUD completo de utilizadores, com validação de dados à entrada e respostas
  de erro consistentes (`401` credenciais/token, `403` sem permissão,
  `404` recurso inexistente, `409` email duplicado, `422` validação).
- Autenticação por JWT com expiração configurável.
- Modelo de permissões com dois perfis: `admin` gere qualquer conta,
  `user` gere apenas a própria.
- Persistência em SQLite por defeito, com suporte a PostgreSQL através da
  variável `DATABASE_URL`, sem alterações de código.

**Abordagem técnica**

- Arquitetura em quatro camadas (`domain` → `application` → `infrastructure`
  → `presentation`): as regras de negócio não dependem de frameworks nem da
  base de dados, o que as torna simples de testar e de evoluir.
- Desenvolvimento orientado por testes (TDD, ciclo Red → Green → Refactor),
  com testes unitários (`tests/unit`) e de integração sobre HTTP (`tests/integration`).
- Princípios SOLID aplicados na separação de responsabilidades, nas interfaces
  de persistência e na injecção de dependências (ver tabela abaixo).
- Entrega contentorizada com Docker (SQLite por defeito, PostgreSQL opcional
  via `docker compose --profile postgres up`).

**Definição de pronto**

`pytest` com todos os testes verdes, API executável via `uvicorn` e via
`docker compose`, com documentação interativa disponível em `/docs`.

## Arquitetura (DDD em 4 camadas)

```
app/
├── domain/          # Entidade User, IUserRepository (interface), exceções — zero dependências
├── application/     # UserService, AuthService — só dependem da interface (DIP)
├── infrastructure/  # SQLAlchemy, JWT, bcrypt — implementam a interface (LSP)
├── presentation/    # FastAPI routers, schemas Pydantic, dependencies
├── core/config.py   # Settings via env
└── main.py          # Wiring + error handlers
tests/
├── unit/            # Entidade, services (FakeRepo), security
└── integration/     # Fluxo HTTP real com SQLite em memória
```

## SOLID onde

| Princípio | Onde |
|---|---|
| SRP | `UserService` só regras · `security.py` só cripto · schemas só validação |
| OCP | Novo repo (ex. Postgres) = nova classe `IUserRepository`, sem tocar services |
| LSP | `SQLUserRepository` substituível por `FakeRepo` nos testes |
| ISP | `IUserRepository` por operação; `require_admin` separado de `get_current_user` |
| DIP | Services recebem `IUserRepository`, não `Session` |

## TDD (Red → Green → Refactor)

1. **Red:** `tests/unit/test_user_entity.py` falha antes da entidade existir.
2. **Green:** implementa `domain/user.py` até passar.
3. Repete para services (`FakeRepo`) e por fim integração (`test_api.py`).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## Correr

```bash
cp .env.example .env
uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

## Docker

```bash
docker compose up --build
```

PostgreSQL (opcional, via profile `postgres`):

```bash
DATABASE_URL=postgresql://app:app@db:5432/users docker compose --profile postgres up --build
```

## Endpoints

| Método | Rota | Acesso |
|---|---|---|
| POST | `/users` | público (cria sempre `role=user`) |
| POST | `/auth/login` | público → `{access_token}` |
| GET | `/users/me` | autenticado |
| GET | `/users` | admin |
| GET | `/users/{id}` | próprio ou admin |
| PUT | `/users/{id}` | próprio ou admin (nome/email) |
| PATCH | `/users/{id}/role` | admin (`admin`/`user`) |
| DELETE | `/users/{id}` | próprio ou admin |

Erros: `404` não encontrado · `409` email duplicado · `401` credenciais/token · `403` sem permissão · `422` validação.

## Exemplo

```bash
curl -X POST localhost:8000/users -H 'Content-Type: application/json' \
  -d '{"name":"Ana","email":"ana@mail.com","password":"password123"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"ana@mail.com","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl localhost:8000/users/me -H "Authorization: Bearer $TOKEN"
```
