# 04. Estado atual

> **Atualize este arquivo ao final de cada tarefa.** Última atualização: 2026-11-22.

## Fase atual
**Fase 0: arquitetura e ambiente.** Status: **em validação** (não concluída).

## Validação das etapas 1.1 a 1.3 (confirmada por execução)
Na máquina da dona do projeto: `docker compose run --rm backend pytest` = **42 passed**; `ruff check .` = All checks passed; `alembic upgrade head` sem erro. Dockerfile ajustado (chown de /srv) para ruff/pytest funcionarem como usuário não-root. Commit das etapas 1.1 a 1.3 feito pela dona do projeto (confirmar o hash do push quando informado). Não conferidos ainda: `/api/v1/health/ready` no navegador e o frontend ("API: ok").

**Etapa 1.4: escrita, NÃO validada.** Rate limiting no Redis (`core/rate_limit.py`, config em `Settings`), endpoints `GET /users/me/sessions`, `DELETE /users/me/sessions/{id}`, `DELETE /users/me/sessions`, e testes: `test_rate_limit.py` (limitador com Redis real + endpoints com limites baixos), `test_isolation.py` (dois usuários: não leem nem revogam sessões um do outro; 404 idêntico para sessão alheia e inexistente). CI agora tem serviço Redis. ADR-010. Validar com `docker compose run --rm backend pytest` (contagem estática: 62 testes = 42 anteriores + 8 de rate limit + 12 de isolamento; vale o número que o pytest reportar).

### Histórico: primeira execução de testes (etapas 1.1 a 1.3)
`docker compose run --rm backend pytest`: **39 passaram, 1 falhou** (40 coletados). A falha era um bug do próprio teste (`test_invalid_request_id_is_replaced` usava acentos em cabeçalho HTTP, que o httpx não aceita); corrigido com valores ASCII parametrizados. Confirmado por execução: autenticação (16 testes), esquema e migração 0001 sem drift (8), segurança (8). `ruff check` ainda não confirmado (falhou antes por permissão do cache; Dockerfile corrigido). Ainda não conferidos: `/api/v1/health/ready`, `alembic upgrade head` no banco real e o frontend.

## Fase 1 (em andamento)
Etapas: 1.1 base do backend, 1.2 modelos de identidade + migração, 1.3 endpoints de auth, 1.4 rate limit e testes de isolamento, 1.5 frontend base, 1.6 telas de login/cadastro, 1.7 CI e lockfiles. Reset de senha por e-mail fica no fim da Fase 1, com envio **somente de desenvolvimento** (grava o link no log), identificado como tal.

**Etapa 1.1: escrita, NÃO validada.** Contém: logging JSON com request_id (`core/logging.py`), middleware de request-id (`core/middleware.py`), erros de domínio + Problem Details RFC 9457 (`core/errors.py`), sessão SQLAlchemy e `Base` com naming convention (`infrastructure/database.py`), `GET /api/v1/health/ready` (checa banco e Redis, 503 se falhar), Alembic configurado (sem migrações ainda), 7 testes em `tests/test_core.py` (não dependem de banco). Sem novas dependências. Validar com: `docker compose run --rm backend pytest` e `ruff check .`; testar também `/api/v1/health/ready` e `docker compose run --rm backend alembic current`.

**Etapa 1.2: escrita, NÃO validada.** Modelos `User` (`modules/users/models.py`) e `UserSession` (`modules/authentication/models.py`), registro em `modules/models_registry.py`, migração `0001` escrita à mão (sem rodar o autogenerate), `tests/conftest.py` (cria o banco `<nome>_test` e aplica as migrações) e `tests/test_identity_models.py` (7 testes de banco, incluindo um que compara modelos x migração). Decisões: sem relationship ORM entre módulos; cascade de sessões no banco; e-mail em minúsculas garantido por CHECK; ids UUID v4 (UUID v7 não existe na stdlib do Python 3.12). Validar com: `docker compose run --rm backend alembic upgrade head` e `docker compose run --rm backend pytest`.

**Etapa 1.2: escrita, NÃO validada.** Modelos `User` (`modules/users/models.py`) e `UserSession` (`modules/authentication/models.py`), `TimestampMixin`, registro central de modelos (`infrastructure/model_registry.py`, usar também no Alembic), migração `0001_users_and_user_sessions`, fixtures de banco (`tests/conftest.py`: cria banco `<nome>_test`, aplica migrações) e 8 testes em `tests/test_identity_schema.py` (inclui teste de drift migração x modelos, unicidade, check de e-mail minúsculo, cascade, consistência de revogação). CI agora sobe PostgreSQL. ADR-008 registra o modelo. **Atenção ao aplicar:** durante a montagem apareceram arquivos de um rascunho anterior conflitante (outra migração 0001, `models_registry.py`, `test_identity_models.py`); foram removidos. Se algum deles existir na sua pasta, apague: duas migrações `0001` quebram o Alembic. Validar com `docker compose run --rm backend pytest` e `... alembic upgrade head`.

**Etapa 1.3: escrita, NÃO validada (depende de 1.1 e 1.2 passarem).** Endpoints `POST /auth/register|login|refresh|logout` e `GET /users/me`. Código em `modules/authentication/{security,schemas,repositories,services,dependencies,api}.py` e `modules/users/{schemas,repositories,api}.py`. Novas dependências: argon2-cffi 23.1.0, PyJWT 2.9.0, email-validator 2.2.0. **`JWT_SECRET` agora é obrigatório** (mín. 32 caracteres; `.env.example` já tem a variável, então um `.env` copiado dele funciona). Testes: `tests/test_security.py` (sem banco) e `tests/test_auth.py` (integração, usa o banco `<nome>_test`). Detalhes e trade-offs no ADR-009. Pendente: rate limiting, sessões (listar/revogar), `PATCH /users/me`, recuperação de senha.

## Existe da Fase 0 (gerado; parte validada, ver tabela)
- Esqueleto do monorepo, docker-compose (db, redis, backend, worker, frontend; minio opcional), CI (ruff, pytest, typecheck, build).
- Backend: FastAPI com `GET /api/v1/health`, config (pydantic-settings), app Celery, 1 teste (`test_health.py`).
- Frontend: Vite + React + TS mínimo que consulta o health.
- Docs: README, visão de arquitetura, ADRs 001-007, esta pasta de contexto.

## Validação
| Item | Resultado |
|---|---|
| `docker compose up --build` | **Em andamento** na máquina da dona do projeto (Windows, Docker Desktop). Primeiro build lento. Falha anterior causada pela imagem do MinIO (já corrigida no compose; ela precisa usar o arquivo novo) |
| `GET /api/v1/health` = ok | **Confirmado** nos logs do backend (200 OK) |
| Frontend em :5173 mostra "API: ok" | Não confirmado |
| `pytest` / `ruff` | Não executado |
| `npm run typecheck` / `build` | Não executado |
| Push para o GitHub | **Não feito**. O repositório remoto está vazio |

## Problemas encontrados na validação
- Worker falhou: `kombu` (dependência transitiva do Celery) exigiu redis-py >= 6.1.0 e o projeto fixava 5.1.1. Corrigido para `redis==6.1.0` (a confirmar após rebuild). Lição: dependências transitivas não estão fixadas; gerar lockfile.

- Frontend mostrou "API: error": faltava CORS no backend. Adicionado `CORSMiddleware` (origens em `cors_origins`, config.py). A confirmar após rebuild.
- Os três problemas (MinIO, redis/kombu, CORS) estão registrados no README.

## Pendências imediatas
1. Concluir e confirmar a validação local acima.
2. Primeiro commit/push ao GitHub (verificar que `.env` não aparece no `git status`).
3. Gerar lockfiles (`package-lock.json`; Python a definir).
4. Fixar versões de dependências revisadas (as atuais são de 2024 e podem estar defasadas).

## Riscos / limitações conhecidas
- Todo o código foi escrito sem execução automatizada no ambiente do Claude.
- Sem bucket/servidor S3 até o ADR-007 ser resolvido (necessário só na Fase 2).
- Sem readiness check de dependências no `/health` (previsto na Fase 1).

## Próxima etapa
Fase 1: Alembic, modelos de identidade, registro/login/refresh/logout, testes de isolamento. Só iniciar após a Fase 0 validada.
