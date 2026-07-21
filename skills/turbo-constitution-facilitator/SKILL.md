---
name: turbo-constitution-facilitator
description: Conduct repository-aware Socratic interviews to create or update a Spec Kit constitution, persist resumable decisions, produce an approved draft, and never replace the final constitution without human approval.
---

# Turbo Constitution Facilitator

## Purpose

Guide the creation or evolution of `.specify/memory/constitution.md` through evidence-based questions. Start with repository diagnosis, ask one adaptive question at a time, delegate draft writing to `speckit-constitution`, and wait for explicit approval before changing the final constitution.

## Inputs

- user intent: create, update, or review constitutional principles;
- repository structure, code patterns, tests, CI, documentation, dependencies, and Git history when relevant;
- `AGENTS.md`, `.specify/turbo/project.yml`, current workflow state, and Spec Kit constitution;
- previous `.specify/memory/constitution-interview.md`, when resuming.

## Outputs

- `.specify/memory/constitution-interview.md`;
- `.specify/memory/constitution.draft.md`;
- approved `.specify/memory/constitution.md` only after human approval;
- updated `constitutionInterview` state and next action;
- evidence, decisions, rejected alternatives, contradictions, confidence, and residual questions.

## Workflow

1. Determine `create` or `update` without changing files.
2. Inspect repository and configuration before asking anything. Record facts, patterns, gaps, and uncertainty in the interview artifact.
3. Classify each configured theme as applicable, partially applicable, or not applicable with a reason.
4. Ask exactly one question at a time. Base it on evidence, explain why it matters, and offer options only when they clarify a real tradeoff.
5. Record the user's answer verbatim, the decision extracted from it, confidence, and the next question before continuing.
6. Cover applicable themes: engineering principles, quality/testing, architecture/boundaries, security/privacy, documentation, collaboration/review, and governance/evolution.
7. Check every proposed principle for a rationale, observable practice, validation criterion, scope, and contradiction with existing principles.
8. When coverage is sufficient and blocking questions are resolved, invoke `speckit-constitution` with explicit instructions to write `.specify/memory/constitution.draft.md`, never the final file.
9. Present the draft and a concise diff for human approval. If rejected, record the reason and return to the affected question/theme.
10. After approval, update the final constitution, record approval metadata, validate required principles, and mark the workflow completed.

## Update rules

- Preserve existing principles unless the interview establishes that they are obsolete, contradictory, or intentionally changed.
- Explain every proposed change with evidence, user decision, impact, and validation consequence.
- Do not silently rewrite wording that changes meaning.
- Keep the upstream Spec Kit constitution format recognizable.

## State and resumption

Persist `constitutionInterview` in `.specify/turbo/state.json` with mode, status, current theme, current question, draft path, interview path, and confidence. On resume, load the saved interview and continue from `currentQuestion`; do not repeat completed diagnosis or questions.

## Blocking conditions

Set the interview to `blocked` and stop when repository evidence is insufficient, answers conflict, a required decision is missing, the upstream draft command fails, or approval is absent. Never treat a rejected, incomplete, or failed draft as an approved constitution.

## Handoff contract

Every handoff must include objective, evidence reviewed, themes covered, answered and open questions, decisions, contradictions, draft path, validation status, approval status, risks, and next action. The orchestrator verifies these artifacts rather than accepting a completion claim alone.
