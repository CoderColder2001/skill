from __future__ import annotations

import json
from pathlib import Path

import pytest

from skill_debug_tools.common.files import atomic_write_text, read_yaml
from skill_debug_tools.attach import attach_skill
from skill_debug_tools.attach.target import _refresh_managed_block
from skill_debug_tools.workspace.discovery import IntegrationState, discover_skills

_MANAGED_BLOCK_START = "<!-- skill-debug:managed:start -->"
_MANAGED_BLOCK_END = "<!-- skill-debug:managed:end -->"


def _skill_document(name: str, *, body: str = "# Skill\n") -> str:
    return f"---\nname: {name}\ndescription: test skill\n---\n\n{body}"


def _expected_managed_body(skill_name: str) -> str:
    return "\n".join(
        [
            "## Debug Capability",
            "",
            "This skill supports `skill-debug`.",
            "",
            "- Debug support: enabled",
            "- Debug config: `skill-debug/config.yaml`",
            "- Debug log root: `skill-debug-logs`",
            f"- Manual debug command: `/skill-debug 调试 {skill_name}`",
        ]
    )


def _expected_managed_block(skill_name: str) -> str:
    return f"{_MANAGED_BLOCK_START}\n{_expected_managed_body(skill_name)}\n{_MANAGED_BLOCK_END}"


def _expected_config(skill_name: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "target_skill": skill_name,
        "skill_path": "SKILL.md",
        "debug_output_root": "skill-debug-logs",
        "auto_debug_allowed": True,
        "default_review_mode": "async",
        "default_backend_profile": "noop",
        "manual_debug_command": f"/skill-debug 调试 {skill_name}",
    }


def _assert_canonical_managed_block(document: str, *, skill_name: str) -> None:
    assert document.count(_expected_managed_block(skill_name)) == 1
    lines = document.splitlines()
    start_index = next(index for index, line in enumerate(lines) if line.strip() == _MANAGED_BLOCK_START)
    end_index = next(
        index for index, line in enumerate(lines[start_index + 1 :], start_index + 1) if line.strip() == _MANAGED_BLOCK_END
    )
    assert sum(1 for line in lines if line.strip() == _MANAGED_BLOCK_START) == 1
    assert sum(1 for line in lines if line.strip() == _MANAGED_BLOCK_END) == 1
    managed_block = "\n".join(lines[start_index : end_index + 1])
    assert managed_block == _expected_managed_block(skill_name)
    assert "{{" not in managed_block
    assert "}}" not in managed_block


def test_attach_skill_creates_target_local_integration_files_on_first_attach(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "attached"

    integration_root = skill_root / "skill-debug"
    assert (integration_root / "config.yaml").exists()
    assert (integration_root / "evaluation-guide.md").exists()
    assert (integration_root / "review-prompt.md").exists()
    assert (integration_root / "injection-state.json").exists()

    config = read_yaml(integration_root / "config.yaml")
    assert config == _expected_config("code-analyse")

    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")
    assert skill_document.count("## Debug Capability") == 1
    assert "skill-debug/targets/code-analyse" not in skill_document

    state = json.loads((integration_root / "injection-state.json").read_text(encoding="utf-8"))
    assert state["schema_version"] == 1
    assert state["target_skill"] == "code-analyse"
    assert state["skill_path"] == "SKILL.md"
    assert state["managed_block_marker"] == "skill-debug"
    assert state["managed_block_version"] == 1
    assert state["managed_block_fingerprint"]
    assert state["last_attach_result"] == "attached"

    records = discover_skills(tmp_path)
    assert len(records) == 1
    assert records[0].state is IntegrationState.ATTACHED
    assert records[0].reason is None


def test_attach_skill_renders_target_local_templates_without_unresolved_placeholders(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))

    attach_skill(tmp_path, "code-analyse")

    guide = (skill_root / "skill-debug" / "evaluation-guide.md").read_text(encoding="utf-8")
    assert "# code-analyse Evaluation Guide" in guide
    assert "`/skill-debug 调试 code-analyse`" in guide
    assert "`skill-debug-logs`" in guide
    assert "{{" not in guide
    assert "}}" not in guide

    prompt = (skill_root / "skill-debug" / "review-prompt.md").read_text(encoding="utf-8")
    assert "# code-analyse Review Prompt Overlay" in prompt
    assert "`code-analyse`" in prompt
    assert "`skill-debug-logs`" in prompt
    assert "{{" not in prompt
    assert "}}" not in prompt


def test_attach_skill_is_idempotent_and_preserves_target_owned_guide_and_prompt(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))

    first_result = attach_skill(tmp_path, "code-analyse")
    assert first_result == "attached"

    guide_path = skill_root / "skill-debug" / "evaluation-guide.md"
    prompt_path = skill_root / "skill-debug" / "review-prompt.md"
    atomic_write_text(guide_path, "# Custom Guide\nKeep this.\n")
    atomic_write_text(prompt_path, "# Custom Prompt\nKeep this too.\n")

    second_result = attach_skill(tmp_path, "code-analyse")

    assert second_result == "already_aligned"
    assert guide_path.read_text(encoding="utf-8") == "# Custom Guide\nKeep this.\n"
    assert prompt_path.read_text(encoding="utf-8") == "# Custom Prompt\nKeep this too.\n"


def test_attach_skill_repairs_stray_start_marker_without_dropping_target_owned_content(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=(
                "# Code Analyse\n\n"
                f"{_MANAGED_BLOCK_START}\n"
                "## Target-Owned Notes\n"
                "Keep this section.\n"
            ),
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "## Target-Owned Notes\nKeep this section.\n" in skill_document
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")


def test_attach_skill_repairs_duplicate_managed_blocks_without_dropping_content_between_them(
    tmp_path: Path,
) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=(
                "# Code Analyse\n\n"
                f"{_expected_managed_block('code-analyse')}\n\n"
                "## Keep This Section\n"
                "Target-owned content between duplicate blocks.\n\n"
                f"{_expected_managed_block('code-analyse')}\n"
            ),
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "## Keep This Section\nTarget-owned content between duplicate blocks.\n" in skill_document
    assert skill_document.count("## Debug Capability") == 1
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")


def test_attach_skill_repairs_end_before_start_markers_and_preserves_unrelated_content(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=(
                "# Code Analyse\n\n"
                f"{_MANAGED_BLOCK_END}\n"
                "## Keep This Section\n"
                "Target-owned content survives malformed ordering.\n"
                f"{_MANAGED_BLOCK_START}\n"
            ),
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "## Keep This Section\nTarget-owned content survives malformed ordering.\n" in skill_document
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")


def test_attach_skill_repairs_stray_start_before_valid_block_and_preserves_target_owned_content(
    tmp_path: Path,
) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=(
                "# Code Analyse\n\n"
                f"{_MANAGED_BLOCK_START}\n"
                "## Keep This Section\n"
                "Preserve this target-owned content.\n\n"
                f"{_expected_managed_block('code-analyse')}\n"
            ),
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "## Keep This Section\nPreserve this target-owned content.\n" in skill_document
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")


def test_attach_skill_repairs_nested_standalone_markers_without_swallowing_target_owned_content(
    tmp_path: Path,
) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=(
                "# Code Analyse\n\n"
                f"{_MANAGED_BLOCK_START}\n"
                f"{_MANAGED_BLOCK_START}\n"
                "## Keep This Section\n"
                "Nested malformed markers must not swallow this content.\n"
                f"{_MANAGED_BLOCK_END}\n"
                f"{_MANAGED_BLOCK_END}\n"
            ),
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert "## Keep This Section\nNested malformed markers must not swallow this content.\n" in skill_document
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")


def test_attach_skill_repairs_malformed_markers_without_trimming_trailing_spaces_from_target_content(
    tmp_path: Path,
) -> None:
    skill_root = tmp_path / "code-analyse"
    trailing_space_line = "Keep this line with two spaces.  "
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=(
                "# Code Analyse\n\n"
                f"{_MANAGED_BLOCK_START}\n"
                f"{trailing_space_line}\n"
            ),
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    skill_document = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    assert f"{trailing_space_line}\n" in skill_document
    _assert_canonical_managed_block(skill_document, skill_name="code-analyse")


def test_refresh_managed_block_preserves_literal_inline_marker_prose_and_appends_managed_block() -> None:
    inline_sentence = (
        "    Use <!-- skill-debug:managed:start -->literal<!-- skill-debug:managed:end --> markers here."
    )
    original_document = _skill_document(
        "code-analyse",
        body=f"# Code Analyse\n\nDetails:\n\n{inline_sentence}\n",
    )

    updated_document = _refresh_managed_block(
        original_document,
        marker="skill-debug",
        body=_expected_managed_body("code-analyse"),
    )

    assert inline_sentence in updated_document
    _assert_canonical_managed_block(updated_document, skill_name="code-analyse")
    expected_prefix = original_document.rstrip()
    expected_suffix = _expected_managed_block("code-analyse")
    assert updated_document == f"{expected_prefix}\n\n{expected_suffix}\n"


def test_refresh_managed_block_replaces_balanced_block_without_stripping_suffix_indentation() -> None:
    original_document = _skill_document(
        "code-analyse",
        body=(
            "# Code Analyse\n\n"
            f"{_expected_managed_block('code-analyse')}\n"
            "    Indented suffix line must stay indented.\n"
        ),
    )

    updated_document = _refresh_managed_block(
        original_document,
        marker="skill-debug",
        body=_expected_managed_body("code-analyse"),
    )

    assert "    Indented suffix line must stay indented.\n" in updated_document
    _assert_canonical_managed_block(updated_document, skill_name="code-analyse")


def test_refresh_managed_block_replaces_balanced_block_without_trimming_trailing_spaces_from_final_suffix_line() -> None:
    trailing_space_line = "Final suffix line keeps two spaces.  "
    original_document = _skill_document(
        "code-analyse",
        body=(
            "# Code Analyse\n\n"
            f"{_expected_managed_block('code-analyse')}\n"
            f"{trailing_space_line}\n"
        ),
    )

    updated_document = _refresh_managed_block(
        original_document,
        marker="skill-debug",
        body=_expected_managed_body("code-analyse"),
    )

    assert f"{trailing_space_line}\n" in updated_document
    _assert_canonical_managed_block(updated_document, skill_name="code-analyse")


def test_attach_skill_repairs_broken_partial_integration_and_preserves_existing_owned_values(
    tmp_path: Path,
) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(skill_root / "SKILL.md", _skill_document("code-analyse", body="# Code Analyse\n"))
    atomic_write_text(
        skill_root / "skill-debug" / "config.yaml",
        (
            "schema_version: 1\n"
            "target_skill: code-analyse\n"
            "skill_path: SKILL.md\n"
            "skill_output_root: custom-output\n"
            "debug_output_root: old-debug-root\n"
            "auto_debug_allowed: false\n"
            "default_review_mode: sync\n"
            "default_backend_profile: custom-backend\n"
            "manual_debug_command: /tmp/old\n"
        ),
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"

    integration_root = skill_root / "skill-debug"
    config = read_yaml(integration_root / "config.yaml")
    assert config["schema_version"] == 1
    assert config["target_skill"] == "code-analyse"
    assert config["skill_path"] == "SKILL.md"
    assert config["skill_output_root"] == "custom-output"
    assert config["debug_output_root"] == "skill-debug-logs"
    assert config["auto_debug_allowed"] is True
    assert config["default_review_mode"] == "async"
    assert config["default_backend_profile"] == "custom-backend"
    assert config["manual_debug_command"] == "/skill-debug 调试 code-analyse"

    state = json.loads((integration_root / "injection-state.json").read_text(encoding="utf-8"))
    assert state["last_attach_result"] == "repaired"

    records = discover_skills(tmp_path)
    assert len(records) == 1
    assert records[0].state is IntegrationState.ATTACHED
    assert records[0].reason is None


def test_attach_skill_repairs_parseable_non_mapping_config_to_canonical_shape(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    integration_root = skill_root / "skill-debug"
    atomic_write_text(
        skill_root / "SKILL.md",
        _skill_document(
            "code-analyse",
            body=f"# Code Analyse\n\n{_expected_managed_block('code-analyse')}\n",
        ),
    )
    atomic_write_text(integration_root / "config.yaml", "- stale\n- config\n")
    atomic_write_text(integration_root / "evaluation-guide.md", "# Existing Guide\n")
    atomic_write_text(integration_root / "review-prompt.md", "# Existing Prompt\n")
    atomic_write_text(
        integration_root / "injection-state.json",
        json.dumps(
            {
                "schema_version": 1,
                "target_skill": "code-analyse",
                "skill_path": "SKILL.md",
                "managed_block_marker": "skill-debug",
                "managed_block_version": 1,
                "managed_block_fingerprint": "placeholder",
            }
        )
        + "\n",
    )

    result = attach_skill(tmp_path, "code-analyse")

    assert result == "repaired"
    assert read_yaml(integration_root / "config.yaml") == _expected_config("code-analyse")


def test_attach_skill_raises_clear_error_for_unknown_skill_name(tmp_path: Path) -> None:
    atomic_write_text((tmp_path / "code-analyse" / "SKILL.md"), _skill_document("code-analyse"))

    with pytest.raises(ValueError, match="Unknown skill name 'missing-skill'"):
        attach_skill(tmp_path, "missing-skill")


def test_attach_skill_raises_clear_error_for_ambiguous_skill_name(tmp_path: Path) -> None:
    atomic_write_text((tmp_path / "alpha" / "SKILL.md"), _skill_document("shared-name"))
    atomic_write_text((tmp_path / "beta" / "SKILL.md"), _skill_document("shared-name"))

    with pytest.raises(ValueError, match="Ambiguous skill name 'shared-name'"):
        attach_skill(tmp_path, "shared-name")
