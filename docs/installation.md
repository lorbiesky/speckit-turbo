# Installation

Spec Kit Turbo is installed into an existing project that uses, or will use, GitHub Spec Kit.

## Prerequisites

- Git repository;
- Python 3.10 or newer for the doctor command;
- GitHub Spec Kit initialized when the project is ready to run specification workflows;
- a clone of this repository available locally.

## Unix, Linux, and macOS

From the Spec Kit Turbo repository:

```bash
./scripts/install.sh ../path-to-project
```

## Windows PowerShell

```powershell
./scripts/install.ps1 ../path-to-project
```

The installer preserves existing project configuration and adds or refreshes only managed Turbo assets.

## Installed structure

```text
project/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── turbo-orchestrator/
│       ├── turbo-product-owner/
│       ├── turbo-architect/
│       ├── turbo-test-engineer/
│       └── turbo-code-reviewer/
└── .specify/
    └── turbo/
        ├── AGENTS.turbo.md
        ├── project.yml
        ├── state.json
        ├── doctor.py
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
python .specify/turbo/doctor.py
```

Use strict mode when placeholders and other warnings must fail automation:

```bash
python .specify/turbo/doctor.py --strict
```

The doctor verifies:

- Git and Spec Kit directories;
- the managed `AGENTS.md` integration block;
- required skills;
- installed schemas and workflows;
- project-profile structure and quality commands;
- persistent workflow-state structure.

## Reinstall or update

Run the same installer again after updating the Spec Kit Turbo clone. Existing `project.yml`, `state.json`, and non-managed `AGENTS.md` content are preserved. Skills, shared rules, schemas, workflows, and the doctor command are refreshed.

Review upstream changes before updating projects that have modified installed Turbo assets directly. Project-specific changes belong in the project profile or local `AGENTS.md`, not in generated runtime files.

## Validate this repository

Contributor validation requires the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
```

This validates schemas, templates, skill metadata, workflow structure, owner references, gates, and classification uniqueness.
