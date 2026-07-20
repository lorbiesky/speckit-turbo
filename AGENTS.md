# AGENTS.md

## Mission

Evolve Spec Kit Turbo as a reusable, auditable layer on top of GitHub Spec Kit. Prefer composition over forking upstream behavior.

## Operating rules

1. Inspect the repository and project profile before proposing implementation.
2. Classify work as feature, bugfix, refactor, discovery, maintenance, or hotfix.
3. Do not implement a feature before its problem, scope, and acceptance criteria are explicit.
4. Keep product decisions separate from technical decisions.
5. Preserve traceability from requirement to acceptance criterion, task, code, and test.
6. Prefer small, reviewable changes and draft pull requests.
7. Never overwrite project-specific conventions with generic defaults silently.
8. Record assumptions, risks, unresolved questions, and deviations from the plan.
9. Run relevant quality gates before declaring work complete.
10. Keep upstream Spec Kit concepts recognizable to reduce maintenance cost.

## Required artifacts by workflow

### Feature

- specification;
- clarification record when ambiguity exists;
- implementation plan;
- task breakdown;
- validation evidence;
- final review summary.

### Bugfix

- reproduction or observable failure;
- root-cause hypothesis and confirmation;
- regression test where practical;
- implementation notes;
- validation evidence.

### Refactor

- motivation and boundaries;
- behavioral invariants;
- migration strategy when needed;
- regression validation.

## Human checkpoints

Pause for human review when:

- business behavior is ambiguous;
- scope materially expands;
- architecture introduces a new dependency or cross-system contract;
- destructive migration is required;
- security, privacy, or compliance risk is identified;
- implementation deviates materially from an approved plan.

## Repository structure

- `skills/`: reusable agent capabilities;
- `workflows/`: workflow definitions and routing;
- `presets/`: overrides and templates for Spec Kit;
- `stacks/`: technology-specific guidance;
- `schemas/`: machine-readable contracts;
- `docs/`: architecture and operating documentation.
