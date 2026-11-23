from pathlib import Path

import pytest

pytest.importorskip("skill_debug_tools", reason="Optional skill-debug integration is not installed")

from skill_debug_tools.attach import attach_skill
from skill_debug_tools.debug_run.lifecycle import append_debug_event, start_debug_run
from skill_tools.code_study_global.run_tracking import start_run


ROOT = Path(__file__).resolve().parents[1]


def test_code_study_global_target_attachment_and_debug_run_stay_separate(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-study-global"
    skill_root.mkdir()
    skill_path = skill_root / "SKILL.md"
    skill_path.write_text((ROOT / "SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
    attach_skill(tmp_path, "code-study-global")
    start_run(
        output_root=skill_root / "docs" / "code-study-global",
        run_id="csg-20260714-153000-runtime",
        objective="Trace global runtime topology",
        status="in_progress",
        focus_topics=["runtime"],
    )
    debug_run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-study-global",
        debug_run_id="dbg-code-study-global-20260714-153000-runtime",
        linked_skill_run_id="csg-20260714-153000-runtime",
        scope_slug="global",
        trigger_source="manual_alias",
        review_mode="async",
    )
    append_debug_event(
        run=debug_run,
        phase="document_update",
        action="Referenced the business run document",
        evidence=["business output exists"],
        artifact_refs=[str(skill_root / "docs" / "code-study-global" / "runs" / "csg-20260714-153000-runtime.md")],
    )
    assert (skill_root / "skill-debug" / "config.yaml").exists()
    assert (skill_root / "skill-debug-logs" / "runs").exists()
    assert not (skill_root / "docs" / "code-study-global" / "debug-log.md").exists()
