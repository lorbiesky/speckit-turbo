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

Every workflow should make its current phase, completed artifacts, open questions, decisions, and next action recoverable from repository files. Chat history must not be the only source of truth.

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
