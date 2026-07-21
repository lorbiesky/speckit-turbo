# Installation

Spec Kit Turbo supports both a clean bootstrap and adaptation of an existing GitHub Spec Kit project. The published npm package is the preferred distribution method.

The target directory is the final argument. Use `.` from inside the target project; a full path is not required.

From the existing project's root:

```bash
cd path-to-project
npx speckit-turbo@latest init . --mode existing
```

From its parent directory:

```bash
npx speckit-turbo@latest init ./path-to-project --mode existing
```

Use automatic mode when you want Turbo to detect whether the project is clean or already structured as Spec Kit:

```bash
npx speckit-turbo@latest init .
```

Install globally when preferred:

```bash
npm install --global speckit-turbo
speckit-turbo init . --mode existing
```

The CLI also exposes `speckit-turbo doctor [path] [--strict]`, `speckit-turbo upgrade [path]`, and `speckit-turbo version [path]`. It is implemented in Node and installs a self-contained Node runtime in each consumer project; Python is not a user prerequisite.

## Prerequisites

- Git repository;
- Node.js 18 or newer and npm;
- GitHub Spec Kit initialized when the project is ready to run specification workflows.

Python is only required for contributors running the repository's legacy validation scripts. It is not required by the published npm CLI or by the installed Node workflow runtime.

## Installation modes

Use automatic detection by default. A structured `.specify` directory containing `memory/constitution.md`, `templates/`, or `scripts/` selects adaptation mode.

Use `--mode clean|existing|auto` to select the installation behavior. Clean mode delegates upstream initialization to Specify CLI and requires `--spec-kit-version`; existing mode preserves upstream Spec Kit files and adds Turbo alongside them.

The installer preserves existing project configuration and adds or refreshes only managed Turbo assets. When updating an existing Turbo installation, it creates a dated backup under `.specify/turbo/backups/`.

## Installed structure

```text
project/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── turbo-orchestrator/
│       ├── turbo/
│       ├── turbo-feature/
│       ├── turbo-bugfix/
│       ├── turbo-refactor/
│       ├── turbo-discovery/
│       ├── turbo-maintenance/
│       ├── turbo-hotfix/
│       ├── turbo-constitution/
│       ├── turbo-status/
│       ├── turbo-resume/
│       ├── turbo-product-owner/
│       ├── turbo-architect/
│       ├── turbo-constitution-facilitator/
│       ├── turbo-tdd-coach/
│       ├── turbo-test-engineer/
│       └── turbo-code-reviewer/
└── .specify/
    └── turbo/
        ├── AGENTS.turbo.md
        ├── manifest.json
        ├── project.yml
        ├── state.json
        ├── turbo.js
        ├── node-runtime/
        │   ├── cli.js
        │   └── node_modules/yaml/
        ├── templates/
        │   ├── constitution-interview.md
        │   ├── constitution.draft.md
        │   ├── tdd-cycle.md
        │   └── visual-spec.md
        └── runtime/
            ├── schemas/
            └── workflows/
```

## Configure the project

Edit `.specify/turbo/project.yml` immediately after installation. Replace the project identity, stack, and command placeholders. A quality gate enabled under `quality` must have a corresponding command.

Example:

```yaml
project:
  name: customer-portal
  type: frontend
  stack: angular

quality:
  lint: true
  unit_tests: true
  build: true
  accessibility: true
  security_review: true

commands:
  install: npm ci
  lint: npm run lint
  test: npm test -- --watch=false
  build: npm run build
```

Keep the workflow booleans and documentation policy from the generated template unless the project requires different human checkpoints.

### TDD

New projects enable TDD by default. Implementation workflows require a failing test before production code and evidence of the green and refactor steps afterward:

```yaml
tdd:
  enabled: true
  allow_exception: true
  require_human_approval_for_exception: true
```

Set `tdd.enabled: false` when the project explicitly does not use TDD. When it remains enabled, tell the agent why TDD is not applicable and provide the risk and alternative validation. The orchestrator records the exception and requests human approval before continuing. Never edit `state.json` to bypass the gate. The cycle is persisted in `.specify/turbo/tdd-cycle.md` and `state.json`.

## Diagnose the installation

Run from the consumer project root:

```bash
    npx speckit-turbo@latest doctor .
```

Use strict mode when placeholders and other warnings must fail automation:

```bash
npx speckit-turbo@latest doctor . --strict
```

The Node doctor verifies:

- the Spec Kit directory and self-contained Node runtime;
- all user-facing and specialist Turbo skills;
- the installed Turbo manifest and version;
- basic project-profile placeholders;
- visual-reference ignore protection, constitution drafts, and backup protection.

The deeper schema, workflow, and contract checks remain available through the contributor validator. Consumer operations use npm for installation and maintenance, and agent commands for development workflows.

Visual references are disabled by default. To persist them safely, configure:

```yaml
visual:
  enabled: true
  persist_references: true
  references_path: .specify/visual-references
```

The installer maintains a managed `.gitignore` block for that directory. The visual skill verifies the rule with `git check-ignore` before copying any image. The doctor reports an error for existing unignored references.

When upgrading a project installed by Turbo `1.0.1` or earlier, the npm CLI backs up and removes only the known legacy Python runtime files. Unknown files and project-owned configuration remain untouched.

## Uso por agentes

O runtime local é um detalhe interno entre as skills, os workflows declarativos e o estado persistente. O usuário não precisa executá-lo. Use os comandos de agente:

```text
$turbo Criar checkout como visitante
$turbo-feature Implementar esta tela conforme o print anexado
$turbo-bugfix Corrigir erro de autenticação
$turbo-refactor Extrair o módulo de pagamentos
$turbo-status
$turbo-resume
$turbo-constitution Atualizar as regras de engenharia
```

O `turbo-orchestrator` inicia ou retoma o workflow, encaminha cada fase para a skill responsável, registra evidências e pausa em checkpoints humanos. As skills invocam `$speckit-specify`, `$speckit-plan`, `$speckit-tasks`, `$speckit-analyze` e `$speckit-implement` quando declarados pelo workflow.

Configure optional checkpoints in `project.yml`:

```yaml
workflow:
  human_checkpoints:
    - product-specification
    - technical-plan
```

Não opere fases editando `state.json` ou executando scripts internos. Consulte `$turbo-status`, resolva o bloqueio indicado e use `$turbo-resume` para continuar.

## Socratic constitution

In Codex, ask to create or update the project constitution. The facilitator first diagnoses the repository, asks one question at a time, and resumes from `.specify/turbo/state.json` when interrupted. It creates a draft and waits for approval before changing the upstream constitution.

Equivalent Codex workflow intents are:

```text
$turbo-constitution
$turbo-status
$turbo-resume
```

Para screenshots, basta anexar a imagem ao pedido. A análise visual será ativada automaticamente, gerará `visual-spec.md` e critérios `VAC-*`, e bloqueará a persistência se o diretório não estiver protegido pelo `.gitignore`.

## Reinstall or update

Run the npm upgrade after a new Turbo version is published. Existing `project.yml`, `state.json`, constitution, specs, templates, upstream commands, and non-managed `AGENTS.md` content are preserved. Skills, shared rules, schemas, workflows, manifest, Node runtime, and doctor command are refreshed.

```bash
npx speckit-turbo@latest version .
npx speckit-turbo@latest upgrade ../meu-projeto
```

The installed manifest is `.specify/turbo/manifest.json`. It records the Turbo version, Codex integration, Spec Kit concepts expected by the workflows, and managed paths. The `AGENTS.md` integration block is added only once and is never replaced by an upgrade.

Review upstream changes before updating projects that have modified installed Turbo assets directly. Project-specific changes belong in the project profile or local `AGENTS.md`, not in generated runtime files.

## Validate this repository

Contributor validation requires the development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py
```

This validates schemas, templates, skill metadata, workflow structure, owner references, gates, and classification uniqueness. Python is used only for contributor validation and is not required by consumer projects.
