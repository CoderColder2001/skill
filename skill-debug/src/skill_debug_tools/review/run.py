from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skill_debug_tools.common.files import atomic_write_text, read_yaml, write_json


@dataclass(frozen=True)
class ReviewResult:
    review_path: Path
    review_status_path: Path
    review_input_path: Path
    backend_profile: str
    runner: str


def select_backend_name(
    *,
    run_override: str | None,
    target_default: str | None,
    global_default: str | None,
) -> str:
    return run_override or target_default or global_default or "noop"


def load_backend_profile(config_path: Path, profile_name: str) -> dict[str, Any]:
    config = read_yaml(config_path)
    return config.get("profiles", {}).get(profile_name, {})


def run_review_for_request(
    *,
    request_path: Path,
    config_path: Path | None = None,
) -> ReviewResult:
    request_path = request_path.resolve()
    run_root = request_path.parent
    skill_root = _infer_skill_root(run_root)
    review_path = run_root / "review.md"
    review_status_path = run_root / "review-status.json"
    review_input_path = run_root / "artifacts" / "review-input.md"
    request_payload = json.loads(request_path.read_text(encoding="utf-8"))
    skill_name = str(request_payload.get("skill_name", "")).strip() or skill_root.name
    target_root = skill_root / "skill-debug"
    target_config = read_yaml(target_root / "config.yaml")
    resolved_config_path = _resolve_config_path(skill_root=skill_root, config_path=config_path)
    backend_name = select_backend_name(
        run_override=request_payload.get("backend_profile"),
        target_default=target_config.get("default_backend_profile"),
        global_default=_load_global_default_profile_name(resolved_config_path),
    )

    try:
        profile = load_backend_profile(resolved_config_path, backend_name)
        if not profile:
            raise ValueError(f"Backend profile `{backend_name}` was not found in `{resolved_config_path}`.")

        runner_name = str(profile.get("runner", "noop"))
        review_input = _build_review_input(
            skill_root=skill_root,
            request_payload=request_payload,
            request_path=request_path,
            run_root=run_root,
            skill_name=skill_name,
            target_root=target_root,
        )
        atomic_write_text(review_input_path, review_input)
        _append_artifact_index_entries(
            run_root / "artifacts" / "artifact-index.md",
            ["- `review-input.md` - reproducible review input snapshot"],
        )

        runner = _load_runner(runner_name)
        review_body = runner(prompt=review_input, profile=profile)
        atomic_write_text(review_path, _render_review_document(review_body))

        status_payload = {
            "status": "completed",
            "skill_name": skill_name,
            "debug_run_id": request_payload.get("debug_run_id"),
            "linked_skill_run_id": request_payload.get("linked_skill_run_id"),
            "review_mode": request_payload.get("review_mode"),
            "backend_profile": backend_name,
            "runner": runner_name,
            "provider": profile.get("provider", "unknown"),
            "model": profile.get("model"),
            "request_path": str(request_path),
            "review_path": str(review_path),
        }
        write_json(review_status_path, status_payload)
        _append_artifact_index_entries(
            run_root / "artifacts" / "artifact-index.md",
            [
                "- `review.md` - review result produced by the selected review backend",
                "- `review-status.json` - review execution metadata and outcome",
            ],
        )
        return ReviewResult(
            review_path=review_path,
            review_status_path=review_status_path,
            review_input_path=review_input_path,
            backend_profile=backend_name,
            runner=runner_name,
        )
    except Exception as exc:
        write_json(
            review_status_path,
            {
                "status": "failed",
                "skill_name": skill_name,
                "debug_run_id": request_payload.get("debug_run_id"),
                "linked_skill_run_id": request_payload.get("linked_skill_run_id"),
                "review_mode": request_payload.get("review_mode"),
                "backend_profile": backend_name,
                "request_path": str(request_path),
                "error": str(exc),
            },
        )
        _append_artifact_index_entries(
            run_root / "artifacts" / "artifact-index.md",
            ["- `review-status.json` - review failure metadata"],
        )
        raise


def _resolve_config_path(*, skill_root: Path, config_path: Path | None) -> Path:
    if config_path is not None:
        return config_path
    local_config = skill_root / "skill-debug" / "runtime" / "config" / "backends.local.yaml"
    if local_config.exists():
        return local_config
    return _framework_root() / "runtime" / "config" / "backends.example.yaml"


def _load_global_default_profile_name(config_path: Path) -> str | None:
    config = read_yaml(config_path)
    return config.get("default_profile")


def _infer_skill_root(run_root: Path) -> Path:
    skill_debug_logs_root = run_root.parent.parent
    return skill_debug_logs_root.parent


def _build_review_input(
    *,
    skill_root: Path,
    request_payload: dict[str, Any],
    request_path: Path,
    run_root: Path,
    skill_name: str,
    target_root: Path,
) -> str:
    debug_log = run_root / "debug-log.md"
    artifact_index = run_root / "artifacts" / "artifact-index.md"
    evaluation_guide = (target_root / "evaluation-guide.md").read_text(encoding="utf-8").strip()
    review_overlay = (target_root / "review-prompt.md").read_text(encoding="utf-8").strip()
    business_outputs = _read_referenced_business_outputs(skill_root=skill_root, debug_log_path=debug_log)

    prompt_body = "\n".join(
        [
            "Review this skill-debug trace and produce an execution-quality assessment.",
            "",
            "## Review Request",
            "",
            f"- Skill: `{skill_name}`",
            f"- Debug Run ID: `{request_payload.get('debug_run_id', 'unknown')}`",
            f"- Linked Skill Run ID: `{request_payload.get('linked_skill_run_id', 'unknown')}`",
            f"- Review Mode: `{request_payload.get('review_mode', 'unknown')}`",
            f"- Request Path: `{request_path}`",
            "",
            "## Target Review Overlay",
            "",
            review_overlay,
            "",
            "## Evaluation Guide",
            "",
            evaluation_guide,
            "",
            "## Debug Log",
            "",
            debug_log.read_text(encoding="utf-8").strip(),
            "",
            "## Artifact Index",
            "",
            artifact_index.read_text(encoding="utf-8").strip(),
            "",
            "## Referenced Business Outputs",
            "",
            business_outputs,
            "",
            "## Review Expectations",
            "",
            "- Focus on correctness of the trace, completeness of major steps, and evidence quality.",
            "- Call out missing or weak evidence, silent failures, and ambiguous status changes.",
            "- Confirm business artifacts are referenced without being copied into the debug artifact root.",
            "- End with actionable next steps.",
        ]
    ).strip()
    template = (_framework_root() / "templates" / "review-prompt.md").read_text(encoding="utf-8")
    return template.replace("{{ skill_name }}", skill_name).replace("{{ prompt_body }}", prompt_body) + "\n"


def _read_referenced_business_outputs(*, skill_root: Path, debug_log_path: Path) -> str:
    references: list[str] = []
    for line in debug_log_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- Artifact Refs: "):
            continue
        payload = line.split(": ", 1)[1].strip()
        if payload == "none":
            continue
        for item in payload.split(","):
            reference = item.strip().strip("`")
            if reference and reference not in references:
                references.append(reference)

    if not references:
        return "- No referenced business outputs captured."

    sections: list[str] = []
    resolved_skill_root = skill_root.resolve()
    for reference in references:
        path = Path(reference)
        if not path.is_absolute():
            path = resolved_skill_root / path
        resolved = path.resolve()
        if not resolved.exists():
            sections.extend([f"### {reference}", "", "- Referenced file was missing at review time.", ""])
            continue
        if resolved != resolved_skill_root and resolved_skill_root not in resolved.parents:
            sections.extend(
                [
                    f"### {reference}",
                    "",
                    "- Referenced file is outside the target skill root and was not inlined.",
                    "",
                ]
            )
            continue
        sections.extend(
            [
                f"### {resolved}",
                "",
                "```md",
                resolved.read_text(encoding="utf-8").rstrip(),
                "```",
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _framework_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_runner(runner_name: str):
    runner_path = _framework_root() / "review_runners" / f"{runner_name}.py"
    if not runner_path.exists():
        raise ValueError(f"Review runner `{runner_name}` is not available at `{runner_path}`.")

    spec = importlib.util.spec_from_file_location(f"skill_debug_runner_{runner_name}", runner_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Failed to load runner module for `{runner_name}`.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run = getattr(module, "run", None)
    if run is None:
        raise ValueError(f"Runner `{runner_name}` does not expose a `run` function.")
    return run


def _render_review_document(review_body: str) -> str:
    normalized = review_body.strip()
    if normalized.startswith("#"):
        return normalized + "\n"
    template = (_framework_root() / "templates" / "review.md").read_text(encoding="utf-8")
    return template.replace("{{ review_summary }}", normalized) + "\n"


def _append_artifact_index_entries(artifact_index_path: Path, entries: list[str]) -> None:
    if not artifact_index_path.exists():
        atomic_write_text(artifact_index_path, "# Artifact Index\n\n")
    current = artifact_index_path.read_text(encoding="utf-8")
    additions = [entry for entry in entries if entry not in current]
    if not additions:
        return
    suffix = "" if current.endswith("\n") else "\n"
    atomic_write_text(artifact_index_path, current + suffix + "\n".join(additions) + "\n")
