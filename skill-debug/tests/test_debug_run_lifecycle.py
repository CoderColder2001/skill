from pathlib import Path

import pytest

from skill_debug_tools.debug_run.lifecycle import (
    append_debug_event,
    finalize_debug_run,
    load_debug_run,
    start_debug_run,
)


def test_start_debug_run_writes_under_target_local_log_root(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()

    run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260622-120000-auth-login",
        linked_skill_run_id="ca-20260622-120000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_command",
        review_mode="async",
    )

    assert run.debug_log == skill_root / "skill-debug-logs" / "runs" / "dbg-code-analyse-20260622-120000-auth-login" / "debug-log.md"
    assert run.debug_log.exists()
    assert run.review_request.exists()
    assert not (skill_root / "code-analyse-docs" / "debug-log.md").exists()


def test_append_debug_event_tracks_artifact_references_without_copying(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    business_output = skill_root / "code-analyse-docs" / "runs" / "ca-20260622-120000-auth-login.md"
    business_output.parent.mkdir(parents=True, exist_ok=True)
    business_output.write_text("# Run\n", encoding="utf-8")

    run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260622-120000-auth-login",
        linked_skill_run_id="ca-20260622-120000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_command",
        review_mode="async",
    )
    append_debug_event(
        run=run,
        phase="document_update",
        action="Updated scoped overview",
        evidence=["overview existed already"],
        artifact_refs=[str(business_output)],
    )
    finalize_debug_run(run=run, review_mode="async")

    assert str(business_output) in run.debug_log.read_text(encoding="utf-8")
    assert not (run.run_root / "artifacts" / "ca-20260622-120000-auth-login.md").exists()
    assert "review-request.json" not in run.artifact_index.read_text(encoding="utf-8")


def test_start_debug_run_rejects_path_escape_segments(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()

    with pytest.raises(ValueError):
        start_debug_run(
            skill_root=skill_root,
            skill_name="code-analyse",
            debug_run_id="../outside",
            linked_skill_run_id="ca-20260622-120000-auth-login",
            scope_slug="auth-login",
            trigger_source="manual_command",
            review_mode="async",
        )


def test_load_debug_run_rejects_run_root_outside_target_log_root(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    outside_root = tmp_path / "outside-run"
    outside_root.mkdir()

    with pytest.raises(ValueError):
        load_debug_run(skill_root=skill_root, run_root=outside_root)
