# ADR-007: Backend de armazenamento S3 compatível

- Status: Aberto
- Data: 2026-11-22

## Contexto
O ADR-003 previa MinIO como armazenamento de objetos. Durante a validação da Fase 0, as imagens oficiais `minio/minio` deixaram de ser baixáveis (removidas dos registries públicos), o que quebrou o `docker compose up`.

## Decisão
1. O serviço `minio` passa a ser opcional (profile `storage`), fora do caminho da Fase 0.
2. A aplicação continuará falando com uma **interface de storage S3-compatível**, sem acoplamento a um fornecedor.
3. O servidor S3 concreto será escolhido e registrado neste ADR **antes da Fase 2**, avaliando alternativas como SeaweedFS, Garage ou outras imagens ativas e mantidas. Critérios: imagem pública estável, licença compatível, manutenção ativa e simplicidade em desenvolvimento.

## Consequências
A Fase 0 volta a ser executável sem dependência do MinIO. O risco de lock-in já estava mitigado pela abstração de storage do ADR-003; este episódio justifica mantê-la.
