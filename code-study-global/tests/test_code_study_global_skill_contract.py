from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_code_study_global_skill_references_global_output_and_tracking_commands() -> None:
    document = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "name: \"code-study-global\"" in document
    assert "Use only when the user explicitly invokes /code-study-global" in document
    assert "docs/code-study-global/" in document
    assert "index.md" in document
    assert "current-run.md" in document
    assert "future-work.md" in document
    assert "[run-tracking instructions](references/run-tracking.md)" in document
    tracking_guide = (ROOT / "references" / "run-tracking.md").read_text(encoding="utf-8")
    assert 'python3 "<skill-root>/scripts/code_study_global_run_tracking.py" start' in tracking_guide


def test_code_study_global_skill_requires_index_links_and_document_boundaries() -> None:
    document = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Cross-Document Link Rules" in document
    assert "Coverage Matrix Rules" in document
    assert "Previous`, `Next`, and `Related` links" in document
    assert "Put navigation and synthesis in `index.md`, stable structural maps in `maps/`, and focused mechanisms or chains in `topics/`" in document


def test_code_study_global_skill_requires_document_snapshots() -> None:
    document = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Document Snapshot Rules" in document
    assert "Every `index.md`, map document, and topic document must include a `Document Snapshot` section" in document
    assert "Project root." in document
    assert "Branch, or `detached HEAD` / `not a git repo` when appropriate." in document
    assert "HEAD full SHA." in document
    assert "HEAD time and subject." in document
    assert "Document update time, including timezone when available." in document
    assert "Source link style, such as `repo-relative links with visible line numbers`." in document
    assert "Whether `docs/code-study-global/` or parent `docs/` is ignored by git." in document


def test_code_study_global_skill_uses_snapshots_for_staleness_and_link_policy() -> None:
    document = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "Source baseline, such as HEAD short SHA or `not_recorded`." in document
    assert "mark the coverage row as `stale` with the newer HEAD noted" in document
    assert "Use repository-relative Markdown links from the generated document to source files by default" in document
    assert "verify linked source paths exist by resolving them relative to the generated Markdown file" in document
    assert "Snapshot fields that are missing branch, HEAD, document update time, source link style, or docs-ignore status." in document


def test_code_study_global_skill_is_not_module_scoped() -> None:
    document = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "This skill has one scope: the whole repository." in document
    assert "Do not create `scopes/<module>/` style module-local study trees." in document
    assert "use `code-study-module` instead" in document
