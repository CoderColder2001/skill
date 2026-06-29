from pathlib import Path

from skill_debug_tools.attach import attach_skill
from skill_debug_tools.debug_run.lifecycle import append_debug_event, start_debug_run
from skill_tools.code_analyse.run_tracking import start_run


ROOT = Path(__file__).resolve().parents[1]


def test_code_analyse_target_attachment_and_debug_run_stay_separate(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    skill_path = skill_root / "SKILL.md"
    skill_path.write_text((ROOT / "SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
    attach_skill(tmp_path, "code-analyse")
    start_run(
        output_root=skill_root / "code-analyse-docs",
        run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        objective="Trace the auth login workflow",
        status="in_progress",
        module_scoped=True,
    )
    debug_run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
        linked_skill_run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_alias",
        review_mode="async",
    )
    append_debug_event(
        run=debug_run,
        phase="document_update",
        action="Referenced the business run document",
        evidence=["business output exists"],
        artifact_refs=[str(skill_root / "code-analyse-docs" / "runs" / "ca-20260618-153000-auth-login.md")],
    )
    assert (skill_root / "skill-debug" / "config.yaml").exists()
    assert (skill_root / "skill-debug-logs" / "runs").exists()
    assert not (skill_root / "code-analyse-docs" / "debug-log.md").exists()
