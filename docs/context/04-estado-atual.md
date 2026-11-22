# 04. Estado atual

> **Atualize este arquivo ao final de cada tarefa.** Última atualização: 2026-11-22.

## Fase atual
**Fase 0: arquitetura e ambiente.** Status: **em validação** (não concluída).

## Existe (gerado, mas NÃO verificado por execução)
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
