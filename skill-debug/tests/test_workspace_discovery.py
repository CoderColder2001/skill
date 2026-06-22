from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

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


def _skill_document_with_suffix(suffix: str) -> str:
    return f"---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n{suffix}"


def _managed_body() -> str:
    return "\n".join(
        [
            "## Debug Capability",
            "",
            "This skill supports `skill-debug`.",
            "",
            "- Debug support: enabled",
            "- Debug config: `skill-debug/config.yaml`",
            "- Debug log root: `skill-debug-logs`",
            "- Manual debug command: `/skill-debug 调试 code-analyse`",
        ]
    )


def _managed_block_fingerprint(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _config_text(*, target_skill: str = "code-analyse", skill_path: str = "SKILL.md") -> str:
    return (
        "schema_version: 1\n"
        f"target_skill: {target_skill}\n"
        f"skill_path: {skill_path}\n"
        "debug_output_root: skill-debug-logs\n"
    )


def _write_attached_skill(
    skill_root: Path,
    *,
    managed_body: str | None = None,
    config_text: str | None = None,
    state_overrides: dict[str, object] | None = None,
) -> str:
    body = _managed_body() if managed_body is None else managed_body
    atomic_write_text(skill_root / "SKILL.md", _skill_document(managed_body=body))
    atomic_write_text(
        skill_root / "skill-debug" / "config.yaml",
        _config_text() if config_text is None else config_text,
    )
    atomic_write_text(skill_root / "skill-debug" / "evaluation-guide.md", "# Guide\n")
    atomic_write_text(skill_root / "skill-debug" / "review-prompt.md", "# Overlay\n")
    state = {
        "schema_version": 1,
        "target_skill": "code-analyse",
        "skill_path": "SKILL.md",
        "managed_block_marker": "skill-debug",
        "managed_block_fingerprint": _managed_block_fingerprint(body),
    }
    if state_overrides:
        state.update(state_overrides)
    write_json(skill_root / "skill-debug" / "injection-state.json", state)
    return body


def test_discover_skills_marks_pristine_skill_without_local_integration_as_attachable(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document())

    results = discover_skills(tmp_path)

    assert [item.name for item in results] == ["code-analyse"]
    assert results[0].state is IntegrationState.ATTACHABLE
    assert results[0].reason is None


def test_discover_skills_marks_stale_managed_block_without_local_files_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document(managed_body=_managed_body()))

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "missing integration files: config.yaml, evaluation-guide.md, review-prompt.md, injection-state.json"


def test_discover_skills_marks_start_marker_only_without_local_files_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document_with_suffix("<!-- skill-debug:managed:start -->\n"),
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "missing integration files: config.yaml, evaluation-guide.md, review-prompt.md, injection-state.json"


def test_discover_skills_marks_end_marker_only_without_local_files_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document_with_suffix("<!-- skill-debug:managed:end -->\n"),
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "missing integration files: config.yaml, evaluation-guide.md, review-prompt.md, injection-state.json"


def test_discover_skills_marks_partial_integration_without_config_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document())
    atomic_write_text(skill_root / "skill-debug" / "evaluation-guide.md", "# Guide\n")

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "missing integration files: config.yaml, review-prompt.md, injection-state.json"


def test_discover_skills_marks_empty_integration_directory_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document())
    (skill_root / "skill-debug").mkdir(parents=True)

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "missing integration files: config.yaml, evaluation-guide.md, review-prompt.md, injection-state.json"


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
    _write_attached_skill(
        skill_root,
        state_overrides={
            "managed_block_fingerprint": "not-the-right-fingerprint",
        },
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "managed block fingerprint does not match SKILL.md"


def test_discover_skills_parses_quoted_frontmatter_name(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        "---\nname: \"code-analyse\"\ndescription: \"analyse\"\n---\n\n# Code Analyse\n",
    )

    results = discover_skills(tmp_path)

    assert [item.name for item in results] == ["code-analyse"]
    assert results[0].state is IntegrationState.ATTACHABLE


@pytest.mark.parametrize(
    "document",
    [
        pytest.param(
            "---\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="missing-name",
        ),
        pytest.param(
            "---\nname: \"\"\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="empty-string-name",
        ),
        pytest.param(
            "---\nname: \"   \"\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="whitespace-string-name",
        ),
        pytest.param(
            "---\nname: null\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="null-name",
        ),
        pytest.param(
            "---\nname: [code-analyse]\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="list-name",
        ),
        pytest.param(
            "---\nname: {value: code-analyse}\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="mapping-name",
        ),
    ],
)
def test_discover_skills_skips_skill_with_invalid_frontmatter_name(
    tmp_path: Path,
    document: str,
) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", document)

    results = discover_skills(tmp_path)

    assert results == []


def test_discover_skills_skips_skill_with_malformed_frontmatter_without_crashing(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        "---\nname: [code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
    )

    results = discover_skills(tmp_path)

    assert results == []


@pytest.mark.parametrize(
    "document",
    [
        pytest.param(
            "# Code Analyse\n",
            id="no-frontmatter-delimiters",
        ),
        pytest.param(
            "---\nname: code-analyse\ndescription: analyse\n\n# Code Analyse\n",
            id="unterminated-frontmatter",
        ),
        pytest.param(
            "\n---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
            id="frontmatter-not-at-start",
        ),
    ],
)
def test_discover_skills_skips_skill_with_non_discoverable_frontmatter_without_crashing(
    tmp_path: Path,
    document: str,
) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", document)

    results = discover_skills(tmp_path)

    assert results == []


def test_discover_skills_marks_malformed_config_yaml_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    _write_attached_skill(
        skill_root,
        config_text="target_skill: [code-analyse\n",
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "config.yaml is malformed"


def test_discover_skills_marks_parseable_non_mapping_config_yaml_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    _write_attached_skill(
        skill_root,
        config_text="- code-analyse\n- other-skill\n",
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "config.yaml is malformed"


def test_discover_skills_marks_malformed_injection_state_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    _write_attached_skill(skill_root)
    atomic_write_text(
        skill_root / "skill-debug" / "injection-state.json",
        "target_skill: [code-analyse\n",
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "injection-state.json is malformed"


@pytest.mark.parametrize(
    "state_document",
    [
        pytest.param(
            "- code-analyse\n- other-skill\n",
            id="list",
        ),
        pytest.param(
            "code-analyse\n",
            id="scalar",
        ),
    ],
)
def test_discover_skills_marks_parseable_non_mapping_injection_state_as_broken(
    tmp_path: Path,
    state_document: str,
) -> None:
    skill_root = tmp_path / "code-analyse"
    _write_attached_skill(skill_root)
    atomic_write_text(
        skill_root / "skill-debug" / "injection-state.json",
        state_document,
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "injection-state.json is malformed"


def test_discover_skills_sorts_by_name_then_path(tmp_path: Path) -> None:
    atomic_write_text(
        tmp_path / "a-beta" / "one" / "SKILL.md",
        "---\nname: beta\ndescription: analyse\n---\n\n# Beta\n",
    )
    atomic_write_text(
        tmp_path / "c-alpha" / "two" / "SKILL.md",
        "---\nname: alpha\ndescription: analyse\n---\n\n# Alpha Two\n",
    )
    atomic_write_text(
        tmp_path / "b-alpha" / "three" / "SKILL.md",
        "---\nname: alpha\ndescription: analyse\n---\n\n# Alpha Three\n",
    )

    results = discover_skills(tmp_path)

    assert [(item.name, item.root.relative_to(tmp_path).as_posix()) for item in results] == [
        ("alpha", "b-alpha/three"),
        ("alpha", "c-alpha/two"),
        ("beta", "a-beta/one"),
    ]


@pytest.mark.parametrize(
    ("config_text", "state_overrides", "expected_reason"),
    [
        pytest.param(
            _config_text(skill_path=""),
            None,
            "config skill_path does not point at SKILL.md",
            id="config-empty-skill-path",
        ),
        pytest.param(
            _config_text(target_skill="other-skill"),
            None,
            "config target_skill does not match SKILL.md frontmatter name",
            id="config-target-skill",
        ),
        pytest.param(
            _config_text(skill_path="nested/SKILL.md"),
            None,
            "config skill_path does not point at SKILL.md",
            id="config-skill-path",
        ),
        pytest.param(
            None,
            {"target_skill": "other-skill"},
            "injection-state target_skill does not match SKILL.md frontmatter name",
            id="state-target-skill",
        ),
        pytest.param(
            None,
            {"skill_path": ""},
            "injection-state skill_path does not point at SKILL.md",
            id="state-empty-skill-path",
        ),
        pytest.param(
            None,
            {"skill_path": "nested/SKILL.md"},
            "injection-state skill_path does not point at SKILL.md",
            id="state-skill-path",
        ),
        pytest.param(
            None,
            {"managed_block_marker": "different-marker"},
            "injection-state managed_block_marker does not match skill-debug",
            id="state-managed-block-marker",
        ),
    ],
)
def test_discover_skills_marks_alignment_mismatch_as_broken(
    tmp_path: Path,
    config_text: str | None,
    state_overrides: dict[str, object] | None,
    expected_reason: str,
) -> None:
    skill_root = tmp_path / "code-analyse"
    _write_attached_skill(
        skill_root,
        config_text=config_text,
        state_overrides=state_overrides,
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == expected_reason


def test_discover_skills_marks_stale_self_consistent_managed_block_as_broken(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    stale_body = "\n".join(
        [
            "## Debug Capability",
            "",
            "This skill supports `skill-debug`.",
            "",
            "- Debug support: enabled",
            "- Debug config: `skill-debug/targets/code-analyse/config.yaml`",
            "- Debug log root: `skill-debug-logs/code-analyse`",
            "- Manual debug command: `/code-analyse-debug_mode`",
        ]
    )
    _write_attached_skill(
        skill_root,
        managed_body=stale_body,
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
    assert results[0].reason == "managed block content does not match current render rules"


def test_discover_skills_marks_fully_aligned_skill_as_attached(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    _write_attached_skill(skill_root)

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.ATTACHED
    assert results[0].reason is None
