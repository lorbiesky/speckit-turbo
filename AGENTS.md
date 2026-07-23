# AGENTS.md

## Mission

Evolve Spec Kit Turbo as a reusable native bundle on top of GitHub Spec Kit. Prefer composition over forks and keep upstream concepts recognizable.

## Operating rules

1. Inspect the extension, workflows, bundle and version contract before changing behavior.
2. Keep the public interface in the `speckit.turbo.*` namespace; never replace `speckit.*` upstream commands.
3. Do not introduce a custom runtime, npm package, `node_modules`, `.specify/turbo/`, or parallel workflow state.
4. Keep gates and resumability in native Spec Kit workflows.
5. Preserve traceability from requirement through acceptance, task, code, validation and review.
6. Preserve project-specific conventions; the extension config is optional and local to `.specify/extensions/turbo/`.
7. Persist visual references only after confirming Git ignores `.specify/visual-references/`.
8. Never replace the final constitution before a Socratic interview, draft and explicit human approval.
9. Run structural and documentation validation before declaring work complete.

## Repository structure

- `extension.yml`, `commands/`, `templates/`, `scripts/`: Turbo extension assets.
- `workflows/<id>/workflow.yml`: native installable workflows.
- `bundle.yml`: versioned composition of the extension and workflows.
- `catalogs/`: extension, workflow and bundle discovery metadata.
- `VERSION`: single release version.
- `docs/`: public operating and maintenance documentation.
