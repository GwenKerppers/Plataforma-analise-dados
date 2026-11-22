# 02. Arquitetura e stack

## Estilo
**Monólito modular** (ADR-001). Três processos: frontend (SPA), backend (API FastAPI) e worker (Celery, **mesma imagem/código do backend**, comando diferente). Sem microsserviços.

## Componentes
Frontend React ⇄ API FastAPI → PostgreSQL (metadados), object storage S3-compatível (arquivos/Parquet), Redis (broker + cache) → Worker Celery. Adaptador de LLM opcional e substituível.

## Camadas por módulo (backend)
`api → services (aplicação) → domain ← repositories/adapters (infraestrutura)`.
O domínio não importa FastAPI, SQLAlchemy nem SDKs de LLM. Regras de negócio ficam no backend, nunca no frontend.

Estrutura interna sugerida de um módulo:
`api.py, schemas.py, services.py, repositories.py, models.py, domain.py, exceptions.py`.

## Stack
- Frontend: React 18, TypeScript, Vite. (Planejados: Tailwind, TanStack Query, React Router, React Hook Form, Zod, Recharts, Lucide.)
- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, Pytest, HTTPX.
- Dados/ML (planejado): Pandas, NumPy, SciPy, scikit-learn, PyArrow (Parquet).
- Infra: PostgreSQL 16, Redis 7, Celery, Docker Compose, GitHub Actions.
- **Adiados:** PyTorch e LangGraph (ADR-006). Servidor S3: a definir (ADR-007).

## Estrutura de pastas (real)
```
apps/backend/   app/{api/v1, core, infrastructure, modules}, tests/
apps/frontend/  src/
docs/           architecture/, decisions/, context/
.github/workflows/ci.yml
docker-compose.yml, .env.example, README.md, CLAUDE.md, LICENSE
```
Pastas de módulos futuros **não** são criadas vazias; nascem quando houver código.

## Princípios
KISS, YAGNI, SOLID proporcional, Secure by Design, API First. Não adicionar abstração ou dependência sem justificativa.
