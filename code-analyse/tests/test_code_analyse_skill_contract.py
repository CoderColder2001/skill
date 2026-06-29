from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_code_analyse_skill_references_run_tracking_commands() -> None:
    document = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "current-run.md" in document
    assert "future-work.md" in document
    assert "python3 scripts/code_analyse_run_tracking.py start" in document
    assert "Do not place debug logs in `code-analyse-docs/`" in document
    assert "Debug config: `skill-debug/config.yaml`" in document
    assert "Debug log root: `skill-debug-logs`" in document
    assert "Manual debug command: `/skill-debug 调试 code-analyse`" in document
