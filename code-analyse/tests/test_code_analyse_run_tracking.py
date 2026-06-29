from pathlib import Path

from skill_tools.code_analyse.run_tracking import (
    append_run_event,
    finalize_run,
    start_run,
    sync_future_work,
)


def test_start_run_creates_global_and_scope_documents(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "code-analyse-docs",
        run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        objective="Trace the auth login workflow",
        status="needs_clarification",
        module_scoped=True,
    )
    assert run.global_current.exists()
    assert run.global_run.exists()
    assert run.scope_current and run.scope_current.exists()
    assert run.scope_run and run.scope_run.exists()


def test_append_event_updates_current_run_and_history(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "code-analyse-docs",
        run_id="ca-20260618-153000-repo",
        scope_slug="repo",
        objective="Map repository-wide architecture",
        status="in_progress",
        module_scoped=False,
    )
    append_run_event(
        output_root=tmp_path / "code-analyse-docs",
        run_id=run.run_id,
        phase="scope_resolution",
        action="Marked repository-wide scope",
        evidence=["user omitted module"],
        outputs=[],
        next_step="Inspect entrypoints",
    )
    history = run.global_run.read_text()
    current = run.global_current.read_text()
    assert "scope_resolution" in history
    assert "Inspect entrypoints" in current


def test_sync_future_work_keeps_status_per_topic(tmp_path: Path) -> None:
    sync_future_work(
        output_root=tmp_path / "code-analyse-docs",
        scope_slug="auth-login",
        topics=[
            {"topic": "request-flow", "priority": "high", "status": "open"},
            {"topic": "session-state", "priority": "medium", "status": "deferred"},
        ],
    )
    future_work = (tmp_path / "code-analyse-docs" / "scopes" / "auth-login" / "future-work.md").read_text()
    assert "request-flow" in future_work
    assert "session-state" in future_work
    assert "deferred" in future_work
