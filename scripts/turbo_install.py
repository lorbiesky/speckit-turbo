#!/usr/bin/env python3
"""Install or adapt Spec Kit Turbo without overwriting upstream Spec Kit assets."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


START_MARKER = "<!-- speckit-turbo:start -->"
END_MARKER = "<!-- speckit-turbo:end -->"
VISUAL_GITIGNORE_START = "# speckit-turbo:start"
VISUAL_GITIGNORE_END = "# speckit-turbo:end"
VISUAL_GITIGNORE_ENTRY = ".specify/visual-references/"
STRUCTURED_SIGNALS = (
    Path("memory/constitution.md"),
    Path("templates"),
    Path("scripts"),
)
AGENT_DIRS = (".agents/skills", ".github/prompts", ".github/agents", ".claude/commands")


class InstallError(RuntimeError):
    pass


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise InstallError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallError(f"Expected JSON object in {path}")
    return value


def has_spec_kit(root: Path) -> tuple[bool, list[str]]:
    specify = root / ".specify"
    found = [str(path) for path in STRUCTURED_SIGNALS if (specify / path).exists()]
    return bool(found), found


def detect_integration(root: Path) -> str:
    if (root / ".agents" / "skills").exists() and list((root / ".agents" / "skills").glob("speckit-*/SKILL.md")):
        return "codex"
    if (root / ".github" / "prompts").exists() or (root / ".github" / "agents").exists():
        return "copilot"
    if (root / ".claude" / "commands").exists():
        return "claude"
    return "unknown"


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def snapshot_paths(root: Path) -> dict[Path, Path | None]:
    paths = [root / ".specify", root / ".agents", root / ".github", root / ".claude", root / "AGENTS.md", root / ".gitignore"]
    snapshot: dict[Path, Path | None] = {}
    temp = Path(__file__).resolve().parent / ".bootstrap-snapshot"
    remove_path(temp)
    temp.mkdir()
    for path in paths:
        if path.exists():
            target = temp / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(path, target) if path.is_dir() else shutil.copy2(path, target)
            snapshot[path] = target
        else:
            snapshot[path] = None
    return snapshot


def restore_snapshot(snapshot: dict[Path, Path | None]) -> None:
    for destination, source in snapshot.items():
        remove_path(destination)
        if source is not None and source.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination) if source.is_dir() else shutil.copy2(source, destination)
    temp = Path(__file__).resolve().parent / ".bootstrap-snapshot"
    remove_path(temp)


def run_bootstrap(root: Path, version: str, integration: str) -> None:
    command = os.environ.get("SPECKIT_TURBO_BOOTSTRAP_COMMAND")
    if command:
        rendered = command.replace("{target}", shlex.quote(str(root))).replace("{version}", shlex.quote(version))
    else:
        rendered = (
            "uv tool run --from "
            f"git+https://github.com/github/spec-kit.git@{shlex.quote(version)} "
            f"specify init --here --integration {shlex.quote(integration)} --ignore-agent-tools"
        )
    print(f"Bootstrapping GitHub Spec Kit ({version})...")
    result = subprocess.run(rendered, cwd=root, shell=True)
    if result.returncode != 0:
        raise InstallError(f"Spec Kit bootstrap failed with exit code {result.returncode}")


def backup_existing_turbo(turbo: Path, old_version: str) -> Path | None:
    if not turbo.exists():
        return None
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")
    backup = turbo / "backups" / f"{timestamp}-{old_version or 'unknown'}"
    backup.mkdir(parents=True, exist_ok=True)
    managed = ("AGENTS.turbo.md", "doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh", "manifest.json", "project.yml", "state.json", "runtime", "templates")
    for name in managed:
        source = turbo / name
        if source.exists():
            destination = backup / name
            shutil.copytree(source, destination) if source.is_dir() else shutil.copy2(source, destination)
    return backup


def ensure_visual_gitignore(target: Path) -> None:
    """Install only the managed visual-reference block, preserving all user rules."""
    path = target / ".gitignore"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    start = content.find(VISUAL_GITIGNORE_START)
    end = content.find(VISUAL_GITIGNORE_END)
    if (start >= 0) != (end >= 0) or (start >= 0 and end < start):
        raise InstallError(".gitignore contains a malformed Spec Kit Turbo visual-reference block")
    block = f"{VISUAL_GITIGNORE_START}\n{VISUAL_GITIGNORE_ENTRY}\n{VISUAL_GITIGNORE_END}"
    if start >= 0:
        end += len(VISUAL_GITIGNORE_END)
        updated = content[:start] + block + content[end:]
    else:
        separator = "\n" if content and not content.endswith("\n") else ""
        updated = content + separator + block + "\n"
    if updated != content:
        path.write_text(updated, encoding="utf-8")


def copy_managed(source_root: Path, target: Path, mode: str, upstream_version: str | None, integration: str, backup: Path | None) -> None:
    skills_target = target / ".agents" / "skills"
    turbo = target / ".specify" / "turbo"
    runtime = turbo / "runtime"
    ensure_visual_gitignore(target)
    skills_target.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)

    for skill in (source_root / "skills").glob("turbo-*"):
        destination = skills_target / skill.name
        remove_path(destination)
        shutil.copytree(skill, destination)
    for directory in ("schemas", "workflows"):
        destination = runtime / directory
        remove_path(destination)
        shutil.copytree(source_root / directory, destination)
    templates_target = turbo / "templates"
    templates_target.mkdir(parents=True, exist_ok=True)
    for template_name in ("constitution-interview.md", "constitution.draft.md", "visual-spec.md"):
        shutil.copy2(source_root / "templates" / template_name, templates_target / template_name)
    turbo.mkdir(parents=True, exist_ok=True)
    for name in ("AGENTS.turbo.md", "doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh"):
        shutil.copy2(source_root / ("AGENTS.turbo.md" if name == "AGENTS.turbo.md" else f"scripts/{name}"), turbo / name)

    project = turbo / "project.yml"
    if not project.exists():
        shutil.copy2(source_root / "templates/project.yml", project)
        if upstream_version:
            project.write_text(
                project.read_text(encoding="utf-8").replace("replace-with-spec-kit-version", upstream_version),
                encoding="utf-8",
            )
    state = turbo / "state.json"
    if not state.exists():
        shutil.copy2(source_root / "templates/state.json", state)

    manifest = read_json(source_root / "manifest.json")
    manifest["installation"] = {
        "mode": mode,
        "integration": integration,
        "specKitVersion": upstream_version,
        "bootstrap": mode == "clean",
        "backup": str(backup.relative_to(target)) if backup else None,
    }
    (turbo / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    agents_file = target / "AGENTS.md"
    content = agents_file.read_text(encoding="utf-8") if agents_file.exists() else ""
    if START_MARKER not in content:
        separator = "\n" if content and not content.endswith("\n") else ""
        content += separator + f"{START_MARKER}\n## Spec Kit Turbo\n\nFollow the shared rules in `.specify/turbo/AGENTS.turbo.md` and use the installed specialist skills under `.agents/skills/turbo-*`.\nPersist resumable workflow state in `.specify/turbo/state.json` and load project gates from `.specify/turbo/project.yml`.\n{END_MARKER}\n"
        agents_file.write_text(content, encoding="utf-8")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--mode", choices=("auto", "clean", "existing"), default="auto")
    parser.add_argument("--spec-kit-version")
    parser.add_argument("--upgrade", action="store_true")
    parser.add_argument("--version", action="store_true")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    source_root = Path(__file__).resolve().parents[1]
    if args.version:
        print(read_json(source_root / "manifest.json").get("turboVersion", "unknown"))
        return 0
    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Target directory does not exist: {target}", file=sys.stderr)
        return 2
    structured, signals = has_spec_kit(target)
    if (target / ".specify").exists() and not structured:
        print("Warning: .specify exists but no structured Spec Kit signals were detected; treating the project as clean unless --mode existing is used.", file=sys.stderr)
    mode = "existing" if args.mode == "auto" and structured else "clean" if args.mode == "auto" else args.mode
    if mode == "clean" and structured:
        print("Refusing clean mode: structured Spec Kit installation detected (" + ", ".join(signals) + ")", file=sys.stderr)
        return 2
    if mode == "existing" and not structured:
        print("Refusing existing mode: no structured Spec Kit installation detected", file=sys.stderr)
        return 2
    integration = detect_integration(target) if structured else "codex"
    if mode == "existing" and integration != "codex":
        print(f"Warning: detected Spec Kit integration '{integration}'; Turbo skills are Codex-first and are not adapted for this integration.", file=sys.stderr)

    turbo = target / ".specify" / "turbo"
    existing_manifest = read_json(turbo / "manifest.json") if (turbo / "manifest.json").exists() else {}
    if turbo.exists() and not existing_manifest and any(turbo.iterdir()):
        print("Refusing installation: .specify/turbo exists without a Turbo manifest", file=sys.stderr)
        return 2
    upstream_version = args.spec_kit_version
    if mode == "clean":
        if not upstream_version:
            print("Clean mode requires --spec-kit-version <ref>", file=sys.stderr)
            return 2
        snapshot = snapshot_paths(target)
        try:
            ensure_visual_gitignore(target)
            run_bootstrap(target, upstream_version, "codex")
        except InstallError as exc:
            restore_snapshot(snapshot)
            print(str(exc), file=sys.stderr)
            return 1
        remove_path(Path(__file__).resolve().parent / ".bootstrap-snapshot")
        integration = detect_integration(target)
    elif not upstream_version:
        upstream_version = existing_manifest.get("installation", {}).get("specKitVersion")

    if mode == "existing":
        try:
            ensure_visual_gitignore(target)
        except InstallError as exc:
            print(str(exc), file=sys.stderr)
            return 2

    backup = backup_existing_turbo(turbo, existing_manifest.get("turboVersion", "")) if existing_manifest else None
    try:
        copy_managed(source_root, target, mode, upstream_version, integration, backup)
    except (InstallError, OSError) as exc:
        print(f"Turbo installation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Spec Kit Turbo {read_json(source_root / 'manifest.json').get('turboVersion')} installed in {target} ({mode}).")
    if mode == "clean":
        print(f"Spec Kit initialized from {upstream_version}.")
    if backup:
        print(f"Backup created at {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
