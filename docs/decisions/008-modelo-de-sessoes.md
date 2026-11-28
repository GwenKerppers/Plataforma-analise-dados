# ADR-008: Modelo de usuários e sessões

- Status: Proposto
- Data: 2026-11-22

## Contexto
O ADR-002 define refresh tokens com rotação e detecção de reuso. Falta decidir como isso é persistido.

## Decisão
- **`users`**: PK UUID (v4; Python 3.12 não traz UUIDv7 e não vale uma dependência só para isso), e-mail único **sempre em minúsculas**, com `CHECK (email = lower(email))` no banco além da normalização no serviço, `password_hash` (Argon2id), `full_name`, `is_active`, timestamps.
- **`user_sessions`**: **uma linha por refresh token emitido**. Uma rotação revoga a linha antiga (`revoked_reason = 'rotated'`) e cria outra na mesma `family_id`. Reapresentar um token já rotacionado revoga a família inteira (`reuse_detected`). Só o hash SHA-256 do token é guardado.
- Integridade no banco: motivos de revogação restritos a `rotated`, `logout`, `reuse_detected`, e `revoked_at`/`revoked_reason` sempre preenchidos juntos. `ON DELETE CASCADE` de `users` para `user_sessions`.
- **Não armazenamos IP**, só o `user_agent` (truncado), por minimização de dados (LGPD). Pode ser reavaliado se a auditoria exigir.
- A tabela `password_reset_tokens` fica para o fim da Fase 1, junto com a recuperação de senha.

## Consequências
Reuso de token é detectável sem estado extra. A listagem de sessões ativas agrupa por `family_id`. Limpeza de linhas expiradas será uma tarefa periódica futura. Um teste compara as migrações com os modelos e falha se divergirem.
