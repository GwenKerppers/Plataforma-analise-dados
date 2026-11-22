# 01. Visão e escopo

## O que é
Aplicação web para: importar datasets (CSV/XLSX/XLS), analisá-los estatisticamente (EDA), visualizá-los, treinar modelos de Machine Learning e consultá-los em linguagem natural via assistente de IA.

## Natureza do projeto
**Projeto de estudo e portfólio**, publicado no GitHub para avaliadores de entrevistas. Não é um produto comercial. Consequências:
- Linguagem do README e docs: honesta, sem tom de marketing ("SaaS").
- O status real de cada fase deve ser sempre visível. Não prometer o que não existe.
- Decisões justificadas em ADRs são parte do valor do projeto.

## Nome
- Nome do projeto: **Plataforma de Análise de Dados** (pasta/slug `plataforma-analise-dados`). O nome anterior "DataMind" foi abandonado.
- Repositório GitHub: https://github.com/GwenKerppers/Plataforma-Inteligente-de-Analise-de-Dados (pode ser renomeado para `plataforma-analise-dados`).
- Licença: MIT.

## Usuários-alvo
Pessoas sem programação e analistas com conhecimento técnico.

## Pilares
1. Engenharia de dados (ingestão, validação, versionamento).
2. Análise (estatística descritiva, EDA, visualização).
3. Machine Learning (experimentos reproduzíveis).
4. IA generativa (consulta em linguagem natural com ferramentas controladas).

## Fora de escopo inicial
Microsserviços, OAuth/OIDC federado, Deep Learning (PyTorch), orquestração multiagente (LangGraph). Podem entrar depois, via ADR.

## Requisitos originais
A especificação técnica completa (v2.0, em português) foi fornecida pela dona do projeto. Recomenda-se guardá-la no repositório como `docs/especificacao-original.md`. Este conjunto de arquivos é um resumo operacional dela.
