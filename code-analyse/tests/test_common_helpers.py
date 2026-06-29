from pathlib import Path

from skill_tools.common.files import atomic_write_text, ensure_parent, read_yaml
from skill_tools.common.markdown import replace_managed_block, render_bullet_list


def test_atomic_write_text_creates_parent(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "file.md"
    atomic_write_text(target, "hello\n")
    assert target.read_text() == "hello\n"


def test_replace_managed_block_rewrites_existing_region() -> None:
    original = """Before
<!-- skill-debug:managed:start -->
old
<!-- skill-debug:managed:end -->
After
"""
    updated = replace_managed_block(
        original,
        marker="skill-debug",
        body="new line",
    )
    assert "old" not in updated
    assert "new line" in updated


def test_render_bullet_list_preserves_backticks() -> None:
    rendered = render_bullet_list(["`code-analyse-docs/`", "`skill-debug-logs/`"])
    assert rendered.splitlines() == ["- `code-analyse-docs/`", "- `skill-debug-logs/`"]
