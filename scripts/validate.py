#!/usr/bin/env python3
"""Validate Spec Kit Turbo schemas, templates, workflows, and skills."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by local setup failures
    print(
        "Missing validation dependencies. Run: python3 -m pip install -r requirements-dev.txt",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def validate_instance(instance: Any, schema: Any, label: str) -> None:
    if instance is None or schema is None:
        return
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        fail(f"{label}: {location}: {error.message}")


def parse_skill(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail(f"{path.relative_to(ROOT)}: missing YAML front matter")
        return None
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        fail(f"{path.relative_to(ROOT)}: invalid front matter: {exc}")
        return None
    if not isinstance(metadata, dict):
        fail(f"{path.relative_to(ROOT)}: front matter must be an object")
        return None
    return metadata


def main() -> int:
    schema_paths = sorted((ROOT / "schemas").glob("*.schema.json"))
    if not schema_paths:
        fail("schemas/: no JSON schemas found")

    schemas: dict[str, Any] = {}
    for path in schema_paths:
        schema = load_json(path)
        if schema is None:
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema exposes several schema exceptions
            fail(f"{path.relative_to(ROOT)}: invalid JSON Schema: {exc}")
        schemas[path.name] = schema

    required_templates = {
        "project.yml",
        "state.json",
        "spec.md",
        "clarifications.md",
        "plan.md",
        "tasks.md",
        "constitution-interview.md",
        "constitution.draft.md",
        "visual-spec.md",
        "delivery-summary.md",
        "bug-evidence.md",
        "root-cause.md",
        "refactor-analysis.md",
    }
    existing_templates = {
        path.name for path in (ROOT / "templates").iterdir() if path.is_file()
    } if (ROOT / "templates").exists() else set()
    for missing in sorted(required_templates - existing_templates):
        fail(f"templates/{missing}: required template is missing")

    project = load_yaml(ROOT / "templates" / "project.yml")
    validate_instance(
        project,
        schemas.get("project-profile.schema.json"),
        "templates/project.yml",
    )

    state = load_json(ROOT / "templates" / "state.json")
    validate_instance(
        state,
        schemas.get("workflow-state.schema.json"),
        "templates/state.json",
    )

    manifest = load_json(ROOT / "manifest.json")
    validate_instance(manifest, schemas.get("manifest.schema.json"), "manifest.json")

    skills: dict[str, Path] = {}
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        metadata = parse_skill(path)
        if metadata is None:
            continue
        name = metadata.get("name")
        description = metadata.get("description")
        if not isinstance(name, str) or not name:
            fail(f"{path.relative_to(ROOT)}: front matter requires a non-empty name")
            continue
        if name != path.parent.name:
            fail(
                f"{path.relative_to(ROOT)}: skill name '{name}' must match directory '{path.parent.name}'"
            )
        if not isinstance(description, str) or not description.strip():
            fail(f"{path.relative_to(ROOT)}: front matter requires a description")
        if name in skills:
            fail(f"{path.relative_to(ROOT)}: duplicate skill name '{name}'")
        skills[name] = path

    if "turbo-orchestrator" not in skills:
        fail("skills/: turbo-orchestrator is required")

    allowed_classifications = set(
        schemas.get("workflow-state.schema.json", {})
        .get("properties", {})
        .get("classification", {})
        .get("enum", [])
    )
    workflow_classifications: dict[str, Path] = {}
    workflow_count = 0
    supported_conditions = {"visual_input_present", "visual_input_absent_or_completed"}
    supported_checkpoints = {"always", "when_configured"}

    for path in sorted((ROOT / "workflows").glob("*.yml")):
        workflow_count += 1
        data = load_yaml(path)
        if not isinstance(data, dict):
            fail(f"{path.relative_to(ROOT)}: workflow must be an object")
            continue

        for key in ("name", "version", "classification", "state_file", "phases"):
            if key not in data:
                fail(f"{path.relative_to(ROOT)}: missing required key '{key}'")

        name = data.get("name")
        if name != path.stem:
            fail(f"{path.relative_to(ROOT)}: name '{name}' must match filename '{path.stem}'")

        classification = data.get("classification")
        if classification not in allowed_classifications:
            fail(f"{path.relative_to(ROOT)}: unsupported classification '{classification}'")
        elif classification in workflow_classifications:
            previous = workflow_classifications[classification].relative_to(ROOT)
            fail(
                f"{path.relative_to(ROOT)}: classification '{classification}' already handled by {previous}"
            )
        else:
            workflow_classifications[classification] = path

        phases = data.get("phases")
        if not isinstance(phases, list) or not phases:
            fail(f"{path.relative_to(ROOT)}: phases must be a non-empty list")
            continue

        phase_ids: set[str] = set()
        provided_facts: set[str] = set()
        for index, phase in enumerate(phases):
            label = f"{path.relative_to(ROOT)}: phases[{index}]"
            if not isinstance(phase, dict):
                fail(f"{label}: phase must be an object")
                continue

            phase_id = phase.get("id")
            if not isinstance(phase_id, str) or not phase_id:
                fail(f"{label}: phase requires a non-empty id")
            elif phase_id in phase_ids:
                fail(f"{label}: duplicate phase id '{phase_id}'")
            else:
                phase_ids.add(phase_id)

            owner = phase.get("owner")
            if not isinstance(owner, str) or not owner:
                fail(f"{label}: phase requires an owner")
            elif owner.startswith("turbo-") and owner not in skills:
                fail(f"{label}: referenced skill '{owner}' does not exist")

            gate = phase.get("gate")
            requirements = gate.get("require") if isinstance(gate, dict) else None
            if not isinstance(requirements, list) or not requirements:
                fail(f"{label}: gate.require must be a non-empty list")
            elif len(requirements) != len(set(requirements)):
                fail(f"{label}: gate.require contains duplicates")

            outputs = phase.get("outputs", [])
            if outputs is not None and (not isinstance(outputs, list) or not all(isinstance(item, str) and item for item in outputs)):
                fail(f"{label}: outputs must be a list of non-empty paths")

            condition = phase.get("condition")
            if condition is not None and condition not in supported_conditions:
                fail(f"{label}: unsupported condition '{condition}'")

            checkpoint = phase.get("human_checkpoint")
            if checkpoint is not None and checkpoint not in supported_checkpoints:
                fail(f"{label}: unsupported human_checkpoint '{checkpoint}'")

            facts_before_phase = set(provided_facts)
            preconditions = phase.get("preconditions", [])
            if preconditions is not None and (not isinstance(preconditions, list) or not all(isinstance(item, str) and item for item in preconditions)):
                fail(f"{label}: preconditions must be a list of non-empty facts")
            elif isinstance(preconditions, list):
                unresolved = set(preconditions) - facts_before_phase
                if unresolved:
                    fail(f"{label}: preconditions must be provided by an earlier phase: {', '.join(sorted(unresolved))}")

            provides = phase.get("provides", [])
            if provides is not None and (not isinstance(provides, list) or not all(isinstance(item, str) and item for item in provides)):
                fail(f"{label}: provides must be a list of non-empty facts")
            elif isinstance(provides, list):
                duplicates = set(provides) & provided_facts
                if duplicates:
                    fail(f"{label}: facts are already provided by another phase: {', '.join(sorted(duplicates))}")
                provided_facts.update(provides)

            invokes = phase.get("invokes", [])
            if invokes is not None and not isinstance(invokes, list):
                fail(f"{label}: invokes must be a list")
            elif isinstance(invokes, list):
                for invoked in invokes:
                    if isinstance(invoked, str) and invoked.startswith("turbo-") and invoked not in skills:
                        fail(f"{label}: invoked skill '{invoked}' does not exist")
                    if isinstance(invoked, str) and invoked.startswith("speckit-") and invoked not in {
                        "speckit-constitution", "speckit-specify", "speckit-clarify",
                        "speckit-plan", "speckit-tasks", "speckit-analyze",
                        "speckit-checklist", "speckit-implement",
                    }:
                        fail(f"{label}: unsupported Spec Kit command '{invoked}'")

    if workflow_count == 0:
        fail("workflows/: no workflows found")
    missing_workflows = allowed_classifications - set(workflow_classifications)
    if missing_workflows:
        fail("workflows/: classifications without a workflow: " + ", ".join(sorted(missing_workflows)))

    if ERRORS:
        print(f"Validation failed with {len(ERRORS)} error(s):", file=sys.stderr)
        for message in ERRORS:
            print(f"- {message}", file=sys.stderr)
        return 1

    print(
        "Validation passed: "
        f"{len(schema_paths)} schemas, {len(existing_templates)} templates, "
        f"{len(skills)} skills, {workflow_count} workflows."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
