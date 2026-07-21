---
name: turbo
description: Start or resume Spec Kit Turbo work from a natural-language request. Use for any feature, bug, refactor, discovery, maintenance, hotfix, constitution request, or an attached screenshot when the user has not selected a workflow.
---

# Turbo

Load `AGENTS.md`, `.specify/turbo/project.yml`, and the state if it is not the untouched template. If active state matches the request, resume it; otherwise classify the request and explain any material ambiguity before starting.

Start or resume the selected workflow through the agent workflow contract. Treat attached screenshots as workflow inputs automatically. Report the selected workflow, owner, gate, artifacts, and next action. Delegate to the owner skill; do not implement before the required product and planning phases.

Use `turbo-orchestrator` for routing and its stop conditions. Preserve upstream `$speckit-*` commands; invoke them only in their declared Turbo phase.
