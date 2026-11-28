# ADR-010: Limitação de requisições (rate limiting)

- Status: Proposto
- Data: 2026-11-22

## Contexto
Os endpoints de cadastro, login e renovação são alvo de força bruta e de abuso. O ADR-002 exige rate limiting nos endpoints sensíveis; o ADR-009 deixou a mitigação de enumeração de e-mails para esta etapa.

## Decisão
- **Janela fixa no Redis** (`INCR` + `EXPIRE NX` em transação), sem dependência nova. A janela começa na primeira requisição da chave. Limites configuráveis por variável de ambiente (defaults): cadastro 10/hora por IP; login 20/min por IP e **5/min por e-mail**; renovação 60/min por IP. Excedido: `429` com `Retry-After` e corpo RFC 9457 (`code: rate_limited`).
- A chave por e-mail usa **hash** do e-mail, para não gravar e-mails no Redis.
- **Fail open:** se o Redis estiver indisponível, a requisição passa e o erro vai para o log. Troca consciente: disponibilidade do login acima de proteção temporária; deve gerar alerta quando houver monitoramento.
- **IP do cliente:** `request.client.host`. Atrás de proxy/balanceador, é preciso configurar o uvicorn para confiar nos cabeçalhos do proxy (`--proxy-headers` e `--forwarded-allow-ips`); sem isso todos os usuários compartilhariam o IP do proxy. Não confiamos em `X-Forwarded-For` por padrão, pois seria falsificável.
- Limite por e-mail aceita um efeito colateral: alguém pode atrasar o login de uma vítima por até 1 minuto tentando repetidamente. Considerado aceitável frente ao ganho contra força bruta.

## Consequências
Testes usam Redis real com prefixo único por teste (o CI agora sobe um serviço Redis); os demais testes usam um limitador nulo. Janela fixa permite rajada de até 2x o limite na virada da janela; se isso virar problema, migrar para janela deslizante.

## Sessões (mesma etapa)
`GET /users/me/sessions`, `DELETE /users/me/sessions/{id}` e `DELETE /users/me/sessions`. O `id` público é o `family_id`. Sessão inexistente e sessão de outro usuário respondem igual (404). O token de acesso já emitido continua válido até expirar (até 15 min) após a revogação.
