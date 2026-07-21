#!/usr/bin/env python3
"""Diagnose a project configured with Spec Kit Turbo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # The doctor remains useful without optional YAML support.
    yaml = None

REQUIRED_STATE_KEYS = {
    "version",
    "workId",
    "classification",
    "workflow",
    "status",
    "currentPhase",
    "phases",
    "decisions",
    "openQuestions",
    "validations",
    "nextAction",
    "updatedAt",
}
PLACEHOLDER_PREFIXES = ("replace-with-", "change-me")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.successes: list[str] = []

    def ok(self, message: str) -> None:
        self.successes.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def render(self) -> None:
        for message in self.successes:
            print(f"✓ {message}")
        for message in self.warnings:
            print(f"! {message}")
        for message in self.errors:
            print(f"✗ {message}")
        print(
            f"\nSummary: {len(self.successes)} passed, "
            f"{len(self.warnings)} warning(s), {len(self.errors)} error(s)."
        )


def read_json(path: Path, report: Report) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.error(f"Missing {path}")
        return None
    except json.JSONDecodeError as exc:
        report.error(f"Invalid JSON in {path}: {exc}")
        return None
    if not isinstance(value, dict):
        report.error(f"{path} must contain a JSON object")
        return None
    return value


def check_project_profile(root: Path, report: Report) -> None:
    path = root / ".specify" / "turbo" / "project.yml"
    if not path.exists():
        report.error("Missing .specify/turbo/project.yml")
        return

    text = path.read_text(encoding="utf-8")
    if yaml is None:
        required_sections = ("project:", "workflow:", "quality:", "commands:")
        missing = [section for section in required_sections if section not in text]
        if missing:
            report.error(f"project.yml is missing sections: {', '.join(missing)}")
        else:
            report.ok("Project profile has the required sections")
        report.warn("PyYAML is not installed; project.yml received structural checks only")
        return

    try:
        profile = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        report.error(f"Invalid YAML in project.yml: {exc}")
        return

    if not isinstance(profile, dict):
        report.error("project.yml must contain an object")
        return

    missing_sections = {
        "project",
        "workflow",
        "quality",
        "commands",
    } - set(profile)
    if missing_sections:
        report.error(f"project.yml is missing sections: {', '.join(sorted(missing_sections))}")
        return

    project = profile.get("project")
    if not isinstance(project, dict) or not all(project.get(key) for key in ("name", "type", "stack")):
        report.error("project.yml must define project.name, project.type, and project.stack")
    else:
        report.ok(
            f"Project profile loaded for {project['name']} ({project['type']}/{project['stack']})"
        )

    commands = profile.get("commands")
    quality = profile.get("quality")
    if not isinstance(commands, dict) or not isinstance(quality, dict):
        report.error("project.yml quality and commands must be objects")
        return

    gate_to_command = {
        "lint": "lint",
        "unit_tests": "test",
        "build": "build",
    }
    for gate, command_name in gate_to_command.items():
        if quality.get(gate) is True:
            command = commands.get(command_name)
            if not isinstance(command, str) or not command.strip():
                report.error(f"Quality gate '{gate}' is enabled but commands.{command_name} is missing")
            elif command.startswith(PLACEHOLDER_PREFIXES):
                report.warn(f"commands.{command_name} still contains the template placeholder")
            else:
                report.ok(f"Quality gate '{gate}' has a configured command")

    install_command = commands.get("install")
    if isinstance(install_command, str) and install_command.startswith(PLACEHOLDER_PREFIXES):
        report.warn("commands.install still contains the template placeholder")


def check_state(root: Path, report: Report) -> None:
    path = root / ".specify" / "turbo" / "state.json"
    state = read_json(path, report)
    if state is None:
        return

    missing = REQUIRED_STATE_KEYS - set(state)
    if missing:
        report.error(f"state.json is missing fields: {', '.join(sorted(missing))}")
        return

    phases = state.get("phases")
    if not isinstance(phases, list) or not phases:
        report.error("state.json phases must be a non-empty list")
    else:
        report.ok(
            f"Workflow state loaded: {state.get('workflow')} / {state.get('currentPhase')} / {state.get('status')}"
        )

    if state.get("workId") == "replace-with-work-id":
        report.warn("state.json still uses the template workId")


def check_installation(root: Path, report: Report) -> None:
    if not (root / ".git").exists():
        report.warn("Target does not appear to be a Git repository")
    else:
        report.ok("Git repository detected")

    if not (root / ".specify").exists():
        report.error("Spec Kit directory .specify is missing")
    else:
        report.ok("Spec Kit directory detected")

    agents = root / "AGENTS.md"
    if not agents.exists():
        report.error("AGENTS.md is missing")
    elif "speckit-turbo:start" not in agents.read_text(encoding="utf-8"):
        report.warn("AGENTS.md does not contain the Spec Kit Turbo managed block")
    else:
        report.ok("AGENTS.md contains the Spec Kit Turbo integration block")

    skills_root = root / ".agents" / "skills"
    skill_files = sorted(skills_root.glob("turbo-*/SKILL.md")) if skills_root.exists() else []
    if not skill_files:
        report.error("No Turbo skills found under .agents/skills")
    else:
        names = {path.parent.name for path in skill_files}
        report.ok(f"{len(names)} Turbo skill(s) installed")
        for required in ("turbo-orchestrator", "turbo-product-owner", "turbo-architect", "turbo-test-engineer", "turbo-code-reviewer"):
            if required not in names:
                report.error(f"Required skill '{required}' is missing")

    runtime = root / ".specify" / "turbo" / "runtime"
    for directory in ("schemas", "workflows"):
        if not (runtime / directory).exists():
            report.error(f"Runtime directory {runtime / directory} is missing")
    if (runtime / "schemas").exists() and (runtime / "workflows").exists():
        report.ok("Workflow and schema runtime files are installed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Project directory to diagnose")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a failure code when warnings are present",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Target directory does not exist: {root}", file=sys.stderr)
        return 2

    report = Report()
    check_installation(root, report)
    check_project_profile(root, report)
    check_state(root, report)
    report.render()

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
