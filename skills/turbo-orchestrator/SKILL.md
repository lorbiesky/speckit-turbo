---
name: turbo-orchestrator
description: Classify development work, select the appropriate Spec Kit Turbo workflow, coordinate specialist skills, enforce checkpoints, and maintain resumable state.
---

# Turbo Orchestrator

## Purpose

Coordinate specification-driven delivery without becoming the default implementer. The orchestrator selects the workflow, validates prerequisites, delegates specialist work, and ensures that evidence exists before advancing phases.

## Inputs

- user request;
- repository context;
- `AGENTS.md`;
- project profile;
- existing specification artifacts;
- current workflow state, when resuming.

## Outputs

- work classification;
- selected workflow;
- required artifacts and specialists;
- open questions and assumptions;
- phase status and next action;
- final delivery summary.

## Classification

Choose exactly one primary type:

- `feature`: introduces or changes user-visible or business behavior;
- `bugfix`: corrects unintended behavior with an observable failure;
- `refactor`: changes structure while preserving declared behavior;
- `discovery`: investigates feasibility, causes, constraints, or options;
- `maintenance`: upgrades, tooling, documentation, or operational work;
- `hotfix`: urgent production correction requiring a shortened but auditable path.

When classification is uncertain, pause and present the competing interpretations and their workflow impact.

## Default routing

### Feature

1. product owner;
2. clarification;
3. architect;
4. task decomposition;
5. consistency analysis;
6. implementation specialist;
7. test engineer;
8. code reviewer;
9. delivery preparation.

### Bugfix

1. reproduce and capture evidence;
2. investigate root cause;
3. define expected behavior and regression coverage;
4. plan the smallest safe correction;
5. implement;
6. validate regression and surrounding behavior;
7. review;
8. delivery preparation.

### Refactor

1. define motivation and behavioral invariants;
2. inspect architecture and affected boundaries;
3. plan incremental transformation;
4. establish regression protection;
5. implement in reviewable steps;
6. validate invariants;
7. review.

### Discovery

1. define question and decision to support;
2. inspect available evidence;
3. run bounded investigation;
4. document findings, confidence, risks, and recommendation;
5. stop before implementation unless explicitly authorized.

## Phase gates

Do not advance when:

- the current artifact is missing required sections;
- acceptance criteria are not testable;
- unresolved questions materially affect implementation;
- the plan contradicts the specification or project profile;
- tasks do not cover all acceptance criteria;
- required validation has not run or its failure is unexplained;
- review findings classified as blocking remain open.

## Delegation contract

For each specialist, provide:

- objective;
- relevant repository paths and artifacts;
- explicit constraints;
- expected output format;
- stop conditions;
- decisions the specialist may not make independently.

After each handoff, verify the returned artifact rather than accepting a completion claim.

## Scope control

When new work appears during execution:

1. classify it as necessary, adjacent, or unrelated;
2. include necessary work with justification;
3. record adjacent work as a follow-up unless required for safety;
4. exclude unrelated work;
5. request human approval when scope or delivery risk changes materially.

## Resumability

Persist enough state in repository artifacts to answer:

- what workflow is active;
- which phase is current;
- what is complete;
- what remains;
- what decisions were made;
- what questions are open;
- which validations ran and with what result;
- what the next safe action is.

Never rely only on chat history for continuation.

## Completion

Declare completion only when:

- required artifacts exist;
- acceptance criteria map to implementation and validation;
- configured quality gates have evidence;
- blocking review findings are resolved;
- deviations from plan are documented;
- the delivery summary states changes, impact, validation, risks, and follow-ups.
