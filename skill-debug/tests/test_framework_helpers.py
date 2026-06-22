from pathlib import Path

import pytest

from skill_debug_tools.common.files import atomic_write_text, ensure_parent, read_yaml, write_json
from skill_debug_tools.common.markdown import replace_managed_block


def test_atomic_write_text_creates_parent(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "artifact.md"
    atomic_write_text(target, "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"


def test_write_json_writes_sorted_json(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    write_json(target, {"b": 2, "a": 1})
    assert target.read_text(encoding="utf-8") == '{\n  "a": 1,\n  "b": 2\n}\n'


def test_replace_managed_block_rewrites_existing_region() -> None:
    original = """Before
<!-- skill-debug:managed:start -->
old
<!-- skill-debug:managed:end -->
After
"""
    updated = replace_managed_block(original, marker="skill-debug", body="new line")
    assert "old" not in updated
    assert "new line" in updated


def test_read_yaml_returns_empty_mapping_for_missing_file(tmp_path: Path) -> None:
    assert read_yaml(tmp_path / "missing.yaml") == {}


def test_read_yaml_parses_mapping_content(tmp_path: Path) -> None:
    target = tmp_path / "config.yaml"
    atomic_write_text(target, "name: demo\ncount: 2\n")

    assert read_yaml(target) == {"name": "demo", "count": 2}


def test_read_yaml_rejects_non_mapping_content(tmp_path: Path) -> None:
    target = tmp_path / "list.yaml"
    atomic_write_text(target, "- one\n- two\n")

    with pytest.raises(ValueError, match="YAML document must be a mapping"):
        read_yaml(target)
