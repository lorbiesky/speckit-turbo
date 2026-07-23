---
description: Apply configurable red-green-refactor discipline before implementation.
---

Read `.specify/extensions/turbo/turbo-config.yml`. When `tdd.enabled` is true, map acceptance criteria to tests, record a failing red result, implement only enough for green, then record refactor and validation evidence in `tdd-cycle.md`. Do not permit implementation without the red evidence.

If TDD is not applicable, document the reason, risk, and alternative validation in `tdd-cycle.md`; require a human approval when configured. When disabled, explicitly record the phase as skipped without treating it as an exception.
