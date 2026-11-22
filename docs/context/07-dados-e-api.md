# 07. Dados e API

## Modelo de dados (domínios)
- Identidade: users, user_sessions, password_reset_tokens
- Dados: datasets, dataset_versions, dataset_columns, dataset_importations
- Análises: analyses, analysis_results, visualizations, dashboards, dashboard_items
- ML: ml_experiments, ml_models, ml_model_artifacts
- IA: ai_conversations, ai_messages, ai_tool_executions, ai_usage_records
- Infra: processing_tasks, audit_logs

Diagrama ER em `docs/architecture/overview.md`.

## Convenções
- PK UUID; `created_at`/`updated_at` em tudo; `owner_id` (FK users) em todo recurso de usuário.
- `datasets` = identidade lógica; `dataset_versions` = dado imutável. Análises, visualizações e experimentos referenciam `dataset_version_id`.
- `dataset_versions` guarda chaves de storage (original e parquet), `file_hash_sha256`, contagens, tamanho, status, esquema. Único `(dataset_id, version_number)`.
- Importação com preview exige estado intermediário `PENDING_CONFIRMATION` (com expiração e limpeza).
- `processing_tasks`: estados PENDING, QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED; `idempotency_key` único por usuário; `attempts`; `error_code`.
- `user_sessions`: apenas hash do refresh token, `family_id`, `revoked_at`.
- Linhas de planilha nunca no PostgreSQL.
- Exclusão: CASCADE só dentro do mesmo agregado; objetos do storage removidos por serviço explícito e auditado.

## API
- Prefixo `/api/v1`; OpenAPI do FastAPI; tipos TS gerados e verificados no CI.
- Erros RFC 9457 (`application/problem+json`), sem stack trace, com `request_id`.
- Paginação: `page, page_size, sort, order` → `{items, total, page, page_size}`.
- Tarefas longas: `202` + `task_id`; polling em `GET /tasks/{task_id}`; cabeçalho `Idempotency-Key`.
- Recurso de outro usuário responde **404**, não 403.

## Rotas planejadas
Auth: `POST /auth/register|login|refresh|logout`; Usuário: `GET/PATCH /users/me`, `GET/DELETE /users/me/sessions[/{id}]`.
Dados: `/datasets`, `/datasets/{id}`, `/datasets/{id}/preview`, `/datasets/{id}/versions`.
Demais: `/analytics`, `/visualizations`, `/dashboards`, `/ml/experiments`, `/ai/conversations[/{id}/messages]`, `/tasks/{id}`.

## Implementado hoje
Apenas `GET /api/v1/health`.
