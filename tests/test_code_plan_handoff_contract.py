from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CodePlanHandoffContractTest(unittest.TestCase):
    def test_code_plan_skill_accepts_debug_review_handoff(self) -> None:
        document = (ROOT / "code-plan" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("debug-review", document)
        self.assertIn("修改方案设计", document)
        self.assertIn("current-review.md", document)

    def test_code_plan_docs_explain_the_handoff_entry(self) -> None:
        readme = (ROOT / "code-plan" / "README.md").read_text(encoding="utf-8")
        usage = (ROOT / "code-plan" / "USAGE.md").read_text(encoding="utf-8")
        self.assertIn("debug-review", readme)
        self.assertIn("debug-review", usage)
        self.assertIn("修改方案设计", readme)


if __name__ == "__main__":
    unittest.main()
