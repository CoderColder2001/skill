from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "debug-review"


class DebugReviewSkillContractTest(unittest.TestCase):
    def test_skill_contract_and_required_files_exist(self) -> None:
        required = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "README.md",
            SKILL_ROOT / "USAGE.md",
            SKILL_ROOT / "templates" / "review-report.md",
            SKILL_ROOT / "templates" / "current-review.md",
            SKILL_ROOT / "references" / "analysis-checklist.md",
            SKILL_ROOT / "references" / "evidence-rules.md",
            SKILL_ROOT / "references" / "handoff-to-code-plan.md",
            SKILL_ROOT / "evals" / "evals.json",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing required file: {path}")

    def test_skill_contract_mentions_debug_review_workflow(self) -> None:
        document = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("/debug-review", document)
        self.assertIn("debug-review-docs/", document)
        self.assertIn("current-review.md", document)
        self.assertIn("高置信原因", document)
        self.assertIn("待确认假设", document)
        self.assertIn("code-plan", document)

    def test_evals_cover_analysis_revision_and_handoff(self) -> None:
        payload = json.loads((SKILL_ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        prompts = [item["prompt"] for item in payload["evals"]]
        self.assertEqual(payload["skill_name"], "debug-review")
        self.assertGreaterEqual(len(prompts), 3)
        self.assertTrue(any("/debug-review" in prompt for prompt in prompts))
        self.assertTrue(any("修订" in prompt or "补充" in prompt for prompt in prompts))
        self.assertTrue(any("code-plan" in prompt or "修改方案" in prompt for prompt in prompts))


if __name__ == "__main__":
    unittest.main()
