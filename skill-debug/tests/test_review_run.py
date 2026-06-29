from __future__ import annotations

import json
from pathlib import Path

from skill_debug_tools.attach import attach_skill
from skill_debug_tools.common.files import atomic_write_text, write_json
from skill_debug_tools.debug_run.lifecycle import append_debug_event, finalize_debug_run, start_debug_run
from skill_debug_tools.review.run import load_backend_profile, run_review_for_request, select_backend_name


def _skill_document(name: str, *, body: str = "# Skill\n") -> str:
    return f"---\nname: {name}\ndescription: test skill\n---\n\n{body}"


def test_select_backend_name_prefers_run_override() -> None:
    selected = select_backend_name(
        run_override="test-openai",
        target_default="code-analyse-default",
        global_default="noop",
    )
    assert selected == "test-openai"


def test_select_backend_name_falls_back_to_noop() -> None:
    selected = select_backend_name(
        run_override=None,
        target_default=None,
        global_default=None,
    )
    assert selected == "noop"


def test_load_backend_profile_reads_example_yaml(tmp_path: Path) -> None:
    config = tmp_path / "backends.local.yaml"
    config.write_text(
        "profiles:\n  test-openai:\n    runner: openai_api\n    base_url: https://example.invalid/v1\n    model: gpt-5\n    api_key_env: TEST_KEY\n",
        encoding="utf-8",
    )

    profile = load_backend_profile(config, "test-openai")

    assert profile["runner"] == "openai_api"


def test_run_review_for_request_uses_run_override_backend_and_writes_artifacts(tmp_path: Path) -> None:
    request_path, runtime_config, run_root = _prepare_review_context(
        tmp_path,
        backend_override="deepseek-mock",
        target_default="gpt-mock",
    )

    result = run_review_for_request(
        request_path=request_path,
        config_path=runtime_config,
    )

    review_text = result.review_path.read_text(encoding="utf-8")
    review_status = json.loads(result.review_status_path.read_text(encoding="utf-8"))
    review_input = result.review_input_path.read_text(encoding="utf-8")

    assert "deepseek" in review_text.lower()
    assert "deepseek-chat" in review_text
    assert review_status["status"] == "completed"
    assert review_status["backend_profile"] == "deepseek-mock"
    assert review_status["runner"] == "openai_api"
    assert review_status["provider"] == "deepseek"
    assert result.review_input_path == run_root / "artifacts" / "review-input.md"
    assert "Focus on whether the trace is complete" in review_input
    assert "Verify that debug artifacts stay separate" in review_input


def test_run_review_for_request_falls_back_to_target_default_backend(tmp_path: Path) -> None:
    request_path, runtime_config, run_root = _prepare_review_context(
        tmp_path,
        backend_override=None,
        target_default="gpt-mock",
    )

    result = run_review_for_request(
        request_path=request_path,
        config_path=runtime_config,
    )

    review_text = result.review_path.read_text(encoding="utf-8")
    review_status = json.loads(result.review_status_path.read_text(encoding="utf-8"))

    assert "gpt" in review_text.lower()
    assert "gpt-5" in review_text
    assert review_status["backend_profile"] == "gpt-mock"
    assert review_status["provider"] == "gpt"
    assert (run_root / "review.md").exists()


def _prepare_review_context(
    workspace_root: Path,
    *,
    backend_override: str | None,
    target_default: str,
) -> tuple[Path, Path, Path]:
    skill_root = workspace_root / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))
    attach_skill(workspace_root, "code-analyse")

    target_config = skill_root / "skill-debug" / "config.yaml"
    target_config.write_text(
        target_config.read_text(encoding="utf-8") + f"default_backend_profile: {target_default}\n",
        encoding="utf-8",
    )
    atomic_write_text(
        skill_root / "skill-debug" / "evaluation-guide.md",
        "# code-analyse Evaluation Guide\n\n- Focus on whether the trace is complete.\n- Verify that debug artifacts stay separate from business artifacts.\n",
    )
    atomic_write_text(
        skill_root / "skill-debug" / "review-prompt.md",
        "# code-analyse Review Prompt Overlay\n\nPrioritize evidence quality, output references, and artifact separation.\n",
    )

    business_output = skill_root / "code-analyse-docs" / "runs" / "ca-20260618-153000-auth-login.md"
    business_output.parent.mkdir(parents=True, exist_ok=True)
    business_output.write_text("# Run\n", encoding="utf-8")

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
        artifact_refs=[str(business_output)],
    )
    finalize_debug_run(run=debug_run, review_mode="async")

    request_payload = json.loads(debug_run.review_request.read_text(encoding="utf-8"))
    if backend_override is not None:
        request_payload["backend_profile"] = backend_override
    write_json(debug_run.review_request, request_payload)

    runtime_config = workspace_root / "framework-runtime" / "config" / "backends.local.yaml"
    runtime_config.parent.mkdir(parents=True, exist_ok=True)
    runtime_config.write_text(
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
                "  deepseek-mock:",
                "    runner: openai_api",
                "    provider: deepseek",
                "    transport: mock",
                "    base_url: https://mock-deepseek.invalid/v1",
                "    model: deepseek-chat",
                "    api_key_env: SKILL_DEBUG_DEEPSEEK_KEY",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return debug_run.review_request, runtime_config, debug_run.run_root
