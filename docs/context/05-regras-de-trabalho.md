# 05. Regras de trabalho

## Antes de agir
- Inspecionar o repositório e ler `04-estado-atual.md`. Nunca presumir que um arquivo está vazio. Preservar o que está correto.
- Antes de cada fase: objetivos, módulos afetados, arquivos, decisões, dependências, critérios de aceitação, testes. ADR para decisões relevantes.

## Durante
- Incremental: terminar uma funcionalidade antes de começar a que depende dela.
- Manter frontend, backend e banco sincronizados; não quebrar contratos.
- Não remover testes para passar; não silenciar exceções; não usar mocks/dados fictícios em fluxos reais; mocks devem ser claramente identificados.

## Verificação
- Rodar testes, tipos, lint e build quando possível. **Não afirmar que passou sem executar.** Se não puder executar, dizer isso e por quê.

## Relatório ao concluir uma tarefa
Resumo técnico, arquivos criados/alterados/removidos, decisões e dependências, testes e resultados, limitações, próximos passos.

## Definition of Done
Requisitos implementados, integração real entre camadas, regras no backend, validação de entrada, tratamento de erros, verificação de permissões, persistência adequada, testes automatizados, documentação atualizada, sem erros de build/execução, critérios de aceitação validados. Funcionalidade parcial não é "concluída".

## Restrições não negociáveis
Sem segredos no repositório; sem acesso entre usuários; sem execução irrestrita de SQL/Python/comandos pelo LLM; sem regras de negócio no frontend; sem acoplamento a um provedor de IA; sem microsserviços sem justificativa; sem dependências não avaliadas; não ignorar testes falhando.

## Ambiguidades
Identificar, propor decisão fundamentada e registrar. Não inventar requisitos silenciosamente.

## Como interagir com a dona do projeto
- Português do Brasil, passos numerados, comandos prontos para copiar (Windows/PowerShell como padrão).
- Ela valida no próprio PC; pedir a saída exata de erros.
- Explicar o "porquê" de forma curta; ela usa o projeto para estudo e entrevistas.
