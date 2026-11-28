# ADR-002: Autenticação e isolamento de dados

- Status: Proposto
- Data: 2026-11-22

## Contexto
A plataforma é multiusuário e lida com dados potencialmente sensíveis.

## Decisão
Access token JWT curto (15 min) mantido em memória no frontend. Refresh token opaco em cookie HttpOnly/Secure/SameSite=Strict, persistido apenas como hash, com rotação e revogação da família inteira se um token já rotacionado for reapresentado. Senhas com Argon2id. Rate limiting em Redis. Todo repositório de recurso exige `owner_id`; recurso alheio responde 404.

## Consequências
Reduz exposição a XSS e roubo de tokens. Exige configuração de CORS e proteção CSRF. Testes parametrizados de acesso horizontal são obrigatórios por endpoint.

## Esclarecimento (etapa 1.2)
Refresh tokens são aleatórios e de alta entropia, por isso são guardados com hash SHA-256 (rápido e adequado a esse caso). Argon2id fica restrito às senhas, que têm baixa entropia. Cada rotação cria uma nova linha em `user_sessions` na mesma `family_id`; a linha anterior recebe `used_at`.
