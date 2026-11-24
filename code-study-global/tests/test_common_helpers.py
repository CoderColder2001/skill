from pathlib import Path

from skill_tools.common.files import atomic_write_text


def test_atomic_write_text_creates_parent(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "file.md"
    atomic_write_text(target, "hello\n")
    assert target.read_text() == "hello\n"
