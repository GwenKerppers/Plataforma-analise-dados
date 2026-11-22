# Índice do contexto do projeto

Estes arquivos existem para que o Claude (ou qualquer pessoa) retome o projeto sem depender do histórico de conversas. **Leia na ordem abaixo; o 04 é o mais importante e deve ser mantido atualizado.**

| Arquivo | Conteúdo |
|---|---|
| 01-visao-e-escopo.md | O que é o projeto, para quem, objetivos e fora de escopo |
| 02-arquitetura-e-stack.md | Estilo arquitetural, stack, estrutura de pastas, camadas |
| 03-decisoes-tomadas.md | Decisões já fechadas (e o porquê), incluindo as tomadas em conversa |
| 04-estado-atual.md | **O que existe, o que foi validado, o que está pendente, bloqueios** |
| 05-regras-de-trabalho.md | Protocolo de atuação, definition of done, restrições não negociáveis |
| 06-roadmap-e-backlog.md | Fases 0 a 7, critérios de aceitação e backlog priorizado |
| 07-dados-e-api.md | Modelo de dados e contratos da API |
| 08-seguranca-e-ia.md | Autenticação, isolamento, privacidade e regras do assistente de IA |
| 09-ambiente-e-comandos.md | Como rodar, comandos, problemas conhecidos |

Fonte original dos requisitos: a especificação técnica v2.0 (ver nota no 01). Em caso de conflito, prevalece o que estiver registrado em **03-decisoes-tomadas.md**, pois são decisões posteriores.

## Como usar com o Claude
- **Claude Code:** o `CLAUDE.md` na raiz já aponta para este índice; ele é lido automaticamente.
- **Chat comum (claude.ai):** anexe `04-estado-atual.md` e os arquivos relevantes à tarefa no início da conversa. O Claude não lembra conversas anteriores.
