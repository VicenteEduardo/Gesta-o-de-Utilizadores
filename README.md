# API de Gestão de Utilizadores

API REST em Python (FastAPI) para registo de utilizadores, autenticação com JWT
e gestão de permissões por perfil (`admin` / `user`).

## Objectivo do Projecto

Construir uma API REST para **registar utilizadores, autenticar contas com JWT e gerir
permissões**, servindo como projecto de aprendizagem de boas práticas em Python:

- **Funcional:** CRUD completo de utilizadores, login com JWT, dois perfis
  (`admin` gere todos; `user` gere só a si), validação de dados e erros HTTP
  consistentes (`401/403/404/409/422`), com SQLite por defeito e PostgreSQL via `DATABASE_URL`.
- **Técnico:** aplicar **DDD em 4 camadas** (`domain` → `application` →
  `infrastructure` → `presentation`), desenvolver com **TDD** (Red → Green →
  Refactor, `tests/unit` + `tests/integration`) e respeitar os 5 princípios
  **SOLID** (ver tabela abaixo), com entrega contentorizada em **Docker**.
- **Critério de sucesso:** `pytest` com todos os testes verdes, API a correr via
  `uvicorn` e via `docker compose up`, documentada em `/docs`.

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
pytest -v            # ~13 testes
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

PostgreSQL: descomentar o bloco `db` no `docker-compose.yml` e usar
`DATABASE_URL=postgresql://app:app@db:5432/users`.

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
