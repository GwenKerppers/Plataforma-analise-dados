# 08. Segurança, privacidade e IA

## Autenticação (ADR-002)
Access JWT 15 min (memória); refresh opaco em cookie HttpOnly/Secure/SameSite=Strict, guardado como hash, com rotação; reuso de token rotacionado revoga a família inteira. Senhas Argon2id. Rate limiting (Redis) em login, registro e reset. Exige CORS/CSRF configurados.

## Isolamento
Repositórios exigem `owner_id`. Testes parametrizados de acesso horizontal em cada endpoint, inclusive trocando IDs na requisição. Validação sempre no backend.

## Arquivos (Fase 2)
Lista de extensões; checagem de assinatura/MIME; limites de tamanho/linhas/colunas; proteção contra arquivos comprimidos maliciosos; nomes internos gerados pelo sistema; rejeitar macros. Nunca confiar no nome/extensão do usuário.

## Privacidade / LGPD
Minimização, controle de acesso, retenção, exclusão completa, transparência sobre envio a provedores externos, logs de eventos. **Não declarar conformidade legal automática**; documentar medidas técnicas.

## Assistente de IA (Fase 6)
- Camada independente de provedor; tool calling com schemas validados, limites e autorização. `owner_id` vem do servidor, nunca do modelo.
- **Proibido** executar SQL, Python ou comandos produzidos pelo LLM.
- Estatísticas via ferramentas determinísticas, não por estimativa do modelo.
- Respostas distinguem: calculado, interpretação, hipótese, indisponível; citam dataset, versão, colunas e operação.
- Conteúdo dos datasets é entrada não confiável (prompt injection em células). Mascaramento configurável, limites de contexto/tokens/custo, registro de uso.
- Sem provedor configurado: mensagem clara, nunca simular respostas.

## ML
Pipelines scikit-learn para evitar vazamento; nunca desserializar modelos enviados por usuários.

## Observabilidade
Logs estruturados sem senhas/tokens/dados pessoais; exceções por domínio; métricas só com coleta e interpretação definidas.
