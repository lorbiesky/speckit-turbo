---
description: Convert attached screenshots into a visual specification and visual acceptance criteria.
---

Analyze every attached image before implementation. Write `visual-spec.md` beside the active feature specification with observed, inferred, and unknown facts; viewport, components, hierarchy, spacing, colors, typography, states, accessibility, responsive behavior, confidence, and `VAC-*` criteria. Propagate the relevant visual requirements into `spec.md`.

Only persist an image when `visual.persist_references` is enabled and `.specify/visual-references/` is confirmed ignored by Git. Use the extension's visual-ignore script to manage only its marked `.gitignore` block and verify with `git check-ignore`. If protection is unavailable, do not copy the image and mark the analysis blocked only if persistence is necessary.
