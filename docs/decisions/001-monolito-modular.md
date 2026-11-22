# ADR-001: Monólito modular

- Status: Proposto
- Data: 2026-11-22

## Contexto
O domínio é coeso (dataset, versão e usuário atravessam todos os módulos). Microsserviços adicionariam custo de rede, consistência distribuída e operação sem ganho atual.

## Decisão
Um único código-base backend organizado em módulos com fronteiras claras. Implantado como processos distintos: API e worker (mesma imagem, comandos diferentes) mais o frontend. Não haverá diretório separado `apps/worker` até existir código exclusivo dele.

## Consequências
Simplicidade operacional e refatoração fácil. Exige disciplina nas fronteiras entre módulos (comunicação por serviços, não por modelos internos). Extração futura de um módulo é possível se houver necessidade comprovada de escala.
