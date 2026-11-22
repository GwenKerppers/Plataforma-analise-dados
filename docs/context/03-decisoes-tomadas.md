# 03. Decisões tomadas

Registro cronológico resumido. Detalhes nos ADRs em `docs/decisions/`.

| # | Decisão | Motivo | Onde |
|---|---|---|---|
| 1 | Monólito modular; worker usa a imagem do backend | Domínio coeso, menos operação | ADR-001 |
| 2 | Access JWT 15 min em memória + refresh opaco em cookie HttpOnly, hash no banco, rotação com revogação de família; Argon2id | Reduz risco de XSS/roubo de token | ADR-002 |
| 3 | Datasets em Parquet no object storage; PostgreSQL só metadados; cada importação = versão imutável | Escala e reprodutibilidade | ADR-003 |
| 4 | Celery + Redis; `processing_tasks` como fonte de verdade; polling no frontend | Não bloquear HTTP | ADR-004 |
| 5 | OpenAPI → tipos TS gerados; erros RFC 9457 | Contrato único | ADR-005 |
| 6 | PyTorch e LangGraph adiados | Nenhum requisito atual os exige | ADR-006 |
| 7 | MinIO tornado opcional (profile `storage`); servidor S3 a escolher antes da Fase 2 | As imagens oficiais da MinIO foram removidas de Docker Hub/Quay (set/2026) e quebraram o `docker compose up` | ADR-007 |
| 8 | Licença MIT | Escolha padrão assumida ("pode seguir") | LICENSE |
| 9 | Renomeado de "DataMind" para "Plataforma de Análise de Dados" | Evitar nome que pareça gerado por IA; foco em portfólio | README |
| 10 | Entrega dos arquivos por zip; validação feita pela dona no PC dela | O Claude no chat não executa Docker/testes | 04 |
| 11 | Provedor de LLM não definido; decidir na Fase 6 | Sem requisito antes disso | 06 |

## Convenções
- Idioma de docs e commits: português. Commits no estilo `tipo: descrição` (ex.: `chore: ...`, `feat: ...`).
- Nomes técnicos padrão: usuário/banco/bucket `analise`.

## Questões em aberto
- Servidor S3 concreto (SeaweedFS, Garage ou outro mantido).
- Provedor de LLM.
- Suporte a `.xls` (xlrd é legado): suportar com limites e aviso, a confirmar na Fase 2.
- Renomear o repositório no GitHub.
