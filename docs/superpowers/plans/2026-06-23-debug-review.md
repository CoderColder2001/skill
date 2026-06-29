# Debug Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `/debug-review` skill that writes revisable bug-analysis documents, supports user-driven revisions, and hands off to `code-plan` only after explicit user confirmation.

**Architecture:** Keep `debug-review` as a standalone Markdown-first skill under `/Users/bytedance/workspace/skill/debug-review`, mirroring the document layout conventions already used by `code-review` and `code-plan`. Add lightweight workspace-level contract tests under `/Users/bytedance/workspace/skill/tests` so the handoff rule and core file set are checked without inventing a new runtime stack.

**Tech Stack:** Markdown skill contracts, JSON eval prompts, Python 3.11 `unittest` contract checks, `zip` packaging for `.skill` artifacts

---

## Planned File Structure

### Create

- `docs/superpowers/plans/2026-06-23-debug-review.md`
- `tests/__init__.py`
- `tests/test_debug_review_skill_contract.py`
- `tests/test_code_plan_handoff_contract.py`
- `debug-review/SKILL.md`
- `debug-review/README.md`
- `debug-review/USAGE.md`
- `debug-review/templates/review-report.md`
- `debug-review/templates/current-review.md`
- `debug-review/references/analysis-checklist.md`
- `debug-review/references/evidence-rules.md`
- `debug-review/references/handoff-to-code-plan.md`
- `debug-review/evals/evals.json`

### Modify

- `code-plan/SKILL.md`
- `code-plan/README.md`
- `code-plan/USAGE.md`
- `dist/code-plan.skill`
- `dist/debug-review.skill`

## Task 1: Add Failing Contract Tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_debug_review_skill_contract.py`
- Create: `tests/test_code_plan_handoff_contract.py`
- Test: `tests/test_debug_review_skill_contract.py`
- Test: `tests/test_code_plan_handoff_contract.py`

- [ ] **Step 1: Write the failing debug-review contract test**

```python
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
```

- [ ] **Step 2: Write the failing code-plan handoff contract test**

```python
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
```

- [ ] **Step 3: Run the contract tests to verify they fail**

Run: `python3 -m unittest tests.test_debug_review_skill_contract tests.test_code_plan_handoff_contract -v`

Expected: FAIL because `debug-review/` does not exist yet and `code-plan` does not yet mention the handoff contract.

## Task 2: Implement The `debug-review` Skill Files

**Files:**
- Create: `debug-review/SKILL.md`
- Create: `debug-review/README.md`
- Create: `debug-review/USAGE.md`
- Create: `debug-review/templates/review-report.md`
- Create: `debug-review/templates/current-review.md`
- Create: `debug-review/references/analysis-checklist.md`
- Create: `debug-review/references/evidence-rules.md`
- Create: `debug-review/references/handoff-to-code-plan.md`
- Create: `debug-review/evals/evals.json`
- Test: `tests/test_debug_review_skill_contract.py`

- [ ] **Step 1: Write the standalone skill contract and references**

Implement `debug-review/SKILL.md` so it includes:

- frontmatter `name: "debug-review"`
- explicit invocation rule for `/debug-review`
- default target = current working repository
- output path rules for `debug-review-docs/current-review.md` and `debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md`
- required report structure
- revision flow for conversation feedback and direct document edits
- handoff rule that only enters `code-plan` after explicit user confirmation
- references to:
  - `references/analysis-checklist.md`
  - `references/evidence-rules.md`
  - `references/handoff-to-code-plan.md`
  - `templates/review-report.md`
  - `templates/current-review.md`

- [ ] **Step 2: Add user-facing docs and templates**

Implement:

- `README.md` with positioning, install/copy instructions, and the `/debug-review -> code-plan` progression
- `USAGE.md` with 3 concrete examples:
  - first-pass bug analysis
  - revising analysis after new user evidence
  - user-approved handoff into fix-design planning
- `templates/review-report.md` matching the required report sections
- `templates/current-review.md` as the stable latest-analysis entry

- [ ] **Step 3: Add initial eval prompts**

Implement `debug-review/evals/evals.json` with at least 3 prompts covering:

- initial analysis
- revision after user correction
- explicit handoff into `code-plan`

- [ ] **Step 4: Re-run the debug-review contract test**

Run: `python3 -m unittest tests.test_debug_review_skill_contract -v`

Expected: PASS

## Task 3: Update `code-plan` For The Explicit Handoff

**Files:**
- Modify: `code-plan/SKILL.md`
- Modify: `code-plan/README.md`
- Modify: `code-plan/USAGE.md`
- Test: `tests/test_code_plan_handoff_contract.py`

- [ ] **Step 1: Update the `code-plan` skill contract**

Adjust `code-plan/SKILL.md` so it now accepts two entry paths:

- explicit `/code-plan`
- explicit user-approved handoff from an active `debug-review` analysis

The wording must still block ordinary implicit bug conversations from slipping into `code-plan`.

- [ ] **Step 2: Update user-facing docs**

Adjust `README.md` and `USAGE.md` to explain that:

- the default entry is still `/code-plan`
- users coming from `/debug-review` can say they want to enter fix-design planning
- the latest `debug-review-docs/current-review.md` becomes the handoff context

- [ ] **Step 3: Re-run the handoff contract test**

Run: `python3 -m unittest tests.test_code_plan_handoff_contract -v`

Expected: PASS

## Task 4: Package And Verify Artifacts

**Files:**
- Modify: `dist/code-plan.skill`
- Create: `dist/debug-review.skill`

- [ ] **Step 1: Refresh the packaged artifacts**

Run: `zip -qrFS /Users/bytedance/workspace/skill/dist/code-plan.skill code-plan`

Run: `zip -qr /Users/bytedance/workspace/skill/dist/debug-review.skill debug-review`

- [ ] **Step 2: Verify the contract tests together**

Run: `python3 -m unittest tests.test_debug_review_skill_contract tests.test_code_plan_handoff_contract -v`

Expected: both test modules PASS

- [ ] **Step 3: Verify packaged contents**

Run: `unzip -l /Users/bytedance/workspace/skill/dist/debug-review.skill`

Expected: archive lists the `debug-review/` directory and all required files.

Run: `unzip -l /Users/bytedance/workspace/skill/dist/code-plan.skill`

Expected: archive reflects the updated `code-plan` docs and contract files.
