# ADR-005: Contratos de API e geração de tipos

- Status: Proposto
- Data: 2026-11-22

## Contexto
Frontend e backend precisam permanecer sincronizados sem duplicação manual de tipos.

## Decisão
API REST versionada em /api/v1, esquema OpenAPI gerado pelo FastAPI, tipos TypeScript gerados a partir dele e verificados no CI. Erros no formato RFC 9457.

## Consequências
Divergências de contrato falham no CI. Adiciona uma etapa de geração de tipos ao fluxo do frontend (a ser implementada na Fase 1).
