# Installation

Spec Kit Turbo supports both a clean bootstrap and adaptation of an existing GitHub Spec Kit project. The published npm package is the preferred distribution method:

```bash
npx speckit-turbo@latest init ../path-to-project --mode existing
```

Install globally when preferred:

```bash
npm install --global speckit-turbo
speckit-turbo init ../path-to-project --mode existing
```

The CLI also exposes `speckit-turbo doctor [path] [--strict]`, `speckit-turbo upgrade [path]`, and `speckit-turbo version [path]`. It is implemented in Node and installs a self-contained Node runtime in each consumer project; Python is not a user prerequisite.

## Prerequisites

- Git repository;
- Node.js 18 or newer and npm;
- GitHub Spec Kit initialized when the project is ready to run specification workflows.

Python is only required for contributors running the repository's legacy validation scripts. It is not required by the published npm CLI or by the installed Node workflow runtime.

## Installation modes

Use automatic detection by default. A structured `.specify` directory containing `memory/constitution.md`, `templates/`, or `scripts/` selects adaptation mode.

Clean mode delegates upstream initialization to Specify CLI. It requires an explicit upstream ref:

```bash
./scripts/install.sh --mode clean --spec-kit-version v0.8.11 ../path-to-project
```

Existing mode preserves upstream Spec Kit files and adds Turbo alongside them:

```bash
./scripts/install.sh --mode existing ../path-to-project
```

Use `--mode auto` to make detection explicit in automation. Clean mode requires `uv` and network access unless `SPECKIT_TURBO_BOOTSTRAP_COMMAND` is supplied by a controlled test or environment.

## Installation from a local clone

The npm package is the recommended path. These shell and PowerShell wrappers remain available for local Turbo development and compatibility; they use the legacy Python installer.

```bash
./scripts/install.sh ../path-to-project
```

## Windows PowerShell

```powershell
./scripts/install.ps1 ../path-to-project
```

The installer preserves existing project configuration and adds or refreshes only managed Turbo assets. When updating an existing Turbo installation, it creates a dated backup under `.specify/turbo/backups/`.

## Installed structure

```text
project/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── turbo-orchestrator/
│       ├── turbo-product-owner/
│       ├── turbo-architect/
│       ├── turbo-constitution-facilitator/
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

The deeper schema, workflow, quality-command, installation-mode, and constitution-contract checks remain available through the contributor validator and legacy Python doctor.

Visual references are disabled by default. To persist them safely, configure:

```yaml
visual:
  enabled: true
  persist_references: true
  references_path: .specify/visual-references
```

The installer maintains a managed `.gitignore` block for that directory. The visual skill verifies the rule with `git check-ignore` before copying any image. The doctor reports an error for existing unignored references.

## Dynamic workflow runtime

The installed runtime is `.specify/turbo/turbo.js`. It initializes the state from a workflow classification, evaluates declared conditions and preconditions, skips inapplicable phases, requires evidence for every gate requirement, pauses at configured human checkpoints, and resumes work without losing phase state. It does not replace the coding agent or run Spec Kit commands by itself.

Configure optional checkpoints in `project.yml`:

```yaml
workflow:
  human_checkpoints:
    - product-specification
    - technical-plan
```

Use `start`, `status --refresh`, `complete`, `checkpoint --approve|--reject`, and `resume` to operate the state. `start` safely replaces only the untouched template state; use `--force` to deliberately replace active work.

## Socratic constitution

In Codex, ask to create or update the project constitution. The facilitator first diagnoses the repository, asks one question at a time, and resumes from `.specify/turbo/state.json` when interrupted. It creates a draft and waits for approval before changing the upstream constitution.

Equivalent Codex workflow intents are:

```text
$turbo-constitution
$turbo-status
$turbo-resume
```

## Reinstall or update

Run the npm upgrade after a new Turbo version is published. Existing `project.yml`, `state.json`, constitution, specs, templates, upstream commands, and non-managed `AGENTS.md` content are preserved. Skills, shared rules, schemas, workflows, manifest, Node runtime, and doctor command are refreshed.

```bash
npx speckit-turbo@latest version .
npx speckit-turbo@latest upgrade ../meu-projeto
sh .specify/turbo/upgrade.sh /caminho/para/speckit-turbo .
```

The final shell command is only for compatibility when developing from a local clone; npm users should use `speckit-turbo upgrade`.

The installed manifest is `.specify/turbo/manifest.json`. It records the Turbo version, Codex integration, Spec Kit concepts expected by the workflows, and managed paths. The `AGENTS.md` integration block is added only once and is never replaced by an upgrade.

Review upstream changes before updating projects that have modified installed Turbo assets directly. Project-specific changes belong in the project profile or local `AGENTS.md`, not in generated runtime files.

## Validate this repository

Contributor validation requires the development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py
```

This validates schemas, templates, skill metadata, workflow structure, owner references, gates, and classification uniqueness.
