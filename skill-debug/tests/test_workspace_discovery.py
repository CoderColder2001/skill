from __future__ import annotations

import hashlib
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text, write_json
from skill_debug_tools.workspace.discovery import IntegrationState, discover_skills


def _skill_document(*, managed_body: str | None = None) -> str:
    document = "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n"
    if managed_body is None:
        return document
    return (
        f"{document}\n"
        "<!-- skill-debug:managed:start -->\n"
        f"{managed_body}\n"
        "<!-- skill-debug:managed:end -->\n"
    )


def _managed_body() -> str:
    return "\n".join(
        [
            "## Debug Capability",
            "",
            "- Debug support: enabled",
            "- Debug config: `skill-debug/config.yaml`",
            "- Debug log root: `skill-debug-logs`",
            "- Manual debug command: `/skill-debug 调试 code-analyse`",
        ]
    )


def _managed_block_fingerprint(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def test_discover_skills_marks_skill_without_local_config_as_attachable(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document())

    results = discover_skills(tmp_path)

    assert [item.name for item in results] == ["code-analyse"]
    assert results[0].state is IntegrationState.ATTACHABLE
    assert results[0].reason is None


def test_discover_skills_marks_skill_with_missing_integration_files_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document())
    atomic_write_text(
        skill_root / "skill-debug" / "config.yaml",
        "schema_version: 1\ntarget_skill: code-analyse\nskill_path: SKILL.md\ndebug_output_root: skill-debug-logs\n",
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "missing integration files: evaluation-guide.md, review-prompt.md, injection-state.json"


def test_discover_skills_marks_fingerprint_mismatch_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    body = _managed_body()
    atomic_write_text(skill_root / "SKILL.md", _skill_document(managed_body=body))
    atomic_write_text(
        skill_root / "skill-debug" / "config.yaml",
        "schema_version: 1\ntarget_skill: code-analyse\nskill_path: SKILL.md\ndebug_output_root: skill-debug-logs\n",
    )
    atomic_write_text(skill_root / "skill-debug" / "evaluation-guide.md", "# Guide\n")
    atomic_write_text(skill_root / "skill-debug" / "review-prompt.md", "# Overlay\n")
    write_json(
        skill_root / "skill-debug" / "injection-state.json",
        {
            "schema_version": 1,
            "target_skill": "code-analyse",
            "skill_path": "SKILL.md",
            "managed_block_marker": "skill-debug",
            "managed_block_fingerprint": "not-the-right-fingerprint",
        },
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "managed block fingerprint does not match SKILL.md"


def test_discover_skills_marks_fully_aligned_skill_as_attached(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    body = _managed_body()
    atomic_write_text(skill_root / "SKILL.md", _skill_document(managed_body=body))
    atomic_write_text(
        skill_root / "skill-debug" / "config.yaml",
        "schema_version: 1\ntarget_skill: code-analyse\nskill_path: SKILL.md\ndebug_output_root: skill-debug-logs\n",
    )
    atomic_write_text(skill_root / "skill-debug" / "evaluation-guide.md", "# Guide\n")
    atomic_write_text(skill_root / "skill-debug" / "review-prompt.md", "# Overlay\n")
    write_json(
        skill_root / "skill-debug" / "injection-state.json",
        {
            "schema_version": 1,
            "target_skill": "code-analyse",
            "skill_path": "SKILL.md",
            "managed_block_marker": "skill-debug",
            "managed_block_fingerprint": _managed_block_fingerprint(body),
        },
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.ATTACHED
    assert results[0].reason is None
