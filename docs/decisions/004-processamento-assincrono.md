# ADR-004: Processamento assíncrono com Celery e Redis

- Status: Proposto
- Data: 2026-11-22

## Contexto
Importação, EDA e treinamento são longos e não podem bloquear requisições HTTP.

## Decisão
Celery com Redis como broker. Tabela `processing_tasks` como fonte de verdade do estado (PENDING, QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED), com chave de idempotência por usuário, retentativas limitadas e `acks_late`. Frontend acompanha por polling.

## Consequências
Resiliência a falhas de worker e sem conexões longas. Exige tarefas idempotentes e monitoramento de filas.
