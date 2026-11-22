# ADR-006: Dependências adiadas: PyTorch e LangGraph

- Status: Proposto
- Data: 2026-11-22

## Contexto
Nenhum requisito funcional atual exige Deep Learning (os algoritmos previstos são do scikit-learn). A orquestração do assistente começa com um laço simples de tool calling.

## Decisão
PyTorch e LangGraph ficam fora do projeto até existir caso de uso concreto, que será registrado em novo ADR.

## Consequências
Imagens menores e menos superfície de manutenção. Se surgir demanda, a introdução será uma decisão explícita.
