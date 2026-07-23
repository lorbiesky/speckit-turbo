import json
import subprocess
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
COMMANDS = {
    "start", "feature", "bugfix", "refactor", "maintenance", "hotfix",
    "discovery", "constitution", "status", "resume", "tdd", "visual",
}
WORKFLOWS = {
    "turbo-feature", "turbo-bugfix", "turbo-refactor", "turbo-maintenance",
    "turbo-hotfix", "turbo-discovery", "turbo-constitution",
}


class NativeBundleContractTests(unittest.TestCase):
    def test_structural_validator_passes(self):
        result = subprocess.run(["python3", "scripts/validate.py"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_extension_registers_exact_command_contract(self):
        extension = yaml.safe_load((ROOT / "extension.yml").read_text())
        entries = extension["provides"]["commands"]
        names = {entry["name"].removeprefix("speckit.turbo.") for entry in entries}
        self.assertEqual(names, COMMANDS)
        self.assertEqual(extension["extension"]["version"], VERSION)
        for entry in entries:
            self.assertTrue((ROOT / entry["file"]).is_file())

    def test_every_implementation_workflow_has_tdd_and_gate(self):
        for workflow_id in WORKFLOWS - {"turbo-discovery", "turbo-constitution"}:
            workflow = yaml.safe_load((ROOT / "workflows" / workflow_id / "workflow.yml").read_text())
            step_ids = {step["id"] for step in workflow["steps"]}
            self.assertIn("tdd", step_ids, workflow_id)
            self.assertTrue(any(step.get("type") == "gate" for step in workflow["steps"]), workflow_id)

    def test_catalogs_reference_versioned_assets(self):
        for path in (ROOT / "catalogs").glob("*.json"):
            catalog = json.loads(path.read_text())
            serialized = json.dumps(catalog)
            self.assertIn(VERSION, serialized)
            self.assertTrue(
                "releases/download/v" + VERSION in serialized
                or "/v" + VERSION + "/workflows/" in serialized
            )

    def test_public_docs_do_not_restore_npm_runtime(self):
        prohibited = ("npx speckit-turbo", "$turbo-", "node .specify/turbo")
        public_files = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        text = "\n".join(path.read_text().lower() for path in public_files)
        for token in prohibited:
            self.assertNotIn(token, text, token)

    def test_constitution_questions_are_scope_restricted(self):
        command = (ROOT / "commands/speckit.turbo.constitution.md").read_text().lower()
        for term in (
            "not_constitutional",
            "three contextual policy alternatives",
            "free-text",
            "normalized principle",
            "observable practice",
            "validation criterion",
        ):
            self.assertIn(term, command)

        config = yaml.safe_load((ROOT / "turbo-config.yml").read_text())["constitution"]
        self.assertEqual(config["question_format"], "single_choice_with_free_text")
        self.assertEqual(config["option_count"], 3)
        self.assertTrue(config["require_constitutional_scope"])

    def test_constitution_artifacts_exclude_operational_candidates(self):
        interview = (ROOT / "templates/constitution-interview.md").read_text().lower()
        draft = (ROOT / "templates/constitution.draft.md").read_text().lower()
        self.assertIn("candidates discarded as operational", interview)
        self.assertIn("routing, if rejected as operational", interview)
        self.assertIn("constitutional scope confirmed", draft)
        self.assertIn("observable practice", draft)
        self.assertIn("validation criterion", draft)


if __name__ == "__main__":
    unittest.main()
