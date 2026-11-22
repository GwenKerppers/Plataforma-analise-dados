# ADR-003: Armazenamento de datasets em Parquet via object storage

- Status: Proposto
- Data: 2026-11-22

## Contexto
Planilhas podem ter milhões de linhas; tabelas relacionais não são adequadas para isso e dificultam versionamento.

## Decisão
Arquivo original preservado e versão normalizada em Parquet em object storage compatível com S3 (servidor definido no ADR-007), atrás de uma interface de storage. PostgreSQL guarda apenas metadados, esquema, hash e referências. Cada importação cria uma `dataset_version` imutável.

## Consequências
Leitura colunar eficiente e reprodutibilidade por versão. Exige ciclo de vida explícito para exclusão de objetos e limpeza de importações não confirmadas.
