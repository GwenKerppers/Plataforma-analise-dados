# ADR-009: Fluxo de autenticação (detalhes de implementação)

- Status: Proposto
- Data: 2026-11-22

## Contexto
O ADR-002 fixou a estratégia (access JWT curto + refresh opaco rotacionado) e o ADR-008 o modelo de dados. Aqui ficam as decisões de implementação da etapa 1.3.

## Decisão
- **Senhas:** Argon2id (argon2-cffi, parâmetros padrão). Só comprimento (12 a 128 caracteres), sem regras de composição. No login há máximo, mas não mínimo, para não revelar a política.
- **Login:** erro único "Credenciais inválidas" para e-mail inexistente, senha errada ou usuário inativo; quando o e-mail não existe, é gasta uma verificação fictícia para igualar o tempo de resposta.
- **Cadastro:** responde 409 se o e-mail já existe. Isso permite enumerar e-mails cadastrados. Troca consciente por melhor experiência; será mitigada com rate limiting (etapa 1.4). Alternativa futura: cadastro com confirmação por e-mail.
- **Access token:** JWT HS256, 15 min, claims `sub`, `typ=access`, `iat`, `exp`; o decodificador fixa o algoritmo (rejeita `none`) e o tipo. É sem estado: após logout ou revogação, um access token já emitido vale até expirar (no máximo 15 min).
- **Refresh token:** 48 bytes aleatórios (urlsafe), guardado só como SHA-256. Cookie `HttpOnly`, `SameSite=Strict`, `Secure` fora de desenvolvimento, **`Path=/api/v1/auth`**, para não ser enviado às demais rotas. O frontend deve chamar `refresh` e `logout` com `credentials: "include"`.
- **Rotação e reuso:** cada renovação revoga o token usado (`rotated`) e emite outro na mesma família. Apresentar um token `rotated` revoga a família (`reuse_detected`). Renovações concorrentes do mesmo token são serializadas com `SELECT ... FOR UPDATE`; consequência: um cliente que dispare duas renovações simultâneas com o mesmo token será deslogado. O frontend deve manter uma única renovação em andamento.
- **Logout:** idempotente; revoga a família inteira.
- **JWT_SECRET** é obrigatório (mínimo 32 caracteres); fora de desenvolvimento o valor de exemplo é rejeitado na inicialização.
- **SameSite=Strict** pressupõe frontend e API no mesmo site (hoje `localhost`; em produção, subdomínios do mesmo domínio).

## Consequências
Fluxo verificável por testes de integração (rotação, reuso, expiração, logout, usuário inativo). Pendentes: rate limiting e listagem/revogação de sessões (1.4), recuperação de senha (fim da Fase 1) e `PATCH /users/me`.
