# 06. Roadmap e backlog

MVP = Fases 1 + 2 + 3 (login, importação com versionamento, EDA).

| Fase | Escopo | Critérios de aceitação (resumo) |
|---|---|---|
| 0 | Arquitetura e ambiente | Docs prontos; `docker compose up` funcional |
| 1 | Auth, sessões, rotas protegidas, isolamento | Cadastro/login; refresh e revogação; rotas privadas protegidas; sem acesso a recurso alheio; testes críticos passando |
| 2 | Importação e dados | Upload CSV/XLSX/XLS; rejeita inválidos; assíncrono; preview antes de confirmar; Parquet; versionamento; falha não deixa dataset parcial |
| 3 | EDA | Estatísticas numéricas/categóricas, qualidade, correlações (Pearson/Spearman), outliers (IQR/Z-score); resultados ligados à versão do dataset; testes estatísticos |
| 4 | Visualizações | Construtor de gráficos, dashboards persistidos, filtros, exportação PNG/PDF, validação de compatibilidade de variáveis |
| 5 | Machine Learning | Pipelines scikit-learn sem vazamento; métricas corretas; comparação de experimentos; artefatos versionados; nunca carregar modelos enviados por usuários |
| 6 | Assistente de IA | Abstração de provedores; tool calling com schemas e autorização; sem execução livre de código; separa resultado/interpretação/hipótese; entrada de dados tratada como não confiável; limites de custo |
| 7 | Consolidação | Revisão, desempenho, auditoria de segurança, observabilidade, CI/CD completo, docs |

## Backlog (prioridade e dependência)
| # | Item | Depende de | Prio |
|---|---|---|---|
| 1 | Monorepo, Compose, `.env.example`, health checks | - | P0 (feito, não validado) |
| 2 | ADRs iniciais | - | P0 (feito) |
| 3 | Backend base: config, logging estruturado, Problem Details, request-id | 1 | P0 |
| 4 | Alembic + modelos de identidade | 3 | P0 |
| 5 | Auth completo, Argon2id, rotação, rate limit | 4 | P0 |
| 6 | Testes de auth e isolamento horizontal | 5 | P0 |
| 7 | Frontend base: rotas, layout, cliente API, tipos gerados, Error Boundary | 3 | P0 |
| 8 | Telas de cadastro/login + rotas protegidas | 5, 7 | P0 |
| 9 | CI completo | 6, 8 | P1 |
| 10 | Abstração de storage + escolha do servidor S3 (ADR-007) + worker + `processing_tasks` | 4 | P1 |
| 11 | Upload, validação (assinatura/MIME/limites), preview | 10 | P1 |
| 12 | Parquet, versionamento, hash, listagem | 11 | P1 |
| 13 | EDA | 12 | P1 |
| 14 | Visualizações e dashboards | 12 | P2 |
| 15 | ML | 12 | P2 |
| 16 | Assistente de IA | 13, 15 | P2 |
| 17 | Consolidação | todos | P3 |
