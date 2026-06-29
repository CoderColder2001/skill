from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Literal

import yaml

from skill_debug_tools.common.files import atomic_write_text, read_yaml, write_json
from skill_debug_tools.workspace.discovery import IntegrationState, discover_skills

AttachResult = Literal["attached", "already_aligned", "repaired"]

_CONFIG_SCHEMA_VERSION = 1
_MANAGED_BLOCK_MARKER = "skill-debug"
_MANAGED_BLOCK_VERSION = 1


def attach_skill(workspace_root: Path, skill_name: str) -> AttachResult:
    workspace_root = Path(workspace_root)
    matches = [record for record in discover_skills(workspace_root) if record.name == skill_name]
    if not matches:
        known = ", ".join(sorted({record.name for record in discover_skills(workspace_root)}))
        if known:
            raise ValueError(f"Unknown skill name '{skill_name}'. Known skills: {known}")
        raise ValueError(f"Unknown skill name '{skill_name}'. No discoverable skills found.")
    if len(matches) > 1:
        paths = ", ".join(str(record.root) for record in matches)
        raise ValueError(f"Ambiguous skill name '{skill_name}'. Matches: {paths}")

    record = matches[0]
    if record.state is IntegrationState.ATTACHED:
        return "already_aligned"

    result: AttachResult = "attached" if record.state is IntegrationState.ATTACHABLE else "repaired"
    _attach_target(root=record.root, skill_name=record.name, skill_path=record.skill_path, attach_result=result)
    _verify_attached(workspace_root=workspace_root, skill_name=record.name, root=record.root)
    return result


def _attach_target(*, root: Path, skill_name: str, skill_path: Path, attach_result: AttachResult) -> None:
    integration_root = root / "skill-debug"
    config_path = integration_root / "config.yaml"
    guide_path = integration_root / "evaluation-guide.md"
    prompt_path = integration_root / "review-prompt.md"
    state_path = integration_root / "injection-state.json"

    existing_config = _read_existing_config(config_path)
    legacy_target_root = integration_root / "targets" / skill_name
    legacy_config = _read_existing_config(legacy_target_root / "config.yaml")
    if not existing_config and legacy_config:
        existing_config = legacy_config
    config = _build_config(skill_name=skill_name, existing_config=existing_config)
    atomic_write_text(config_path, _dump_yaml(config))

    if not guide_path.exists():
        legacy_guide = legacy_target_root / "evaluation-guide.md"
        if legacy_guide.exists():
            atomic_write_text(guide_path, legacy_guide.read_text(encoding="utf-8"))
        else:
            atomic_write_text(
                guide_path,
                _render_template(
                    "evaluation-guide.md",
                    skill_name=skill_name,
                    manual_debug_command=_manual_debug_command(skill_name),
                    debug_output_root="skill-debug-logs",
                    evaluation_points="\n".join(
                        [
                            f"- Confirm the run stayed aligned with `SKILL.md` when using `{_manual_debug_command(skill_name)}`.",
                            "- Confirm debug artifacts landed under `skill-debug-logs`.",
                            "- Add skill-specific quality checks here.",
                        ]
                    ),
                ),
            )
    if not prompt_path.exists():
        legacy_prompt = legacy_target_root / "review-prompt.md"
        if legacy_prompt.exists():
            atomic_write_text(prompt_path, legacy_prompt.read_text(encoding="utf-8"))
        else:
            atomic_write_text(
                prompt_path,
                _render_template(
                    "review-prompt.md",
                    skill_name=skill_name,
                    manual_debug_command=_manual_debug_command(skill_name),
                    debug_output_root="skill-debug-logs",
                    prompt_body="\n".join(
                        [
                            f"Review the latest `{skill_name}` debug run as an execution-quality audit.",
                            "",
                            "Focus on:",
                            "- correctness against `SKILL.md`",
                            "- clarity and completeness of evidence under `skill-debug-logs`",
                            "- concrete next steps grounded in the observed run",
                        ]
                    ),
                ),
            )

    if not state_path.parent.exists():
        state_path.parent.mkdir(parents=True, exist_ok=True)

    managed_body = _render_template(
        "injected-debug-block.md",
        skill_name=skill_name,
    ).strip()
    current_document = skill_path.read_text(encoding="utf-8")
    updated_document = _refresh_managed_block(
        current_document,
        marker=_MANAGED_BLOCK_MARKER,
        body=managed_body,
    )
    atomic_write_text(skill_path, updated_document)

    write_json(
        state_path,
        {
            "schema_version": _CONFIG_SCHEMA_VERSION,
            "target_skill": skill_name,
            "skill_path": "SKILL.md",
            "managed_block_marker": _MANAGED_BLOCK_MARKER,
            "managed_block_version": _MANAGED_BLOCK_VERSION,
            "managed_block_fingerprint": _managed_block_fingerprint(managed_body),
            "last_attach_result": attach_result,
        },
    )


def _verify_attached(*, workspace_root: Path, skill_name: str, root: Path) -> None:
    for record in discover_skills(workspace_root):
        if record.name == skill_name and record.root == root:
            if record.state is IntegrationState.ATTACHED:
                return
            reason = f": {record.reason}" if record.reason else ""
            raise RuntimeError(f"Failed to attach '{skill_name}'{reason}")
    raise RuntimeError(f"Failed to attach '{skill_name}': target disappeared during verification")


def _read_existing_config(config_path: Path) -> dict[str, Any]:
    try:
        return read_yaml(config_path)
    except (ValueError, yaml.YAMLError):
        return {}


def _build_config(*, skill_name: str, existing_config: dict[str, Any]) -> dict[str, Any]:
    config: dict[str, Any] = {
        "schema_version": _CONFIG_SCHEMA_VERSION,
        "target_skill": skill_name,
        "skill_path": "SKILL.md",
        "debug_output_root": "skill-debug-logs",
        "auto_debug_allowed": True,
        "default_review_mode": "async",
        "default_backend_profile": "noop",
        "manual_debug_command": _manual_debug_command(skill_name),
    }
    if _should_preserve_skill_output_root(existing_config.get("skill_output_root")):
        config["skill_output_root"] = existing_config["skill_output_root"]
    existing_backend = existing_config.get("default_backend_profile")
    if isinstance(existing_backend, str) and existing_backend.strip():
        config["default_backend_profile"] = existing_backend.strip()
    return config


def _should_preserve_skill_output_root(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return False


def _manual_debug_command(skill_name: str) -> str:
    return f"/skill-debug 调试 {skill_name}"


def _dump_yaml(payload: dict[str, Any]) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def _refresh_managed_block(document: str, *, marker: str, body: str) -> str:
    start = f"<!-- {marker}:managed:start -->"
    end = f"<!-- {marker}:managed:end -->"
    lines = document.splitlines()
    standalone_start_lines = [index for index, line in enumerate(lines) if line.strip() == start]
    standalone_end_lines = [index for index, line in enumerate(lines) if line.strip() == end]
    start_count = len(standalone_start_lines)
    end_count = len(standalone_end_lines)
    managed_block = _managed_block(start=start, body=body, end=end)

    if start_count == 0 and end_count == 0:
        return _append_managed_block(document=document, managed_block=managed_block)
    if start_count == 1 and end_count == 1 and standalone_start_lines[0] < standalone_end_lines[0]:
        return _replace_balanced_managed_block(
            document=document,
            start=start,
            end=end,
            managed_block=managed_block,
        )
    cleaned = _strip_existing_managed_regions(document=document, start=start, end=end)
    return _append_managed_block(document=cleaned, managed_block=managed_block)


def _strip_existing_managed_regions(*, document: str, start: str, end: str) -> str:
    lines = document.splitlines()
    cleaned_lines: list[str] = []
    previous_marker: str | None = None
    content_since_previous_marker = False
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped == start:
            next_marker_index = _find_next_marker_index(lines=lines, start=index + 1, start_marker=start, end_marker=end)
            can_remove_balanced_region = (
                next_marker_index is not None
                and lines[next_marker_index].strip() == end
                and not (previous_marker == start and not content_since_previous_marker)
            )
            if can_remove_balanced_region:
                previous_marker = end
                content_since_previous_marker = False
                index = next_marker_index + 1
                continue
            previous_marker = start
            content_since_previous_marker = False
            index += 1
            continue
        if stripped == end:
            previous_marker = end
            content_since_previous_marker = False
            index += 1
            continue
        cleaned_lines.append(line)
        content_since_previous_marker = True
        index += 1
    if not cleaned_lines:
        return ""
    return "\n".join(cleaned_lines) + "\n"


def _find_next_marker_index(*, lines: list[str], start: int, start_marker: str, end_marker: str) -> int | None:
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped == start_marker or stripped == end_marker:
            return index
    return None


def _managed_block(*, start: str, body: str, end: str) -> str:
    return f"{start}\n{body}\n{end}"


def _append_managed_block(*, document: str, managed_block: str) -> str:
    base = document.rstrip("\n")
    if not base:
        return managed_block + "\n"
    return f"{base}\n\n{managed_block}\n"


def _replace_balanced_managed_block(*, document: str, start: str, end: str, managed_block: str) -> str:
    lines = document.splitlines()
    start_line_index = next(index for index, line in enumerate(lines) if line.strip() == start)
    end_line_index = next(index for index, line in enumerate(lines[start_line_index + 1 :], start_line_index + 1) if line.strip() == end)
    prefix_lines = lines[:start_line_index]
    suffix_lines = lines[end_line_index + 1 :]
    prefix = "\n".join(prefix_lines).rstrip("\n")
    suffix = "\n".join(suffix_lines).lstrip("\n")
    parts = [part for part in [prefix, managed_block, suffix] if part]
    return "\n".join(parts).rstrip("\n") + "\n"


def _managed_block_fingerprint(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _render_template(template_name: str, **replacements: str) -> str:
    template_path = _module_root() / "templates" / template_name
    rendered = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
    return rendered.rstrip() + "\n"


def _module_root() -> Path:
    return Path(__file__).resolve().parents[3]
