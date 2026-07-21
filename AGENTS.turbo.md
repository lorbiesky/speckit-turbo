# Spec Kit Turbo shared rules

Use GitHub Spec Kit as the source of truth for specification artifacts and commands. Turbo composes those capabilities with local workflows and specialist skills; it does not replace or fork Spec Kit.

## Operating rules

- Classify each request as feature, bugfix, or refactor before implementation.
- Load `.specify/turbo/project.yml` and the active workflow state before continuing work.
- Keep product decisions separate from technical decisions.
- Preserve traceability from requirement to acceptance criterion, task, code, test, and review.
- Pause for configured human checkpoints, material ambiguity, scope expansion, or consequential risk.
- Record assumptions, decisions, blockers, deviations, validation evidence, and the next safe action.
- Do not advance a phase without its declared gate evidence.
- Treat TDD as an implementation prerequisite when `tdd.enabled: true`: record red before production code, then green and refactor evidence.
- Use a documented, human-approved exception only when TDD is not applicable; never bypass a TDD gate by editing `state.json`.
- Use `$turbo` to classify and start work, then `$turbo-status` or `$turbo-resume` when needed. Workflow state is managed internally by the orchestrator; do not ask the user to run Node commands or edit phase status by hand.
- Create or update the project constitution through the repository-aware Socratic interview; never replace the final constitution before explicit approval.
- Prefer the smallest reviewable change and existing project conventions.

## Handoffs

Specialist skills must state their objective, inputs, constraints, output artifact, unresolved questions, risks, and stop condition. The orchestrator verifies artifacts instead of accepting completion claims without evidence.

## Completion

Delivery is complete only when acceptance criteria map to implementation and validation, configured quality gates have evidence, blocking review findings are resolved, and the delivery summary records risks and follow-ups.
