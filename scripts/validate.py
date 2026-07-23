#!/usr/bin/env python3
"""Validate the repository's native Spec Kit component contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
COMMANDS = {
    "start", "feature", "bugfix", "refactor", "maintenance", "hotfix",
    "discovery", "constitution", "status", "resume", "tdd", "visual",
}
WORKFLOWS = {
    "turbo-feature", "turbo-bugfix", "turbo-refactor", "turbo-maintenance",
    "turbo-hotfix", "turbo-discovery", "turbo-constitution",
}
IMPLEMENTATION_WORKFLOWS = WORKFLOWS - {"turbo-discovery", "turbo-constitution"}
PUBLIC_DOCS = [ROOT / "README.md", *(ROOT / "docs").glob("*.md")]
FORBIDDEN_PUBLIC_TERMS = ("npx speckit-turbo", "$turbo-", "node .specify/turbo")
CONSTITUTION_CONFIG = {
    "enabled": bool,
    "require_human_approval": bool,
    "question_format": str,
    "option_count": int,
    "show_recommendation": bool,
    "adaptive_follow_up": bool,
    "require_constitutional_scope": bool,
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_extension(errors: list[str]) -> None:
    data = load_yaml(ROOT / "extension.yml")
    if data.get("schema_version") != "1.0":
        fail(errors, "extension.yml must use schema_version 1.0")
    if data.get("extension", {}).get("id") != "turbo":
        fail(errors, "extension id must be turbo")
    if data.get("extension", {}).get("version") != VERSION:
        fail(errors, "extension version must match VERSION")
    entries = data.get("provides", {}).get("commands", [])
    actual = {item.get("name", "").removeprefix("speckit.turbo.") for item in entries}
    if actual != COMMANDS:
        fail(errors, f"extension commands must equal {sorted(COMMANDS)}")
    for item in entries:
        name, file_name = item.get("name", ""), item.get("file", "")
        if not name.startswith("speckit.turbo."):
            fail(errors, f"invalid Turbo command namespace: {name}")
        if not (ROOT / file_name).is_file():
            fail(errors, f"missing command asset: {file_name}")
    config = data.get("provides", {}).get("config", [])
    if not any(item.get("name") == "turbo-config.yml" and (ROOT / item.get("template", "")).is_file() for item in config):
        fail(errors, "extension must expose the Turbo configuration template")


def validate_constitution_contract(errors: list[str]) -> None:
    command = (ROOT / "commands/speckit.turbo.constitution.md").read_text(encoding="utf-8").lower()
    required_command_terms = (
        "constitutional",
        "not_constitutional",
        "one evidence-based constitutional decision at a time",
        "three contextual policy alternatives",
        "recommendation",
        "free-text",
        "normalized principle",
        "observable practice",
        "validation criterion",
        "do not alter `.specify/memory/constitution.md`",
    )
    for term in required_command_terms:
        if term not in command:
            fail(errors, f"constitution command is missing scope rule: {term}")

    config = load_yaml(ROOT / "turbo-config.yml").get("constitution", {})
    if set(config) != set(CONSTITUTION_CONFIG):
        fail(errors, "turbo-config.yml constitution settings must match the structured question contract")
    for key, expected_type in CONSTITUTION_CONFIG.items():
        if key in config and not isinstance(config[key], expected_type):
            fail(errors, f"constitution config {key} must be {expected_type.__name__}")
    if config.get("question_format") != "single_choice_with_free_text":
        fail(errors, "constitution question_format must default to single_choice_with_free_text")
    if config.get("option_count") != 3:
        fail(errors, "constitution option_count must default to 3")
    if config.get("require_constitutional_scope") is not True:
        fail(errors, "constitution scope protection must be enabled by default")

    interview = (ROOT / "templates/constitution-interview.md").read_text(encoding="utf-8").lower()
    for term in (
        "candidate classification",
        "candidates discarded as operational",
        "constitutional principle under evaluation",
        "policy options presented",
        "recommended option",
        "free-text answer",
        "normalized principle",
        "observable practice",
        "validation criterion",
        "routing, if rejected as operational",
    ):
        if term not in interview:
            fail(errors, f"constitution interview template is missing: {term}")

    draft = (ROOT / "templates/constitution.draft.md").read_text(encoding="utf-8").lower()
    for term in ("constitutional scope confirmed", "observable practice", "validation criterion", "limits and auditable exceptions"):
        if term not in draft:
            fail(errors, f"constitution draft template is missing: {term}")


def validate_workflows(errors: list[str]) -> None:
    actual = {path.parent.name for path in (ROOT / "workflows").glob("*/workflow.yml")}
    if actual != WORKFLOWS:
        fail(errors, f"workflows must equal {sorted(WORKFLOWS)}")
    for workflow_id in WORKFLOWS:
        data = load_yaml(ROOT / "workflows" / workflow_id / "workflow.yml")
        if data.get("workflow", {}).get("id") != workflow_id:
            fail(errors, f"{workflow_id}: id mismatch")
        if data.get("workflow", {}).get("version") != VERSION:
            fail(errors, f"{workflow_id}: version must match VERSION")
        if data.get("requires", {}).get("speckit_version") != ">=0.11.4":
            fail(errors, f"{workflow_id}: must require Spec Kit >=0.11.4")
        steps = data.get("steps", [])
        refs = {step.get("command") for step in steps if step.get("command")}
        if not refs:
            fail(errors, f"{workflow_id}: must contain command steps")
        for command in refs:
            if command.startswith("speckit.turbo.") and command.removeprefix("speckit.turbo.") not in COMMANDS:
                fail(errors, f"{workflow_id}: references unknown command {command}")
        if workflow_id in IMPLEMENTATION_WORKFLOWS:
            ids = {step.get("id") for step in steps}
            if "tdd" not in ids or "implement" not in ids:
                fail(errors, f"{workflow_id}: implementation requires a tdd and implement step")
        if not any(step.get("type") == "gate" for step in steps):
            fail(errors, f"{workflow_id}: must provide a native human gate")


def validate_bundle_and_catalogs(errors: list[str]) -> None:
    bundle = load_yaml(ROOT / "bundle.yml")
    if bundle.get("bundle", {}).get("version") != VERSION:
        fail(errors, "bundle version must match VERSION")
    refs = {item.get("id") for item in bundle.get("provides", {}).get("workflows", [])}
    if refs != WORKFLOWS:
        fail(errors, "bundle must compose every Turbo workflow")
    if bundle.get("provides", {}).get("extensions") != [{"id": "turbo", "version": VERSION}]:
        fail(errors, "bundle must compose extension turbo at VERSION")
    catalogs = {
        "extensions.json": ("extensions", {"turbo"}),
        "workflows.json": ("workflows", WORKFLOWS),
        "bundles.json": ("bundles", {"speckit-turbo"}),
    }
    for filename, (key, expected) in catalogs.items():
        data = json.loads((ROOT / "catalogs" / filename).read_text(encoding="utf-8"))
        if set(data.get(key, {})) != expected:
            fail(errors, f"{filename}: entries must equal {sorted(expected)}")
        if VERSION not in json.dumps(data):
            fail(errors, f"{filename}: must contain VERSION")
    for entry in json.loads((ROOT / "catalogs" / "workflows.json").read_text(encoding="utf-8"))["workflows"].values():
        if "/v" + VERSION + "/workflows/" not in entry["url"]:
            fail(errors, "workflow catalog must resolve immutable tagged raw workflow files")


def validate_docs(errors: list[str]) -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_DOCS).lower()
    for term in FORBIDDEN_PUBLIC_TERMS:
        if term in text:
            fail(errors, f"public documentation contains retired runtime term: {term}")
    for command in COMMANDS:
        if f"$speckit-turbo-{command}" not in text:
            fail(errors, f"public documentation does not mention $speckit-turbo-{command}")
    for command in ("specify extension", "specify workflow", "specify bundle", "specify self upgrade"):
        if command not in text:
            fail(errors, f"public documentation does not explain {command}")
    if "install-turbo.sh" not in text or "install-turbo.ps1" not in text:
        fail(errors, "public documentation must expose the one-command installer")


def validate_installers(errors: list[str]) -> None:
    shell_installer = ROOT / "scripts" / "install-turbo.sh"
    powershell_installer = ROOT / "scripts" / "Install-Turbo.ps1"
    if not shell_installer.is_file() or not powershell_installer.is_file():
        fail(errors, "both one-command installers must exist")
    if shell_installer.is_file():
        text = shell_installer.read_text(encoding="utf-8")
        for catalog in ("extensions.json", "workflows.json", "bundles.json"):
            if catalog not in text:
                fail(errors, f"shell installer does not reference {catalog}")
        if "git clone" in text or "node_modules" in text:
            fail(errors, "shell installer must not clone or install a Node runtime")
        if f"/v{VERSION}" not in text:
            fail(errors, "shell installer must use an immutable release tag matching VERSION")
        if '"$SPECIFY_BIN" workflow update' in text:
            fail(errors, "shell installer must not use interactive workflow update")
    if powershell_installer.is_file():
        text = powershell_installer.read_text(encoding="utf-8")
        if "Select-String" in text:
            fail(errors, "PowerShell installer must use literal catalog matching")
        if f"/v{VERSION}" not in text:
            fail(errors, "PowerShell installer must use an immutable release tag matching VERSION")
        if "& specify workflow update" in text:
            fail(errors, "PowerShell installer must not use interactive workflow update")


def main() -> int:
    errors: list[str] = []
    if not re.fullmatch(r"\d+\.\d+\.\d+", VERSION):
        fail(errors, "VERSION must be semantic version X.Y.Z")
    validate_extension(errors)
    validate_constitution_contract(errors)
    validate_workflows(errors)
    validate_bundle_and_catalogs(errors)
    validate_docs(errors)
    validate_installers(errors)
    if errors:
        print("Native Spec Kit Turbo validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Native Spec Kit Turbo {VERSION} contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
