# Plataforma de Análise de Dados

Projeto de estudo e portfólio: uma aplicação web para importar conjuntos de dados, analisá-los estatisticamente, visualizá-los, treinar modelos de Machine Learning e consultá-los em linguagem natural.

O objetivo é praticar e demonstrar engenharia de software aplicada a dados: arquitetura modular, processamento assíncrono, segurança, testes e documentação de decisões.

## Status

Desenvolvimento incremental por fases. O que está de fato pronto aparece marcado.

| Fase | Escopo | Status |
|---|---|---|
| 0 | Arquitetura, ambiente e documentação inicial | Em validação |
| 1 | Autenticação e isolamento de usuários | Em andamento (etapas 1.1 a 1.3 validadas por testes; 1.4 escrita, ainda não validada) |
| 2 | Importação de arquivos e versionamento de datasets | Planejada |
| 3 | Análise exploratória (estatísticas, qualidade, correlação) | Planejada |
| 4 | Visualizações e dashboards | Planejada |
| 5 | Machine Learning | Planejada |
| 6 | Assistente com IA (ferramentas controladas) | Planejada |
| 7 | Consolidação, segurança e observabilidade | Planejada |

## Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Dados e ML (previstos):** Pandas, NumPy, SciPy, scikit-learn, Parquet
- **Infraestrutura:** PostgreSQL, Redis, Celery, armazenamento S3-compatível (a definir, ADR-007), Docker Compose, GitHub Actions

A escolha do monólito modular, do armazenamento em Parquet, da autenticação e das dependências adiadas está justificada nos ADRs.

## Decisões de arquitetura

- [Contexto do projeto (índice)](docs/context/README.md)
- [Visão de arquitetura](docs/architecture/overview.md)
- [ADR-001 Monólito modular](docs/decisions/001-monolito-modular.md)
- [ADR-002 Autenticação e isolamento](docs/decisions/002-autenticacao.md)
- [ADR-003 Datasets em Parquet](docs/decisions/003-armazenamento-parquet.md)
- [ADR-004 Processamento assíncrono](docs/decisions/004-processamento-assincrono.md)
- [ADR-005 Contratos de API](docs/decisions/005-contratos-api.md)
- [ADR-006 Dependências adiadas](docs/decisions/006-dependencias-adiadas.md)
- [ADR-007 Backend de armazenamento S3 (em aberto)](docs/decisions/007-backend-s3.md)
- [ADR-008 Modelo de usuários e sessões](docs/decisions/008-modelo-de-sessoes.md)
- [ADR-009 Fluxo de autenticação](docs/decisions/009-fluxo-de-autenticacao.md)
- [ADR-010 Rate limiting e sessões](docs/decisions/010-rate-limiting.md)

## Executar localmente

Requisitos: Docker e Docker Compose.

```bash
cp .env.example .env     # ajuste as senhas locais
docker compose up --build
```

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API / OpenAPI | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |

## Testes (backend)

Pelo Docker (não exige Python instalado):

```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend pytest
```

## Problemas encontrados na validação da Fase 0

Ao executar o ambiente pela primeira vez, apareceram três problemas. Ficam registrados porque mostram o que só se descobre rodando o projeto:

| Problema | Causa | Correção |
|---|---|---|
| `docker compose up` falhava com `pull access denied for minio/minio` | A MinIO removeu suas imagens públicas (Docker Hub e Quay) em setembro de 2026 | MinIO passou a ser opcional (profile `storage`); o servidor S3 será escolhido antes da Fase 2 ([ADR-007](docs/decisions/007-backend-s3.md)) |
| Worker Celery reiniciava com `VersionMismatch` | O `kombu`, dependência transitiva do Celery, exigiu `redis-py` >= 6.1.0 e o projeto fixava 5.1.1 | `redis` atualizado para 6.1.0. Dependências transitivas ainda não estão travadas: um lockfile será gerado na Fase 1 |
| Frontend mostrava "API: error" apesar de a API responder | Faltava CORS: o navegador bloqueava a chamada de `localhost:5173` para `localhost:8000` | `CORSMiddleware` no backend, com origens configuráveis (`cors_origins`) |

## Limitações conhecidas

- Projeto em construção: apenas o esqueleto da Fase 0 existe.
- Dependências diretas fixadas, mas as transitivas não (lockfile planejado). Versões a revisar antes de qualquer uso além do estudo.
- Segurança de IA, limites de processamento e testes de desempenho serão documentados quando os módulos correspondentes existirem.

## Licença

MIT
