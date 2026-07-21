#!/usr/bin/env python3
"""Diagnose a project configured with Spec Kit Turbo."""

from __future__ import annotations

import argparse
import json
import subprocess
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
    "deviations",
    "nextAction",
    "updatedAt",
}
PLACEHOLDER_PREFIXES = ("replace-with-", "change-me")
VISUAL_GITIGNORE_START = "# speckit-turbo:start"
VISUAL_GITIGNORE_END = "# speckit-turbo:end"
VISUAL_GITIGNORE_ENTRY = ".specify/visual-references/"


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

    spec_kit = profile.get("specKit")
    if spec_kit is not None:
        if not isinstance(spec_kit, dict):
            report.error("project.yml specKit must be an object")

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
    if "deviations" in missing and state.get("version") == "1.0":
        missing.remove("deviations")
        report.warn("state.json uses the legacy 1.0 format without deviations")
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

    interview = state.get("constitutionInterview")
    if interview is not None:
        if not isinstance(interview, dict):
            report.error("state.json constitutionInterview must be an object")
        else:
            status = interview.get("status")
            report.ok(f"Constitution interview state: {status}")
            if status in {"blocked", "awaiting_approval", "draft_ready", "rejected"}:
                report.warn(f"Constitution interview requires attention: {status}")


def check_manifest(root: Path, report: Report) -> None:
    path = root / ".specify" / "turbo" / "manifest.json"
    manifest = read_json(path, report)
    if manifest is None:
        return
    version = manifest.get("turboVersion")
    if not isinstance(version, str) or not version:
        report.error("manifest.json must define turboVersion")
    else:
        report.ok(f"Spec Kit Turbo version {version} installed")
    installation = manifest.get("installation")
    if isinstance(installation, dict):
        mode = installation.get("mode")
        integration = installation.get("integration", "unknown")
        report.ok(f"Installation mode: {mode}; Spec Kit integration: {integration}")
        if installation.get("specKitVersion"):
            report.ok(f"Spec Kit upstream version: {installation['specKitVersion']}")
        if mode == "clean" and not installation.get("specKitVersion"):
            report.error("Clean installation has no recorded Spec Kit version")
        if integration != "codex":
            report.warn("Turbo skills are Codex-first; upstream integration is preserved but not adapted")
    else:
        report.warn("Legacy Turbo manifest without installation metadata")


def check_spec_kit(root: Path, report: Report) -> None:
    specify = root / ".specify"
    if not specify.exists():
        return
    signals = [
        str(path.relative_to(root))
        for path in (specify / "memory/constitution.md", specify / "templates", specify / "scripts")
        if path.exists()
    ]
    if signals:
        report.ok(f"Structured Spec Kit installation detected: {', '.join(signals)}")
    else:
        report.warn(".specify exists but no structured Spec Kit signals were detected")

    backups = root / ".specify" / "turbo" / "backups"
    if backups.exists():
        report.ok(f"Turbo backups available: {len(list(backups.iterdir()))} set(s)")
        gitignore = root / ".gitignore"
        ignored = gitignore.exists() and any(
            line.strip() in {".specify/turbo/backups/", ".specify/turbo/backups"}
            for line in gitignore.read_text(encoding="utf-8").splitlines()
        )
        if ignored:
            report.ok("Turbo backup directory is protected by .gitignore")
        else:
            report.warn("Turbo backups are not protected by .gitignore")


def check_constitution(root: Path, report: Report) -> None:
    profile_path = root / ".specify" / "turbo" / "project.yml"
    enabled = True
    if yaml is not None and profile_path.exists():
        try:
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            enabled = profile.get("constitution", {}).get("enabled", True)
        except yaml.YAMLError:
            return
    if not enabled:
        report.ok("Constitution workflow is disabled by project profile")
        return

    final_path = root / ".specify" / "memory" / "constitution.md"
    interview_path = root / ".specify" / "memory" / "constitution-interview.md"
    draft_path = root / ".specify" / "memory" / "constitution.draft.md"
    if final_path.exists():
        report.ok("Project constitution exists")
    else:
        report.warn("Constitution is not created yet; start the constitution workflow when project rules are ready")
    if interview_path.exists():
        report.ok("Constitution interview artifact exists")
    if draft_path.exists():
        report.warn("Constitution draft is present and must be approved before finalization")
    if draft_path.exists() and not interview_path.exists():
        report.error("Constitution draft exists without its interview record")


def check_visual(root: Path, report: Report) -> None:
    profile_path = root / ".specify" / "turbo" / "project.yml"
    enabled = True
    persist = False
    references_path = ".specify/visual-references"
    if yaml is not None and profile_path.exists():
        try:
            profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            visual = profile.get("visual", {}) or {}
            enabled = visual.get("enabled", True)
            persist = visual.get("persist_references", False)
            references_path = visual.get("references_path", references_path)
            if visual.get("visual_regression") is True:
                command = visual.get("command")
                if not isinstance(command, str) or not command.strip():
                    report.error("visual_regression is enabled but visual.command is missing")
        except yaml.YAMLError:
            return
    if not enabled:
        report.ok("Visual workflow is disabled by project profile")
        return

    references = (root / references_path).resolve()
    try:
        references.relative_to(root.resolve())
    except ValueError:
        report.error("visual.references_path must remain inside the project")
        return

    gitignore = root / ".gitignore"
    content = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    start = content.find(VISUAL_GITIGNORE_START)
    end = content.find(VISUAL_GITIGNORE_END)
    block_valid = start >= 0 and end > start and VISUAL_GITIGNORE_ENTRY in content[start:end]
    if persist and not block_valid:
        report.error("Visual references are enabled but the managed .gitignore block is missing or invalid")
    elif block_valid:
        report.ok("Visual reference directory has a managed .gitignore rule")

    if references.exists():
        files = [path for path in references.rglob("*") if path.is_file()]
        unignored = []
        for path in files:
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(path.relative_to(root))],
                cwd=root,
                capture_output=True,
            )
            if result.returncode != 0:
                unignored.append(str(path.relative_to(root)))
        if unignored:
            report.error("Visual references are not ignored: " + ", ".join(unignored))
        elif files:
            report.ok(f"{len(files)} visual reference(s) are ignored by Git")

    visual_spec = root / "visual-spec.md"
    state_path = root / ".specify" / "turbo" / "state.json"
    if visual_spec.exists():
        report.ok("Visual specification exists")
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            analysis = state.get("visualAnalysis", {})
            if analysis.get("status") == "blocked":
                report.warn("Visual analysis is blocked")
            if analysis.get("status") == "completed" and not visual_spec.exists():
                report.error("Visual analysis is completed but visual-spec.md is missing")
        except json.JSONDecodeError:
            pass


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
        for required in ("turbo-orchestrator", "turbo-product-owner", "turbo-architect", "turbo-implementation-specialist", "turbo-test-engineer", "turbo-code-reviewer", "turbo-constitution-facilitator", "turbo-visual-specifier"):
            if required not in names:
                report.error(f"Required skill '{required}' is missing")

    runtime = root / ".specify" / "turbo" / "runtime"
    for directory in ("schemas", "workflows"):
        if not (runtime / directory).exists():
            report.error(f"Runtime directory {runtime / directory} is missing")
    if (runtime / "schemas").exists() and (runtime / "workflows").exists():
        report.ok("Workflow and schema runtime files are installed")
    if not (root / ".specify" / "turbo" / "workflow_runtime.py").exists():
        report.error("Workflow runtime is missing")
    else:
        report.ok("Dynamic workflow runtime is installed")
    constitution_templates = root / ".specify" / "turbo" / "templates"
    for template in ("constitution-interview.md", "constitution.draft.md", "visual-spec.md"):
        if not (constitution_templates / template).exists():
            report.error(f"Missing installed Turbo template: {template}")


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
    check_spec_kit(root, report)
    check_constitution(root, report)
    check_visual(root, report)
    check_manifest(root, report)
    check_project_profile(root, report)
    check_state(root, report)
    report.render()

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
