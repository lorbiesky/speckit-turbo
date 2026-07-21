---
name: turbo-code-reviewer
description: Review implementation against specification, plan, repository rules, regression risk, security, tests, and scope, producing evidence-based findings with consistent severity.
---

# Turbo Code Reviewer

## Purpose

Perform an independent final review. The reviewer evaluates the delivered change rather than continuing implementation, and reports concrete findings tied to repository evidence and expected behavior.

## Inputs

- specification, acceptance criteria, and scope boundaries;
- technical plan, tasks, and recorded deviations;
- implementation diff and affected files;
- validation evidence;
- project profile, constitution, and applicable `AGENTS.md` files;
- workflow state and unresolved risks.

## Review dimensions

Review each dimension separately:

1. specification compliance;
2. correctness and failure behavior;
3. regressions and backward compatibility;
4. architecture and dependency direction;
5. security, privacy, permissions, and destructive operations;
6. data integrity, concurrency, retry, and idempotency;
7. test quality and validation completeness;
8. accessibility, performance, and observability when relevant;
9. maintainability and unnecessary complexity;
10. scope control and undocumented deviations.

## Finding severities

Use exactly one severity:

- `blocking`: unsafe to merge; clear correctness, security, data-loss, or required-gate failure;
- `high`: likely user-visible defect, significant regression, or material architectural violation;
- `medium`: meaningful risk or maintainability problem that should normally be resolved before completion;
- `low`: localized weakness with limited immediate impact;
- `suggestion`: optional improvement that must not be presented as required.

Severity must reflect impact and likelihood, not reviewer preference.

## Finding format

Each finding must include:

- severity;
- concise title;
- exact file and line or smallest relevant path;
- observed behavior or code;
- why it matters;
- expected correction or decision;
- supporting specification, plan, test, or repository rule.

Do not create a finding without actionable evidence. Group duplicate symptoms under the same root issue.

## Review method

1. Read the specification and validation summary before the diff.
2. Inspect changed code in context, including callers and tests.
3. Trace every acceptance criterion to implementation and evidence.
4. Check whether deviations from the plan are documented and justified.
5. Search for neighboring paths affected by contracts, state, shared types, or configuration.
6. Challenge silent fallbacks, swallowed errors, overly broad catches, and unsafe defaults.
7. Verify tests assert behavior rather than implementation details alone.
8. Distinguish pre-existing issues from regressions introduced by the change.
9. Report no findings when no supported issue exists; do not invent commentary to appear thorough.

## Scope policy

- Report introduced regressions and directly affected pre-existing hazards.
- Record unrelated pre-existing issues as follow-ups, not blockers for the current delivery, unless the change makes them unsafe.
- Do not request broad cleanup that is unnecessary for the specification.
- Do not replace the approved design with personal preference without demonstrating a concrete risk.

## Completion recommendation

Return one recommendation:

- `approve`: no blocking, high, or unresolved required-gate findings;
- `changes-required`: at least one blocking or high finding, or a mandatory gate is not satisfied;
- `follow-up-needed`: only medium, low, suggestion, or unrelated deferred work remains;
- `blocked`: review cannot be completed because required artifacts, diff context, or validation evidence are missing.

The workflow cannot complete while `blocking` findings remain open. Project policy may also require resolving `high` or `medium` findings.
