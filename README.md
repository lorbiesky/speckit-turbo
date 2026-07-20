# Spec Kit Turbo

Camada reutilizável sobre o GitHub Spec Kit para desenvolvimento orientado por especificações com agentes de código.

## Objetivo

Padronizar e automatizar o fluxo de descoberta, especificação, planejamento, implementação, validação e revisão em projetos frontend e backend.

## Princípios

- preservar o fluxo central do Spec Kit;
- adicionar capacidades por presets, extensions, workflows e skills;
- separar regras globais de regras específicas de cada projeto;
- exigir rastreabilidade entre requisito, tarefa, código e teste;
- permitir retomada segura do trabalho por agentes diferentes;
- manter decisões importantes revisáveis por humanos.

## Arquitetura inicial

```text
Core do Spec Kit
  + preset Turbo
  + workflows especializados
  + skills de agentes
  + perfil de stack
  + configuração do projeto consumidor
```

## Primeira fase

A fundação inicial inclui:

- `AGENTS.md` com regras globais;
- documentação da arquitetura;
- perfil de projeto reutilizável;
- skill inicial de orquestração;
- base para workflows de feature, bugfix e refactor.

## Status

Projeto em fase inicial de definição e bootstrap.
