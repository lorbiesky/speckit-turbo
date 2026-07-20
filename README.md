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

## Arquitetura

```text
Core do Spec Kit
  + preset Turbo
  + workflows especializados
  + skills de agentes
  + perfil de stack
  + configuração do projeto consumidor
```

O repositório contém contratos reutilizáveis. O instalador copia os recursos necessários para cada projeto consumidor, preservando sua configuração local.

## Capacidades atuais

- regras globais para agentes em `AGENTS.md`;
- orquestrador com classificação, delegação, gates e retomada;
- especialistas de Product Owner, Architect, Test Engineer e Code Reviewer;
- workflows de feature, bugfix e refactor;
- estado persistente em `.specify/turbo/state.json`;
- perfil de projeto e quality gates;
- instaladores para shell e PowerShell;
- comando doctor para diagnóstico do projeto consumidor;
- validação automática de schemas, templates, skills e workflows.

## Instalação rápida

Em Linux, macOS ou ambientes Unix:

```bash
./scripts/install.sh ../meu-projeto
```

No Windows PowerShell:

```powershell
./scripts/install.ps1 ../meu-projeto
```

Depois, configure o projeto e execute o diagnóstico:

```bash
cd ../meu-projeto
python .specify/turbo/doctor.py
```

Consulte [`docs/installation.md`](docs/installation.md) para estrutura instalada, atualização e validação.

## Desenvolvimento

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
```

A validação também é executada pelo GitHub Actions em pushes para `main` e pull requests.

## Status

Fundação, workflows e runtime inicial em desenvolvimento. O próximo perfil tecnológico planejado é Angular.
