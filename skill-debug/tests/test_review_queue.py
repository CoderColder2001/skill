import json
from pathlib import Path

from skill_debug_tools.attach import attach_skill
from skill_debug_tools.common.files import atomic_write_text, write_json
from skill_debug_tools.debug_run.lifecycle import append_debug_event, finalize_debug_run, start_debug_run
from skill_debug_tools.review.queue import enqueue_review_job, move_job, process_next_review_job


def _skill_document(name: str, *, body: str = "# Skill\n") -> str:
    return f"---\nname: {name}\ndescription: test skill\n---\n\n{body}"


def test_enqueue_review_job_creates_pending_file(tmp_path: Path) -> None:
    job = enqueue_review_job(
        runtime_root=tmp_path / "skill-debug" / "runtime",
        request_path=tmp_path / "request.json",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
    )

    assert job.exists()
    assert "pending" in str(job)


def test_move_job_moves_file_to_destination_bucket(tmp_path: Path) -> None:
    job = enqueue_review_job(
        runtime_root=tmp_path / "skill-debug" / "runtime",
        request_path=tmp_path / "request.json",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
    )

    moved = move_job(job_path=job, destination="done")

    assert moved.exists()
    assert "done" in str(moved)
    assert not job.exists()


def test_process_next_review_job_moves_job_to_done_and_writes_review(tmp_path: Path) -> None:
    request_path, runtime_root, run_root = _prepare_queued_review(
        tmp_path,
        backend_override="gpt-mock",
    )
    job = enqueue_review_job(
        runtime_root=runtime_root,
        request_path=request_path,
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
    )

    moved = process_next_review_job(runtime_root=runtime_root)

    assert moved == runtime_root / "review-queue" / "done" / job.name
    assert moved.exists()
    assert not job.exists()
    assert (run_root / "review.md").exists()
    assert (run_root / "review-status.json").exists()


def test_process_next_review_job_moves_job_to_failed_when_profile_missing(tmp_path: Path) -> None:
    request_path, runtime_root, run_root = _prepare_queued_review(
        tmp_path,
        backend_override="missing-profile",
    )
    job = enqueue_review_job(
        runtime_root=runtime_root,
        request_path=request_path,
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
    )

    moved = process_next_review_job(runtime_root=runtime_root)

    assert moved == runtime_root / "review-queue" / "failed" / job.name
    assert moved.exists()
    review_status = json.loads((run_root / "review-status.json").read_text(encoding="utf-8"))
    assert review_status["status"] == "failed"
    assert "missing-profile" in review_status["error"]


def _prepare_queued_review(
    workspace_root: Path,
    *,
    backend_override: str,
) -> tuple[Path, Path, Path]:
    skill_root = workspace_root / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))
    attach_skill(workspace_root, "code-analyse")

    target_config = skill_root / "skill-debug" / "config.yaml"
    target_config.write_text(
        target_config.read_text(encoding="utf-8") + "default_backend_profile: gpt-mock\n",
        encoding="utf-8",
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
        action="Updated scoped overview",
        evidence=["overview existed already"],
        artifact_refs=[str(skill_root / "code-analyse-docs" / "runs" / "ca-20260618-153000-auth-login.md")],
    )
    finalize_debug_run(run=debug_run, review_mode="async")

    request_payload = json.loads(debug_run.review_request.read_text(encoding="utf-8"))
    request_payload["backend_profile"] = backend_override
    write_json(debug_run.review_request, request_payload)

    runtime_root = workspace_root / "framework-runtime"
    config_path = runtime_root / "config" / "backends.local.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        "\n".join(
            [
                "default_profile: gpt-mock",
                "profiles:",
                "  gpt-mock:",
                "    runner: openai_api",
                "    provider: gpt",
                "    transport: mock",
                "    base_url: https://mock-gpt.invalid/v1",
                "    model: gpt-5",
                "    api_key_env: SKILL_DEBUG_GPT_KEY",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return debug_run.review_request, runtime_root, debug_run.run_root
