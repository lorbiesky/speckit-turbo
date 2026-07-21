from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeInstallationTests(unittest.TestCase):
    def run_install(
        self, target: Path, *options: str, bootstrap_command: str | None = None, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        if bootstrap_command is not None:
            environment["SPECKIT_TURBO_BOOTSTRAP_COMMAND"] = bootstrap_command
        return subprocess.run(
            ["sh", str(ROOT / "scripts/install.sh"), *options, str(target)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=check,
            env=environment,
        )

    def test_clean_bootstraps_upstream_and_installs_turbo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            target.mkdir()
            result = self.run_install(
                target,
                "--mode",
                "clean",
                "--spec-kit-version",
                "v-test",
                bootstrap_command="mkdir -p .specify/memory .specify/templates .specify/scripts; touch .specify/memory/constitution.md",
            )
            self.assertIn("(clean)", result.stdout)
            self.assertTrue((target / ".specify/memory/constitution.md").exists())
            profile = (target / ".specify/turbo/project.yml").read_text(encoding="utf-8")
            self.assertIn("version: v-test", profile)
            manifest = json.loads((target / ".specify/turbo/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["installation"]["mode"], "clean")
            self.assertEqual(manifest["installation"]["specKitVersion"], "v-test")

    def test_clean_bootstrap_failure_restores_partial_upstream_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            target.mkdir()
            (target / "AGENTS.md").write_text("project rules\n", encoding="utf-8")
            result = self.run_install(
                target,
                "--mode",
                "clean",
                "--spec-kit-version",
                "v-test",
                bootstrap_command="mkdir -p .specify/memory; touch .specify/memory/partial; exit 7",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((target / ".specify").exists())
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "project rules\n")
            self.assertFalse((target / ".specify/turbo").exists())
            self.assertFalse((target / ".gitignore").exists())

    def test_installer_manages_visual_gitignore_and_git_check_ignore(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(target)], check=True)
            (target / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
            self.run_install(target, "--mode", "existing")
            gitignore = (target / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("node_modules/", gitignore)
            self.assertIn(".specify/visual-references/", gitignore)
            reference = target / ".specify/visual-references/screenshot.png"
            reference.parent.mkdir(parents=True, exist_ok=True)
            reference.write_bytes(b"fixture")
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(reference.relative_to(target))],
                cwd=target,
            )
            self.assertEqual(result.returncode, 0)

    def test_malformed_visual_gitignore_block_fails_before_installation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            (target / ".gitignore").write_text("# speckit-turbo:start\n", encoding="utf-8")
            result = self.run_install(target, "--mode", "existing", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((target / ".specify/turbo").exists())

    def test_doctor_detects_unignored_visual_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(target)], check=True)
            self.run_install(target, "--mode", "existing")
            gitignore = target / ".gitignore"
            gitignore.write_text("", encoding="utf-8")
            reference = target / ".specify/visual-references/screenshot.png"
            reference.parent.mkdir(parents=True, exist_ok=True)
            reference.write_bytes(b"fixture")
            result = subprocess.run(
                ["python3", str(target / ".specify/turbo/doctor.py")],
                cwd=target,
                capture_output=True,
                text=True,
            )
            self.assertIn("Visual references are not ignored", result.stdout)

    def test_existing_preserves_upstream_and_detects_non_codex_integration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/templates").mkdir()
            (target / ".specify/scripts").mkdir()
            (target / ".specify/memory/constitution.md").write_text("upstream", encoding="utf-8")
            (target / ".github/prompts").mkdir(parents=True)
            upstream = target / ".github/prompts/speckit.specify.md"
            upstream.write_text("upstream command", encoding="utf-8")
            result = self.run_install(target, "--mode", "existing")
            self.assertIn("not adapted", result.stderr)
            self.assertEqual(upstream.read_text(encoding="utf-8"), "upstream command")
            self.assertEqual((target / ".specify/memory/constitution.md").read_text(encoding="utf-8"), "upstream")
            manifest = json.loads((target / ".specify/turbo/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["installation"]["integration"], "copilot")

    def test_upgrade_creates_backup_and_preserves_turbo_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            self.run_install(target, "--mode", "existing")
            profile = target / ".specify/turbo/project.yml"
            state = target / ".specify/turbo/state.json"
            profile.write_text("custom profile\n", encoding="utf-8")
            state.write_text("custom state\n", encoding="utf-8")
            self.run_install(target, "--mode", "existing", "--upgrade")
            self.assertEqual(profile.read_text(encoding="utf-8"), "custom profile\n")
            self.assertEqual(state.read_text(encoding="utf-8"), "custom state\n")
            backups = list((target / ".specify/turbo/backups").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertTrue((backups[0] / "project.yml").exists())

    def test_doctor_reports_installation_mode_and_unignored_backups(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            self.run_install(target, "--mode", "existing")
            self.run_install(target, "--mode", "existing", "--upgrade")
            result = subprocess.run(
                ["python3", str(target / ".specify/turbo/doctor.py")],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertIn("Installation mode: existing", result.stdout)
            self.assertIn("not protected by .gitignore", result.stdout)

    def test_existing_requires_structured_spec_kit_and_manual_turbo_conflict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            target.mkdir()
            result = self.run_install(target, "--mode", "existing", check=False)
            self.assertNotEqual(result.returncode, 0)
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("x", encoding="utf-8")
            (target / ".specify/turbo").mkdir()
            (target / ".specify/turbo/manual.txt").write_text("manual", encoding="utf-8")
            result = self.run_install(target, "--mode", "existing", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((target / ".specify/turbo/manual.txt").exists())

    def test_runtime_skips_visual_phase_without_inputs_and_requires_gate_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            self.run_install(target, "--mode", "existing")
            runtime = target / ".specify/turbo/workflow_runtime.py"
            started = subprocess.run(
                ["python3", str(runtime), "--path", str(target), "start", "feature", "--work-id", "dynamic-feature"],
                text=True, capture_output=True, check=True,
            )
            self.assertIn("feature / active / intake", started.stdout)
            incomplete = subprocess.run(
                ["python3", str(runtime), "--path", str(target), "complete", "intake"],
                text=True, capture_output=True,
            )
            self.assertNotEqual(incomplete.returncode, 0)
            completed = subprocess.run(
                ["python3", str(runtime), "--path", str(target), "complete", "intake",
                 "--evidence", "classified_as_feature=classified", "--evidence", "scope_recorded=scope",
                 "--evidence", "project_profile_loaded=profile"],
                text=True, capture_output=True, check=True,
            )
            self.assertIn("feature / active / product-specification", completed.stdout)
            state = json.loads((target / ".specify/turbo/state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["visualAnalysis"]["status"], "skipped")

    def test_runtime_waits_for_visual_analysis_when_a_print_is_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            self.run_install(target, "--mode", "existing")
            runtime = target / ".specify/turbo/workflow_runtime.py"
            subprocess.run(
                ["python3", str(runtime), "--path", str(target), "start", "feature", "--work-id", "visual-feature",
                 "--visual-input", "button.png"], text=True, capture_output=True, check=True,
            )
            subprocess.run(
                ["python3", str(runtime), "--path", str(target), "complete", "intake",
                 "--evidence", "classified_as_feature=classified", "--evidence", "scope_recorded=scope",
                 "--evidence", "project_profile_loaded=profile"], text=True, capture_output=True, check=True,
            )
            status = subprocess.run(
                ["python3", str(runtime), "--path", str(target), "status"], text=True, capture_output=True, check=True,
            )
            self.assertIn("feature / active / visual-analysis", status.stdout)

    def test_runtime_routes_every_declared_classification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "consumer"
            (target / ".specify/memory").mkdir(parents=True)
            (target / ".specify/memory/constitution.md").write_text("constitution", encoding="utf-8")
            self.run_install(target, "--mode", "existing")
            runtime = target / ".specify/turbo/workflow_runtime.py"
            for classification in ("feature", "bugfix", "refactor", "discovery", "maintenance", "hotfix", "constitution"):
                result = subprocess.run(
                    ["python3", str(runtime), "--path", str(target), "start", classification,
                     "--work-id", f"{classification}-work", "--force"],
                    text=True, capture_output=True, check=True,
                )
                self.assertIn(f"{classification} / active /", result.stdout)


if __name__ == "__main__":
    unittest.main()
