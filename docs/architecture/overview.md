# Visão de arquitetura

## Estilo
Monólito modular com três processos: frontend (SPA), backend (API FastAPI) e worker (Celery, mesmo código do backend). Ver ADR-001.

## Componentes
```mermaid
flowchart LR
    U[Usuário] --> FE[Frontend React/Vite]
    FE -->|REST /api/v1| API[Backend FastAPI]
    API --> PG[(PostgreSQL)]
    API --> OBJ[(MinIO / S3)]
    API -->|enfileira| RD[(Redis)]
    RD --> WK[Worker Celery]
    WK --> PG
    WK --> OBJ
    API --> LLMA[Adaptador LLM]
    LLMA -.->|externo, opcional| LLM[Provedor LLM]
```

## Camadas por módulo
`api → services (aplicação) → domain ← repositories/adapters (infraestrutura)`.
O domínio não importa FastAPI, SQLAlchemy nem SDKs de LLM.

## Modelo de dados inicial
```mermaid
erDiagram
    users ||--o{ user_sessions : has
    users ||--o{ password_reset_tokens : has
    users ||--o{ datasets : owns
    datasets ||--o{ dataset_versions : has
    dataset_versions ||--o{ dataset_columns : describes
    dataset_versions ||--|| dataset_importations : created_by
    dataset_versions ||--o{ analyses : analyzed_by
    analyses ||--o{ analysis_results : produces
    dataset_versions ||--o{ visualizations : feeds
    users ||--o{ dashboards : owns
    dashboards ||--o{ dashboard_items : contains
    visualizations ||--o{ dashboard_items : placed_in
    dataset_versions ||--o{ ml_experiments : trains_on
    ml_experiments ||--o{ ml_models : yields
    ml_models ||--o{ ml_model_artifacts : stores
    users ||--o{ ai_conversations : owns
    ai_conversations ||--o{ ai_messages : has
    ai_messages ||--o{ ai_tool_executions : triggers
    users ||--o{ ai_usage_records : consumes
    users ||--o{ processing_tasks : requests
    users ||--o{ audit_logs : generates
```

Convenções: PK UUID; `created_at`/`updated_at` em todas as tabelas; `owner_id` em todo recurso de usuário. Linhas de planilha ficam em Parquet no object storage, nunca no PostgreSQL. Análises, visualizações e experimentos referenciam sempre `dataset_version_id`.

## Contratos da API
- Prefixo `/api/v1`; tipos TypeScript gerados do OpenAPI (ADR-005).
- Erros em RFC 9457 (`application/problem+json`), sem stack trace.
- Paginação: `page`, `page_size`, `sort`, `order` → `{items, total, page, page_size}`.
- Tarefas longas: `202 Accepted` + `task_id`; polling em `GET /tasks/{task_id}`; `Idempotency-Key` na criação.

## Fronteiras de confiança
Conteúdo de datasets é entrada não confiável (inclusive para o LLM). O LLM nunca executa SQL, Python ou comandos; só ferramentas validadas, que recebem `owner_id` do servidor.
