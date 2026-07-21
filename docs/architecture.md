# Architecture

## Context

Spec Kit Turbo extends GitHub Spec Kit without replacing its central specification-driven workflow. The repository should remain reusable across frontend and backend projects and should not encode one company's application conventions in its core.

## Layers

### 1. Upstream core

The original Spec Kit concepts and lifecycle remain the stable foundation. Turbo should avoid copying upstream implementation unless adaptation is impossible.

### 2. Turbo preset

Provides improved templates, defaults, checklists, and command behavior while preserving familiar Spec Kit artifacts.

### 3. Workflows

Routes requests by work type and controls sequencing, checkpoints, quality gates, and completion criteria.

Initial workflow targets:

- feature;
- bugfix;
- refactor;
- discovery;
- hotfix.

### 4. Agent skills

Encapsulate specialist behavior. Initial roles:

- orchestrator;
- product owner;
- architect;
- frontend engineer;
- backend engineer;
- test engineer;
- code reviewer;
- release manager.

The v1 implementation is Codex-first and installs skills under `.agents/skills`. The generic implementation specialist executes approved tasks; technology-specific specialists can be added later without changing workflow contracts.

The constitution facilitator diagnoses the repository, conducts one adaptive question at a time, delegates draft writing to `speckit-constitution`, and requires human approval before finalizing `.specify/memory/constitution.md`.

Skills should define inputs, outputs, boundaries, handoff rules, and stop conditions. They should not duplicate generic repository context already present in `AGENTS.md`.

### 5. Stack profiles

Add technology-specific constraints and validation. A stack profile may define architecture conventions, preferred tools, quality commands, testing strategy, and known anti-patterns.

The first profile will target Angular. Other stacks remain optional and independently installable.

### 6. Project profile

Each consuming repository declares its own stack, commands, workflow policy, quality gates, and documentation expectations. Project settings override Turbo defaults explicitly.

## Core flow

```text
request
  -> classify
  -> discover/clarify
  -> specify
  -> plan
  -> decompose
  -> analyze consistency
  -> implement incrementally
  -> validate
  -> review
  -> prepare delivery
```

## State and resumability

Every workflow should make its current phase, completed artifacts, open questions, decisions, deviations, validations, blockers, and next action recoverable from repository files. Chat history must not be the only source of truth.

## Installation contract

The project-local manifest fixes the Turbo version and identifies managed assets. Install and upgrade refresh managed runtime files while preserving project configuration and Spec Kit artifacts. Shared Turbo rules live in `AGENTS.turbo.md`; repository-specific rules remain in the consumer's `AGENTS.md`.

## State runtime

`.specify/turbo/turbo.js` is the self-contained Node runtime between declarative workflow YAML and agent work. It creates the phase list for the selected classification, evaluates conditions and earlier-phase preconditions, skips inapplicable phases, verifies one evidence entry for each gate requirement, and records human approval or rejection. Skills still perform discovery, implementation, testing, and review; the runtime only makes their handoffs and resumptions unambiguous.

## Socratic constitution flow

The constitution workflow persists diagnosis, questions, answers, decisions, contradictions, confidence, draft path, and approval status. A draft is written to `.specify/memory/constitution.draft.md`; the final constitution changes only after approval. Interrupted interviews resume from `.specify/turbo/state.json`.

## Visual specification flow

When a frontend request includes screenshots, the visual specifier runs before product specification. It records observed, inferred, and unknown visual facts, generates `VAC-*` criteria, and references the result from `spec.md`. Image persistence is opt-in and can occur only under `.specify/visual-references/` after the managed `.gitignore` rule passes `git check-ignore`.

## Quality model

Completion requires evidence, not an agent assertion. Relevant evidence can include:

- acceptance criteria mapping;
- lint results;
- unit or integration test results;
- successful build;
- accessibility checks;
- security review;
- code review findings and resolutions.

## Design constraints

- composition before fork;
- deterministic files before conversational memory;
- explicit configuration before hidden assumptions;
- human approval for consequential decisions;
- minimal coupling between skills;
- versioned schemas for machine-readable configuration.
