#!/usr/bin/env python3
"""Drive resumable Spec Kit Turbo workflows from their declarative definitions.

This command deliberately does not execute agent work.  It provides the small,
deterministic part of orchestration: create state, select the next applicable
phase, require declared gate evidence, pause at human checkpoints, and resume.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing PyYAML. Run: python3 -m pip install -r requirements-dev.txt") from exc


ROOT = Path(__file__).resolve().parents[1]
STATE_RELATIVE_PATH = Path(".specify/turbo/state.json")
WORKFLOW_DIR = Path(".specify/turbo/runtime/workflows")


class RuntimeError(Exception):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError(f"Unable to read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a YAML object")
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unable to read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return value


def save_state(path: Path, state: dict[str, Any]) -> None:
    state["updatedAt"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def paths(project: Path) -> tuple[Path, Path, Path]:
    return project / STATE_RELATIVE_PATH, project / ".specify/turbo/project.yml", project / WORKFLOW_DIR


def workflow_for(project: Path, classification: str) -> dict[str, Any]:
    _, _, workflow_dir = paths(project)
    for candidate in workflow_dir.glob("*.yml"):
        workflow = load_yaml(candidate)
        if workflow.get("classification") == classification:
            return workflow
    raise RuntimeError(f"No installed workflow handles classification '{classification}'")


def phase_map(workflow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {phase["id"]: phase for phase in workflow["phases"]}


def configured_checkpoint(profile: dict[str, Any], phase: dict[str, Any]) -> bool:
    checkpoint = phase.get("human_checkpoint")
    if checkpoint == "always":
        return True
    if checkpoint != "when_configured":
        return False
    configured = profile.get("workflow", {}).get("human_checkpoints", [])
    return phase["id"] in configured


def condition_applies(condition: str | None, state: dict[str, Any], profile: dict[str, Any]) -> bool:
    if condition is None:
        return True
    visual = state.get("visualAnalysis", {})
    inputs = visual.get("inputs", [])
    if condition == "visual_input_present":
        return bool(profile.get("visual", {}).get("enabled", True) and inputs)
    if condition == "visual_input_absent_or_completed":
        return not inputs or visual.get("status") in {"completed", "skipped"}
    raise RuntimeError(f"Unsupported workflow condition '{condition}'")


def completed_facts(state: dict[str, Any], workflow: dict[str, Any]) -> set[str]:
    definitions = phase_map(workflow)
    facts: set[str] = set()
    for phase in state["phases"]:
        if phase["status"] == "completed" and phase["gate"].get("passed") is True:
            facts.update(definitions[phase["id"]].get("provides", []))
    return facts


def next_phase(state: dict[str, Any], workflow: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any] | None:
    definitions = phase_map(workflow)
    facts = completed_facts(state, workflow)
    for phase_state in state["phases"]:
        if phase_state["status"] in {"completed", "skipped"}:
            continue
        definition = definitions[phase_state["id"]]
        if not condition_applies(definition.get("condition"), state, profile):
            phase_state["status"] = "skipped"
            phase_state["gate"]["passed"] = True
            phase_state["gate"]["reason"] = f"Condition '{definition.get('condition')}' is not applicable."
            if phase_state["id"] == "visual-analysis":
                state["visualAnalysis"]["status"] = "skipped"
            continue
        missing = [fact for fact in definition.get("preconditions", []) if fact not in facts]
        if missing:
            phase_state["status"] = "blocked"
            phase_state["gate"]["reason"] = "Missing preconditions: " + ", ".join(missing)
            state["status"] = "blocked"
            state["currentPhase"] = phase_state["id"]
            state["nextAction"] = "Resolve the declared preconditions before resuming."
            return phase_state
        phase_state["status"] = "active"
        if phase_state["id"] == "visual-analysis":
            state["visualAnalysis"]["status"] = "active"
        state["status"] = "active"
        state["currentPhase"] = phase_state["id"]
        state["nextAction"] = f"Complete '{phase_state['id']}' and record evidence for every declared gate requirement."
        return phase_state
    state["status"] = "completed"
    state["currentPhase"] = state["phases"][-1]["id"]
    state["nextAction"] = "Workflow completed. Review the delivery summary and follow-ups."
    return None


def new_state(workflow: dict[str, Any], work_id: str, visual_inputs: list[str]) -> dict[str, Any]:
    phases = []
    for definition in workflow["phases"]:
        requirements = definition["gate"]["require"]
        phases.append({
            "id": definition["id"], "status": "pending", "owner": definition["owner"],
            "artifacts": definition.get("outputs", []),
            "gate": {"passed": None, "evidence": [], "requirements": {key: "" for key in requirements}},
        })
    return {
        "version": "1.0", "workId": work_id, "classification": workflow["classification"],
        "workflow": workflow["name"], "status": "draft", "currentPhase": workflow["phases"][0]["id"],
        "phases": phases, "decisions": [], "openQuestions": [], "validations": [], "deviations": [],
        "visualAnalysis": {"status": "not_started", "inputs": visual_inputs, "visualSpecPath": "visual-spec.md",
                           "persistedReferencesPath": ".specify/visual-references", "confidence": "low",
                           "unresolvedQuestions": [], "acceptanceCriteria": []},
        "nextAction": "Start the first applicable workflow phase.", "updatedAt": now(),
    }


def require_active(state: dict[str, Any], phase_id: str) -> dict[str, Any]:
    for phase in state["phases"]:
        if phase["id"] == phase_id:
            if phase["status"] != "active":
                raise RuntimeError(f"Phase '{phase_id}' is {phase['status']}, not active")
            return phase
    raise RuntimeError(f"Unknown phase '{phase_id}'")


def parse_evidence(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        key, separator, evidence = value.partition("=")
        if not separator or not key.strip() or not evidence.strip():
            raise RuntimeError("Evidence must use requirement=evidence")
        parsed[key.strip()] = evidence.strip()
    return parsed


def cmd_start(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    state_path, profile_path, _ = paths(project)
    if state_path.exists() and not args.force:
        existing = load_json(state_path)
        if existing.get("workId") != "replace-with-work-id":
            raise RuntimeError(f"State already exists at {state_path}; use resume or --force")
    profile = load_yaml(profile_path)
    workflow = workflow_for(project, args.classification)
    state = new_state(workflow, args.work_id, args.visual_input)
    next_phase(state, workflow, profile)
    save_state(state_path, state)
    print_status(state, workflow)


def cmd_status(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    state_path, profile_path, _ = paths(project)
    state = load_json(state_path)
    workflow = workflow_for(project, state["classification"])
    profile = load_yaml(profile_path)
    if args.refresh and state["status"] not in {"completed", "cancelled", "paused"}:
        next_phase(state, workflow, profile)
        save_state(state_path, state)
    print_status(state, workflow)


def print_status(state: dict[str, Any], workflow: dict[str, Any]) -> None:
    current = next((phase for phase in state["phases"] if phase["id"] == state["currentPhase"]), None)
    print(f"{state['classification']} / {state['status']} / {state['currentPhase']}")
    if current:
        definition = phase_map(workflow)[current["id"]]
        print(f"Owner: {current.get('owner')}")
        print("Gate requirements: " + ", ".join(definition["gate"]["require"]))
        if current["gate"].get("reason"):
            print("Reason: " + current["gate"]["reason"])
    print("Next action: " + state["nextAction"])


def cmd_complete(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    state_path, profile_path, _ = paths(project)
    state, profile = load_json(state_path), load_yaml(profile_path)
    workflow = workflow_for(project, state["classification"])
    phase = require_active(state, args.phase)
    definition = phase_map(workflow)[args.phase]
    supplied = parse_evidence(args.evidence)
    expected = set(definition["gate"]["require"])
    unexpected = set(supplied) - expected
    if unexpected:
        raise RuntimeError("Evidence references undeclared requirement(s): " + ", ".join(sorted(unexpected)))
    phase["gate"]["requirements"].update(supplied)
    missing = [item for item in definition["gate"]["require"] if not phase["gate"]["requirements"].get(item)]
    if missing:
        raise RuntimeError("Missing evidence for: " + ", ".join(missing))
    phase["gate"]["evidence"] = [f"{key}: {value}" for key, value in phase["gate"]["requirements"].items()]
    phase["gate"]["passed"] = True
    if args.phase == "visual-analysis":
        state["visualAnalysis"]["status"] = "completed"
    if configured_checkpoint(profile, definition):
        phase["status"] = "blocked"
        phase["checkpoint"] = {"status": "awaiting_approval", "note": "Human approval required by project profile."}
        state["status"] = "paused"
        state["nextAction"] = f"Approve or reject the human checkpoint for '{args.phase}'."
    else:
        phase["status"] = "completed"
        next_phase(state, workflow, profile)
    save_state(state_path, state)
    print_status(state, workflow)


def cmd_checkpoint(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    state_path, profile_path, _ = paths(project)
    state, profile = load_json(state_path), load_yaml(profile_path)
    workflow = workflow_for(project, state["classification"])
    phase = next((item for item in state["phases"] if item["id"] == args.phase), None)
    if phase is None or phase.get("checkpoint", {}).get("status") != "awaiting_approval":
        raise RuntimeError(f"Phase '{args.phase}' is not awaiting a human checkpoint")
    if args.approve:
        phase["checkpoint"] = {"status": "approved", "note": args.note or "Approved by human."}
        phase["status"] = "completed"
        next_phase(state, workflow, profile)
    else:
        phase["checkpoint"] = {"status": "rejected", "note": args.note or "Rejected by human."}
        phase["status"] = "blocked"
        state["status"] = "blocked"
        state["currentPhase"] = args.phase
        state["nextAction"] = "Address the rejection, update the phase evidence, then resume it."
    save_state(state_path, state)
    print_status(state, workflow)


def cmd_resume(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    state_path, profile_path, _ = paths(project)
    state, profile = load_json(state_path), load_yaml(profile_path)
    workflow = workflow_for(project, state["classification"])
    if state["status"] == "blocked":
        phase = next(item for item in state["phases"] if item["id"] == state["currentPhase"])
        if phase.get("checkpoint", {}).get("status") == "rejected":
            phase.pop("checkpoint", None)
            phase["gate"] = {"passed": None, "evidence": [], "requirements": {key: "" for key in phase_map(workflow)[phase["id"]]["gate"]["require"]}}
        phase["status"] = "active"
    next_phase(state, workflow, profile)
    save_state(state_path, state)
    print_status(state, workflow)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=".", help="Consumer project directory")
    subcommands = parser.add_subparsers(dest="command", required=True)
    start = subcommands.add_parser("start", help="Create state from a workflow classification")
    start.add_argument("classification", help="Classification declared by an installed workflow")
    start.add_argument("--work-id", required=True)
    start.add_argument("--visual-input", action="append", default=[])
    start.add_argument("--force", action="store_true", help="Replace an existing active state")
    start.set_defaults(handler=cmd_start)
    status = subcommands.add_parser("status", help="Show current work and next action")
    status.add_argument("--refresh", action="store_true", help="Evaluate conditions and preconditions before showing status")
    status.set_defaults(handler=cmd_status)
    complete = subcommands.add_parser("complete", help="Close an active phase with declared evidence")
    complete.add_argument("phase")
    complete.add_argument("--evidence", action="append", default=[], metavar="REQUIREMENT=EVIDENCE")
    complete.set_defaults(handler=cmd_complete)
    checkpoint = subcommands.add_parser("checkpoint", help="Record a required human decision")
    checkpoint.add_argument("phase")
    outcome = checkpoint.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--approve", action="store_true")
    outcome.add_argument("--reject", action="store_true")
    checkpoint.add_argument("--note")
    checkpoint.set_defaults(handler=cmd_checkpoint)
    resume = subcommands.add_parser("resume", help="Resume a blocked phase after its blocker is addressed")
    resume.set_defaults(handler=cmd_resume)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.handler(args)
    except RuntimeError as exc:
        print(f"Workflow runtime: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
