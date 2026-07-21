from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ConstitutionContractTests(unittest.TestCase):
    def test_facilitator_skill_has_safety_and_resume_contract(self) -> None:
        skill = (ROOT / "skills/turbo-constitution-facilitator/SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "one question at a time",
            "speckit-constitution",
            "explicit approval",
            "constitutionInterview",
            "do not repeat completed diagnosis",
        ):
            self.assertIn(phrase, skill)

    def test_workflow_contains_approval_before_finalize(self) -> None:
        import yaml

        workflow = yaml.safe_load((ROOT / "workflows/constitution.yml").read_text(encoding="utf-8"))
        phase_ids = [phase["id"] for phase in workflow["phases"]]
        self.assertLess(phase_ids.index("approval"), phase_ids.index("finalize"))
        approval = workflow["phases"][phase_ids.index("approval")]
        self.assertEqual(approval["human_checkpoint"], "always")
        self.assertIn("human_approval_recorded", approval["gate"]["require"])

    def test_state_template_persists_interview_cursor(self) -> None:
        state = json.loads((ROOT / "templates/state.json").read_text(encoding="utf-8"))
        interview = state["constitutionInterview"]
        self.assertEqual(interview["draftPath"], ".specify/memory/constitution.draft.md")
        self.assertEqual(interview["interviewPath"], ".specify/memory/constitution-interview.md")
        self.assertIn("currentQuestion", interview)


if __name__ == "__main__":
    unittest.main()
