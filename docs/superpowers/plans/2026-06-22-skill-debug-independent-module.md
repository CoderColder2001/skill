# Skill Debug Independent Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract `skill-debug` into an independent workspace module, replace the central target registry with target-local integration files, and support `/skill-debug list` plus `/skill-debug 接入 <skill-name>`.

**Architecture:** Build a standalone `/Users/bytedance/workspace/skill/skill-debug` Python module that owns generic discovery, attach, debug-run, and review infrastructure. Move generic tests and reusable code into that module, keep `code-analyse` focused on its own business behavior, and make each target skill own local integration files under `<skill-root>/skill-debug/` and target-local logs under `<skill-root>/skill-debug-logs/`.

**Tech Stack:** Python 3.11, PyYAML, pytest, argparse, Markdown templates, JSON/YAML config, managed Markdown block replacement

---

## Planned File Structure

### Create

- `docs/superpowers/plans/2026-06-22-skill-debug-independent-module.md` - the implementation plan for the extraction and target-local integration work.
- `skill-debug/SKILL.md` - standalone framework skill contract for listing, attaching, and reviewing target skills.
- `skill-debug/pyproject.toml` - standalone package metadata and pytest configuration for the independent module.
- `skill-debug/.gitignore` - ignore local framework runtime state and caches while keeping committed templates and tests tracked.
- `skill-debug/src/skill_debug_tools/__init__.py` - package marker for the standalone framework.
- `skill-debug/src/skill_debug_tools/common/__init__.py` - package marker for shared framework helpers.
- `skill-debug/src/skill_debug_tools/common/files.py` - atomic file writes plus JSON/YAML helpers for the framework.
- `skill-debug/src/skill_debug_tools/common/markdown.py` - managed-block replacement and Markdown rendering helpers.
- `skill-debug/src/skill_debug_tools/workspace/__init__.py` - package marker for workspace discovery helpers.
- `skill-debug/src/skill_debug_tools/workspace/discovery.py` - scan workspace skills, parse `SKILL.md` frontmatter, and classify integration states.
- `skill-debug/src/skill_debug_tools/attach/__init__.py` - package marker for target attachment helpers.
- `skill-debug/src/skill_debug_tools/attach/target.py` - create and repair target-local integration files plus inject managed blocks.
- `skill-debug/src/skill_debug_tools/debug_run/__init__.py` - package marker for debug run lifecycle helpers.
- `skill-debug/src/skill_debug_tools/debug_run/lifecycle.py` - create target-local debug runs, append events, finalize runs, and reload runs safely.
- `skill-debug/src/skill_debug_tools/review/__init__.py` - package marker for review and queue helpers.
- `skill-debug/src/skill_debug_tools/review/run.py` - assemble review inputs from target-local assets and execute configured runners.
- `skill-debug/src/skill_debug_tools/review/queue.py` - shared queue file creation and state transitions under framework runtime.
- `skill-debug/scripts/skill_debug.py` - CLI entrypoint for `list`, `attach`, and later debug-facing subcommands.
- `skill-debug/templates/injected-debug-block.md` - canonical managed block template for target `SKILL.md` files.
- `skill-debug/templates/evaluation-guide.md` - initial target-local evaluation-guide template.
- `skill-debug/templates/review-prompt.md` - initial target-local review-overlay template.
- `skill-debug/templates/review.md` - framework review result wrapper template.
- `skill-debug/review_runners/noop.py` - deterministic offline review backend.
- `skill-debug/review_runners/openai_api.py` - HTTP and mock transport review backend.
- `skill-debug/review_runners/codex_thread.py` - mock Codex-thread runner for integration wiring.
- `skill-debug/runtime/config/backends.example.yaml` - example backend profile set for the framework.
- `skill-debug/tests/conftest.py` - framework temp workspace fixtures for discovery, attach, and review tests.
- `skill-debug/tests/test_workspace_discovery.py` - discovery and state classification tests.
- `skill-debug/tests/test_skill_debug_list.py` - CLI list behavior tests.
- `skill-debug/tests/test_skill_debug_attach.py` - attach, repair, and idempotency tests.
- `skill-debug/tests/test_debug_run_lifecycle.py` - target-local debug log lifecycle tests.
- `skill-debug/tests/test_review_run.py` - review input assembly and backend selection tests.
- `skill-debug/tests/test_review_queue.py` - queue creation and job transition tests.
- `skill-debug/tests/test_review_runners.py` - framework runner transport and error handling tests.
- `code-analyse/skill-debug/config.yaml` - target-local debug integration contract for `code-analyse`.
- `code-analyse/skill-debug/evaluation-guide.md` - target-local evaluation guide for `code-analyse`.
- `code-analyse/skill-debug/review-prompt.md` - target-local review overlay for `code-analyse`.
- `code-analyse/skill-debug/injection-state.json` - tool-managed injection fingerprint and target-local status file for `code-analyse`.
- `code-analyse/tests/test_code_analyse_skill_debug_integration.py` - `code-analyse` integration proof for the new target-local model.

### Modify

- `code-analyse/SKILL.md` - replace the old central-registry managed block with a target-local `skill-debug` block.
- `code-analyse/tests/test_code_analyse_skill_contract.py` - update contract assertions for the new managed block wording and local integration paths.
- `code-analyse/tests/conftest.py` - keep only fixtures still needed by `code-analyse` tests after generic framework tests move out.

### Delete

- `code-analyse/src/skill_tools/skill_debug/__init__.py` - remove the embedded generic framework package marker.
- `code-analyse/src/skill_tools/skill_debug/target_init.py` - remove the embedded target attachment helper.
- `code-analyse/src/skill_tools/skill_debug/debug_run.py` - remove the embedded debug lifecycle helper.
- `code-analyse/src/skill_tools/skill_debug/review_run.py` - remove the embedded review execution helper.
- `code-analyse/src/skill_tools/skill_debug/review_queue.py` - remove the embedded queue helper.
- `code-analyse/skill-debug/SKILL.md` - remove the embedded framework skill contract from inside `code-analyse`.
- `code-analyse/skill-debug/scripts/init_target.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/scripts/start_run.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/scripts/append_event.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/scripts/finalize_run.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/scripts/enqueue_review.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/scripts/review_worker.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/scripts/review_run.py` - remove old embedded framework CLI.
- `code-analyse/skill-debug/review_runners/base.py` - remove old embedded runner scaffolding.
- `code-analyse/skill-debug/review_runners/noop.py` - remove old embedded runner implementation.
- `code-analyse/skill-debug/review_runners/openai_api.py` - remove old embedded runner implementation.
- `code-analyse/skill-debug/review_runners/codex_thread.py` - remove old embedded runner implementation.
- `code-analyse/skill-debug/runtime/config/backends.example.yaml` - remove old embedded example backend config.
- `code-analyse/skill-debug/targets/code-analyse/config.yaml` - remove old central target asset.
- `code-analyse/skill-debug/targets/code-analyse/evaluation-guide.md` - remove old central target asset.
- `code-analyse/skill-debug/targets/code-analyse/review-prompt.md` - remove old central target asset.
- `code-analyse/skill-debug/targets/code-analyse/injection-state.json` - remove old central target asset.
- `code-analyse/tests/test_skill_debug_init_target.py` - move generic attachment tests to the standalone framework module.
- `code-analyse/tests/test_skill_debug_run_lifecycle.py` - move generic lifecycle tests to the standalone framework module.
- `code-analyse/tests/test_skill_debug_review_queue.py` - move generic queue tests to the standalone framework module.
- `code-analyse/tests/test_skill_debug_review_run.py` - move generic review tests to the standalone framework module.
- `code-analyse/tests/test_skill_debug_review_runners.py` - move generic runner tests to the standalone framework module.

### Preserve

- `code-analyse/pyproject.toml` - continue to package only `code-analyse` helpers.
- `code-analyse/src/skill_tools/common/*` - keep the common helpers used by `code-analyse` runtime tooling unless a later refactor deliberately moves them too.
- `code-analyse/src/skill_tools/code_analyse/*` - keep the business run-tracking helpers for `code-analyse`.
- `code-analyse/scripts/code_analyse_run_tracking.py` - keep `code-analyse` business run-tracking CLI.
- `code-analyse/tests/test_code_analyse_run_tracking.py` - keep business run-tracking coverage.

## Task 1: Bootstrap The Standalone `skill-debug` Module

**Files:**
- Create: `skill-debug/pyproject.toml`
- Create: `skill-debug/.gitignore`
- Create: `skill-debug/src/skill_debug_tools/__init__.py`
- Create: `skill-debug/src/skill_debug_tools/common/__init__.py`
- Create: `skill-debug/src/skill_debug_tools/common/files.py`
- Create: `skill-debug/src/skill_debug_tools/common/markdown.py`
- Create: `skill-debug/tests/conftest.py`
- Create: `skill-debug/tests/test_framework_helpers.py`
- Test: `skill-debug/tests/test_framework_helpers.py`

- [ ] **Step 1: Write the failing helper tests**

```python
from pathlib import Path

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
```

- [ ] **Step 2: Run the helper tests to verify they fail**

Run: `python3 -m pytest skill-debug/tests/test_framework_helpers.py -q`

Expected: FAIL with import errors for `skill_debug_tools.common.files` and `skill_debug_tools.common.markdown`

- [ ] **Step 3: Add standalone project metadata and ignore rules**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "skill-debug-tools"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "PyYAML>=6.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

```gitignore
__pycache__/
.pytest_cache/
.venv/
runtime/review-queue/
runtime/config/backends.local.yaml
```

- [ ] **Step 4: Implement the standalone common helpers**

```python
# skill-debug/src/skill_debug_tools/common/files.py
from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import yaml


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
```

```python
# skill-debug/src/skill_debug_tools/common/markdown.py
from __future__ import annotations

from textwrap import dedent


def replace_managed_block(document: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:managed:start -->"
    end = f"<!-- {marker}:managed:end -->"
    managed = dedent(
        f"""\
        {start}
        {body}
        {end}
        """
    ).rstrip()
    if start in document and end in document:
        prefix = document.split(start, 1)[0].rstrip()
        suffix = document.split(end, 1)[1].lstrip()
        return f"{prefix}\n{managed}\n{suffix}".rstrip() + "\n"
    return document.rstrip() + "\n\n" + managed + "\n"
```

- [ ] **Step 5: Re-run the helper tests**

Run: `python3 -m pytest skill-debug/tests/test_framework_helpers.py -q`

Expected: PASS with `4 passed`

- [ ] **Step 6: Commit the standalone bootstrap**

```bash
git add skill-debug/pyproject.toml skill-debug/.gitignore skill-debug/src/skill_debug_tools skill-debug/tests/conftest.py skill-debug/tests/test_framework_helpers.py
git commit -m "chore: bootstrap standalone skill-debug module"
```

## Task 2: Implement Workspace Discovery And Integration Status Classification

**Files:**
- Create: `skill-debug/src/skill_debug_tools/workspace/__init__.py`
- Create: `skill-debug/src/skill_debug_tools/workspace/discovery.py`
- Create: `skill-debug/tests/test_workspace_discovery.py`
- Test: `skill-debug/tests/test_workspace_discovery.py`

- [ ] **Step 1: Write the failing discovery tests**

```python
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text, write_json
from skill_debug_tools.workspace.discovery import IntegrationState, discover_skills


def test_discover_skills_marks_skill_without_local_config_as_attachable(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    atomic_write_text(
        skill_root / "SKILL.md",
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
    )

    results = discover_skills(tmp_path)

    assert [item.name for item in results] == ["code-analyse"]
    assert results[0].state is IntegrationState.ATTACHABLE


def test_discover_skills_marks_fully_aligned_skill_as_attached(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    document = (
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n\n"
        "<!-- skill-debug:managed:start -->\n"
        "## Debug Capability\n\n"
        "- Debug support: enabled\n"
        "- Debug config: `skill-debug/config.yaml`\n"
        "- Debug log root: `skill-debug-logs`\n"
        "- Manual debug command: `/skill-debug 调试 code-analyse`\n"
        "<!-- skill-debug:managed:end -->\n"
    )
    atomic_write_text(skill_root / "SKILL.md", document)
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
            "managed_block_marker": "skill-debug",
            "managed_block_fingerprint": "expected-fingerprint",
        },
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.BROKEN
```

- [ ] **Step 2: Run the discovery tests to verify they fail**

Run: `python3 -m pytest skill-debug/tests/test_workspace_discovery.py -q`

Expected: FAIL with import errors for `skill_debug_tools.workspace.discovery`

- [ ] **Step 3: Implement discovery models and parsing helpers**

```python
# skill-debug/src/skill_debug_tools/workspace/discovery.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from skill_debug_tools.common.files import read_yaml


class IntegrationState(str, Enum):
    ATTACHABLE = "attachable"
    ATTACHED = "attached"
    BROKEN = "broken"


@dataclass(frozen=True)
class SkillRecord:
    name: str
    root: Path
    skill_path: Path
    state: IntegrationState
    reason: str | None = None


def discover_skills(workspace_root: Path) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for skill_path in sorted(workspace_root.rglob("SKILL.md")):
        data = _read_skill_frontmatter(skill_path)
        name = str(data.get("name", "")).strip()
        if not name:
            continue
        root = skill_path.parent
        state, reason = classify_skill(root=root, skill_name=name, skill_path=skill_path)
        records.append(SkillRecord(name=name, root=root, skill_path=skill_path, state=state, reason=reason))
    return sorted(records, key=lambda item: (item.name, str(item.root)))
```

- [ ] **Step 4: Add target-local classification rules**

```python
def classify_skill(*, root: Path, skill_name: str, skill_path: Path) -> tuple[IntegrationState, str | None]:
    integration_root = root / "skill-debug"
    config_path = integration_root / "config.yaml"
    guide_path = integration_root / "evaluation-guide.md"
    overlay_path = integration_root / "review-prompt.md"
    state_path = integration_root / "injection-state.json"
    if not config_path.exists():
        return IntegrationState.ATTACHABLE, None
    required = [config_path, guide_path, overlay_path, state_path]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        return IntegrationState.BROKEN, f"missing integration files: {', '.join(missing)}"
    config = read_yaml(config_path)
    if str(config.get("target_skill", "")).strip() != skill_name:
        return IntegrationState.BROKEN, "config target_skill does not match SKILL.md frontmatter name"
    document = skill_path.read_text(encoding="utf-8")
    if "<!-- skill-debug:managed:start -->" not in document or "<!-- skill-debug:managed:end -->" not in document:
        return IntegrationState.BROKEN, "missing skill-debug managed block"
    return IntegrationState.ATTACHED, None
```

- [ ] **Step 5: Tighten the tests to assert the true attached state**

```python
from skill_debug_tools.attach.target import managed_block_fingerprint, render_managed_block


def test_discover_skills_marks_fully_aligned_skill_as_attached(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    body = render_managed_block(skill_name="code-analyse")
    atomic_write_text(
        skill_root / "SKILL.md",
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n\n"
        f"<!-- skill-debug:managed:start -->\n{body}\n<!-- skill-debug:managed:end -->\n",
    )
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
            "managed_block_marker": "skill-debug",
            "managed_block_fingerprint": managed_block_fingerprint(skill_name="code-analyse"),
        },
    )

    results = discover_skills(tmp_path)

    assert results[0].state is IntegrationState.ATTACHED
```

- [ ] **Step 6: Re-run the discovery tests**

Run: `python3 -m pytest skill-debug/tests/test_workspace_discovery.py -q`

Expected: PASS with `2 passed`

- [ ] **Step 7: Commit discovery and status classification**

```bash
git add skill-debug/src/skill_debug_tools/workspace skill-debug/tests/test_workspace_discovery.py
git commit -m "feat: add workspace skill discovery"
```

## Task 3: Implement Target-Local Attach And Repair

**Files:**
- Create: `skill-debug/src/skill_debug_tools/attach/__init__.py`
- Create: `skill-debug/src/skill_debug_tools/attach/target.py`
- Create: `skill-debug/templates/injected-debug-block.md`
- Create: `skill-debug/templates/evaluation-guide.md`
- Create: `skill-debug/templates/review-prompt.md`
- Create: `skill-debug/tests/test_skill_debug_attach.py`
- Test: `skill-debug/tests/test_skill_debug_attach.py`

- [ ] **Step 1: Write the failing attach tests**

```python
from pathlib import Path

from skill_debug_tools.attach.target import attach_skill, AttachResult
from skill_debug_tools.workspace.discovery import IntegrationState, discover_skills


def test_attach_skill_creates_target_local_integration_files(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    (skill_root / "docs").mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
        encoding="utf-8",
    )

    result = attach_skill(workspace_root=tmp_path, skill_name="code-analyse")

    assert result.status == "attached"
    assert (skill_root / "skill-debug" / "config.yaml").exists()
    assert (skill_root / "skill-debug" / "evaluation-guide.md").exists()
    assert (skill_root / "skill-debug" / "review-prompt.md").exists()
    assert (skill_root / "skill-debug" / "injection-state.json").exists()
    assert "`skill-debug/config.yaml`" in (skill_root / "SKILL.md").read_text(encoding="utf-8")


def test_attach_skill_is_idempotent_and_preserves_target_owned_prompts(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    (skill_root / "SKILL.md").write_text(
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
        encoding="utf-8",
    )
    attach_skill(workspace_root=tmp_path, skill_name="code-analyse")
    custom_prompt = "# Custom Overlay\n\nKeep this text.\n"
    (skill_root / "skill-debug" / "review-prompt.md").write_text(custom_prompt, encoding="utf-8")

    result = attach_skill(workspace_root=tmp_path, skill_name="code-analyse")

    assert result.status == "already_aligned"
    assert (skill_root / "skill-debug" / "review-prompt.md").read_text(encoding="utf-8") == custom_prompt


def test_attach_skill_repairs_partial_integration_state(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    (skill_root / "SKILL.md").write_text(
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
        encoding="utf-8",
    )
    (skill_root / "skill-debug").mkdir(parents=True)
    (skill_root / "skill-debug" / "config.yaml").write_text("target_skill: wrong-skill\n", encoding="utf-8")

    result = attach_skill(workspace_root=tmp_path, skill_name="code-analyse")
    states = discover_skills(tmp_path)

    assert result.status == "repaired"
    assert states[0].state is IntegrationState.ATTACHED
```

- [ ] **Step 2: Run the attach tests to verify they fail**

Run: `python3 -m pytest skill-debug/tests/test_skill_debug_attach.py -q`

Expected: FAIL with import errors for `skill_debug_tools.attach.target`

- [ ] **Step 3: Implement managed block rendering and target-local defaults**

```python
# skill-debug/src/skill_debug_tools/attach/target.py
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text, read_yaml, write_json
from skill_debug_tools.common.markdown import replace_managed_block
from skill_debug_tools.workspace.discovery import discover_skills


@dataclass(frozen=True)
class AttachResult:
    skill_name: str
    skill_root: Path
    status: str


def render_managed_block(*, skill_name: str) -> str:
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


def managed_block_fingerprint(*, skill_name: str) -> str:
    return hashlib.sha256(render_managed_block(skill_name=skill_name).encode("utf-8")).hexdigest()
```

- [ ] **Step 4: Implement attach, repair, and local file preservation**

```python
def attach_skill(*, workspace_root: Path, skill_name: str) -> AttachResult:
    matches = [item for item in discover_skills(workspace_root) if item.name == skill_name]
    if not matches:
        raise ValueError(f"Unknown skill `{skill_name}`.")
    if len(matches) != 1:
        raise ValueError(f"Skill name `{skill_name}` is ambiguous.")
    record = matches[0]
    skill_root = record.root
    integration_root = skill_root / "skill-debug"
    config_path = integration_root / "config.yaml"
    guide_path = integration_root / "evaluation-guide.md"
    overlay_path = integration_root / "review-prompt.md"
    state_path = integration_root / "injection-state.json"
    existing = read_yaml(config_path)
    config_lines = [
        "schema_version: 1",
        f"target_skill: {skill_name}",
        "skill_path: SKILL.md",
        f"skill_output_root: {existing.get('skill_output_root', 'code-analyse-docs')}",
        "debug_output_root: skill-debug-logs",
        "auto_debug_allowed: true",
        "default_review_mode: async",
        f"default_backend_profile: {existing.get('default_backend_profile', 'noop')}",
        f'manual_debug_command: "/skill-debug 调试 {skill_name}"',
        "",
    ]
    atomic_write_text(config_path, "\n".join(config_lines))
    if not guide_path.exists():
        atomic_write_text(guide_path, f"# {skill_name} Evaluation Guide\n\n- Review trace quality.\n")
    if not overlay_path.exists():
        atomic_write_text(overlay_path, f"# {skill_name} Review Prompt\n\nReview the trace carefully.\n")
    document = record.skill_path.read_text(encoding="utf-8")
    managed = replace_managed_block(document, marker="skill-debug", body=render_managed_block(skill_name=skill_name))
    atomic_write_text(record.skill_path, managed)
    write_json(
        state_path,
        {
            "schema_version": 1,
            "target_skill": skill_name,
            "skill_path": "SKILL.md",
            "managed_block_marker": "skill-debug",
            "managed_block_version": 1,
            "managed_block_fingerprint": managed_block_fingerprint(skill_name=skill_name),
            "last_attach_result": record.state.value,
        },
    )
    status = "attached" if record.state.value == "attachable" else "repaired"
    if record.state.value == "attached":
        status = "already_aligned"
    return AttachResult(skill_name=skill_name, skill_root=skill_root, status=status)
```

- [ ] **Step 5: Re-run the attach tests**

Run: `python3 -m pytest skill-debug/tests/test_skill_debug_attach.py -q`

Expected: PASS with `3 passed`

- [ ] **Step 6: Commit the target-local attach flow**

```bash
git add skill-debug/src/skill_debug_tools/attach skill-debug/templates/injected-debug-block.md skill-debug/templates/evaluation-guide.md skill-debug/templates/review-prompt.md skill-debug/tests/test_skill_debug_attach.py
git commit -m "feat: add target-local skill-debug attachment"
```

## Task 4: Implement `/skill-debug list` And `/skill-debug 接入`

**Files:**
- Create: `skill-debug/scripts/skill_debug.py`
- Create: `skill-debug/tests/test_skill_debug_list.py`
- Modify: `skill-debug/SKILL.md`
- Test: `skill-debug/tests/test_skill_debug_list.py`

- [ ] **Step 1: Write the failing CLI tests**

```python
import subprocess
from pathlib import Path


def test_skill_debug_list_shows_attachable_and_attached_states(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "code-analyse").mkdir()
    (workspace / "code-analyse" / "SKILL.md").write_text(
        "---\nname: code-analyse\ndescription: analyse\n---\n\n# Code Analyse\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", "scripts/skill_debug.py", "list", "--workspace-root", str(workspace)],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "code-analyse" in result.stdout
    assert "attachable" in result.stdout
```

- [ ] **Step 2: Run the CLI tests to verify they fail**

Run: `python3 -m pytest skill-debug/tests/test_skill_debug_list.py -q`

Expected: FAIL because `scripts/skill_debug.py` does not exist yet

- [ ] **Step 3: Implement the CLI entrypoint**

```python
# skill-debug/scripts/skill_debug.py
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from skill_debug_tools.attach.target import attach_skill
from skill_debug_tools.workspace.discovery import discover_skills


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--workspace-root", type=Path, default=Path.cwd().parent)

    attach_parser = subparsers.add_parser("attach")
    attach_parser.add_argument("skill_name")
    attach_parser.add_argument("--workspace-root", type=Path, default=Path.cwd().parent)

    args = parser.parse_args()
    if args.command == "list":
        for record in discover_skills(args.workspace_root):
            reason = f" ({record.reason})" if record.reason else ""
            print(f"{record.name}\t{record.state.value}\t{record.root}{reason}")
        return 0

    result = attach_skill(workspace_root=args.workspace_root, skill_name=args.skill_name)
    print(f"{result.skill_name}\t{result.status}\t{result.skill_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Update the standalone framework skill contract**

```md
## Supported Commands

- `/skill-debug list` - list attachable, attached, and broken skills in the workspace.
- `/skill-debug 接入 <skill-name>` - attach or repair `skill-debug` integration for a target skill.

## Core Rules

- Keep debug artifacts outside the target skill business output root.
- Store target integration files under the target skill root in `skill-debug/`.
- Store target debug run artifacts under the target skill root in `skill-debug-logs/`.
- Use target-local integration files as the source of truth after attachment.
```

- [ ] **Step 5: Re-run the CLI tests**

Run: `python3 -m pytest skill-debug/tests/test_skill_debug_list.py -q`

Expected: PASS with `1 passed`

- [ ] **Step 6: Commit the framework CLI**

```bash
git add skill-debug/scripts/skill_debug.py skill-debug/SKILL.md skill-debug/tests/test_skill_debug_list.py
git commit -m "feat: add skill-debug list and attach cli"
```

## Task 5: Port Debug Run Lifecycle To Target-Local Logs

**Files:**
- Create: `skill-debug/src/skill_debug_tools/debug_run/__init__.py`
- Create: `skill-debug/src/skill_debug_tools/debug_run/lifecycle.py`
- Create: `skill-debug/tests/test_debug_run_lifecycle.py`
- Test: `skill-debug/tests/test_debug_run_lifecycle.py`

- [ ] **Step 1: Write the failing lifecycle tests**

```python
from pathlib import Path

import pytest

from skill_debug_tools.debug_run.lifecycle import append_debug_event, load_debug_run, start_debug_run


def test_start_debug_run_writes_under_target_local_log_root(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260622-120000-auth-login",
        linked_skill_run_id="ca-20260622-120000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_command",
        review_mode="async",
    )
    assert run.debug_log == skill_root / "skill-debug-logs" / "runs" / "dbg-code-analyse-20260622-120000-auth-login" / "debug-log.md"


def test_append_debug_event_keeps_only_references_to_business_artifacts(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    business_output = skill_root / "code-analyse-docs" / "runs" / "ca-20260622-120000-auth-login.md"
    business_output.parent.mkdir(parents=True, exist_ok=True)
    business_output.write_text("# Run\n", encoding="utf-8")
    run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260622-120000-auth-login",
        linked_skill_run_id="ca-20260622-120000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_command",
        review_mode="async",
    )
    append_debug_event(
        run=run,
        phase="document_update",
        action="Referenced the business run document",
        evidence=["business output exists"],
        artifact_refs=[str(business_output)],
    )
    assert str(business_output) in run.debug_log.read_text(encoding="utf-8")
    assert not (run.run_root / "artifacts" / "ca-20260622-120000-auth-login.md").exists()


def test_load_debug_run_rejects_run_root_outside_target_log_root(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    with pytest.raises(ValueError):
        load_debug_run(skill_root=skill_root, run_root=tmp_path / "outside-run")
```

- [ ] **Step 2: Run the lifecycle tests to verify they fail**

Run: `python3 -m pytest skill-debug/tests/test_debug_run_lifecycle.py -q`

Expected: FAIL with import errors for `skill_debug_tools.debug_run.lifecycle`

- [ ] **Step 3: Implement the target-local lifecycle helpers**

```python
# skill-debug/src/skill_debug_tools/debug_run/lifecycle.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text, write_json


@dataclass(frozen=True)
class DebugRun:
    run_root: Path
    debug_log: Path
    artifact_index: Path
    review_request: Path


def start_debug_run(
    *,
    skill_root: Path,
    skill_name: str,
    debug_run_id: str,
    linked_skill_run_id: str,
    scope_slug: str,
    trigger_source: str,
    review_mode: str,
) -> DebugRun:
    run_root = skill_root / "skill-debug-logs" / "runs" / debug_run_id
    debug_log = run_root / "debug-log.md"
    artifact_index = run_root / "artifacts" / "artifact-index.md"
    review_request = run_root / "review-request.json"
    atomic_write_text(
        debug_log,
        "\n".join(
            [
                "# Debug Log",
                "",
                f"- Skill: `{skill_name}`",
                f"- Debug Run ID: `{debug_run_id}`",
                f"- Linked Skill Run ID: `{linked_skill_run_id}`",
                f"- Scope: `{scope_slug}`",
                f"- Trigger Source: `{trigger_source}`",
                f"- Review Mode: `{review_mode}`",
                "",
                "## Timeline",
                "",
            ]
        ),
    )
    atomic_write_text(artifact_index, "# Artifact Index\n\n")
    write_json(
        review_request,
        {
            "skill_name": skill_name,
            "debug_run_id": debug_run_id,
            "linked_skill_run_id": linked_skill_run_id,
            "review_mode": review_mode,
        },
    )
    return DebugRun(run_root=run_root, debug_log=debug_log, artifact_index=artifact_index, review_request=review_request)
```

- [ ] **Step 4: Add `append_debug_event`, `finalize_debug_run`, and guarded reload**

```python
def append_debug_event(
    *,
    run: DebugRun,
    phase: str,
    action: str,
    evidence: list[str],
    artifact_refs: list[str],
) -> None:
    current = run.debug_log.read_text(encoding="utf-8")
    block = [
        f"### {phase}",
        f"- Action: {action}",
        f"- Evidence: {', '.join(evidence) if evidence else 'none'}",
        f"- Artifact Refs: {', '.join(artifact_refs) if artifact_refs else 'none'}",
        "",
    ]
    atomic_write_text(run.debug_log, current + "\n".join(block))


def finalize_debug_run(*, run: DebugRun, review_mode: str) -> None:
    current = run.debug_log.read_text(encoding="utf-8")
    atomic_write_text(run.debug_log, current + "## Review Trigger\n\n" + f"- Mode: `{review_mode}`\n")


def load_debug_run(*, skill_root: Path, run_root: Path) -> DebugRun:
    allowed_root = (skill_root / "skill-debug-logs" / "runs").resolve()
    resolved_run_root = run_root.resolve()
    if allowed_root != resolved_run_root.parent and allowed_root not in resolved_run_root.parents:
        raise ValueError(f"Debug run root `{resolved_run_root}` must stay under `{allowed_root}`.")
    return DebugRun(
        run_root=resolved_run_root,
        debug_log=resolved_run_root / "debug-log.md",
        artifact_index=resolved_run_root / "artifacts" / "artifact-index.md",
        review_request=resolved_run_root / "review-request.json",
    )
```

- [ ] **Step 5: Re-run the lifecycle tests**

Run: `python3 -m pytest skill-debug/tests/test_debug_run_lifecycle.py -q`

Expected: PASS with `3 passed`

- [ ] **Step 6: Commit target-local debug lifecycle support**

```bash
git add skill-debug/src/skill_debug_tools/debug_run skill-debug/tests/test_debug_run_lifecycle.py
git commit -m "feat: add target-local skill-debug run lifecycle"
```

## Task 6: Port Review Input Assembly, Queueing, And Runners

**Files:**
- Create: `skill-debug/src/skill_debug_tools/review/__init__.py`
- Create: `skill-debug/src/skill_debug_tools/review/run.py`
- Create: `skill-debug/src/skill_debug_tools/review/queue.py`
- Create: `skill-debug/templates/review.md`
- Create: `skill-debug/review_runners/noop.py`
- Create: `skill-debug/review_runners/openai_api.py`
- Create: `skill-debug/review_runners/codex_thread.py`
- Create: `skill-debug/runtime/config/backends.example.yaml`
- Create: `skill-debug/tests/test_review_run.py`
- Create: `skill-debug/tests/test_review_queue.py`
- Create: `skill-debug/tests/test_review_runners.py`
- Test: `skill-debug/tests/test_review_run.py`
- Test: `skill-debug/tests/test_review_queue.py`
- Test: `skill-debug/tests/test_review_runners.py`

- [ ] **Step 1: Move the existing runner tests into the standalone module and let them fail there**

```python
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest


RUNNER_PATH = Path(__file__).resolve().parents[1] / "review_runners" / "openai_api.py"


def test_openai_http_runner_requires_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_openai_runner()
    monkeypatch.delenv("MISSING_TEST_KEY", raising=False)

    with pytest.raises(ValueError, match="MISSING_TEST_KEY"):
        runner.run(
            prompt="Please review this trace.",
            profile={
                "transport": "http",
                "provider": "gpt",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-5.5",
                "api_key_env": "MISSING_TEST_KEY",
            },
        )


def _load_openai_runner() -> Any:
    spec = importlib.util.spec_from_file_location("test_openai_api_runner", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

- [ ] **Step 2: Run the standalone review tests to verify they fail**

Run: `python3 -m pytest skill-debug/tests/test_review_runners.py skill-debug/tests/test_review_run.py skill-debug/tests/test_review_queue.py -q`

Expected: FAIL with missing modules and runner files

- [ ] **Step 3: Port the existing review runners into the standalone module**

```python
# skill-debug/review_runners/noop.py
from __future__ import annotations


def run(*, prompt: str, profile: dict[str, str]) -> str:
    return "# Review\n\n- Runner: `noop`\n- Result: review skipped for offline or test execution\n"
```

```python
# skill-debug/review_runners/codex_thread.py
from __future__ import annotations

import hashlib


def run(*, prompt: str, profile: dict[str, str]) -> str:
    transport = profile.get("transport", "mock")
    if transport != "mock":
        raise NotImplementedError("Codex-thread review runner only supports `transport: mock` right now.")
    prompt_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    return "\n".join(
        [
            "# Review",
            "",
            "## Backend",
            "",
            "- Runner: `codex_thread`",
            f"- Thread URL: `{profile.get('thread_url', 'mock://codex-thread')}`",
            f"- Prompt Digest: `{prompt_digest}`",
            "",
            "## Findings",
            "",
            "- This is a placeholder mock for thread-based review execution.",
            "- Use it for integration wiring checks before a real Codex thread backend is configured.",
        ]
    )
```

- [ ] **Step 4: Port review assembly and queue logic with target-local config loading**

```python
# skill-debug/src/skill_debug_tools/review/queue.py
from __future__ import annotations

import json
from pathlib import Path

from skill_debug_tools.common.files import atomic_write_text
from skill_debug_tools.review.run import run_review_for_request


def enqueue_review_job(*, runtime_root: Path, request_path: Path, debug_run_id: str) -> Path:
    pending_dir = runtime_root / "review-queue" / "pending"
    job_path = pending_dir / f"{debug_run_id}.json"
    atomic_write_text(
        job_path,
        "{\n"
        f'  "debug_run_id": "{debug_run_id}",\n'
        f'  "request_path": "{request_path}"\n'
        "}\n",
    )
    return job_path
```

```python
# skill-debug/src/skill_debug_tools/review/run.py
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
```

- [ ] **Step 5: Bring over the tested behavior from the current embedded implementation**

```python
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
```

```python
def run_review_for_request(
    *,
    framework_root: Path,
    skill_root: Path,
    request_path: Path,
    config_path: Path | None = None,
) -> ReviewResult:
    request_payload = json.loads(request_path.read_text(encoding="utf-8"))
    run_root = request_path.parent
    review_path = run_root / "review.md"
    review_status_path = run_root / "review-status.json"
    review_input_path = run_root / "artifacts" / "review-input.md"
    target_root = skill_root / "skill-debug"
    target_config = read_yaml(target_root / "config.yaml")
    resolved_config_path = config_path or framework_root / "runtime" / "config" / "backends.example.yaml"
    backend_name = select_backend_name(
        run_override=request_payload.get("backend_profile"),
        target_default=target_config.get("default_backend_profile"),
        global_default=read_yaml(resolved_config_path).get("default_profile"),
    )
    profile = load_backend_profile(resolved_config_path, backend_name)
    if not profile:
        raise ValueError(f"Backend profile `{backend_name}` was not found in `{resolved_config_path}`.")
    runner_name = str(profile.get("runner", "noop"))
    review_input = _build_review_input(skill_root=skill_root, framework_root=framework_root, run_root=run_root, request_payload=request_payload)
    atomic_write_text(review_input_path, review_input)
    runner = _load_runner(framework_root=framework_root, runner_name=runner_name)
    review_body = runner(prompt=review_input, profile=profile)
    atomic_write_text(review_path, review_body if review_body.startswith("#") else f"# Review\n\n{review_body}\n")
    write_json(
        review_status_path,
        {
            "status": "completed",
            "backend_profile": backend_name,
            "runner": runner_name,
            "provider": profile.get("provider", "unknown"),
            "request_path": str(request_path),
        },
    )
    return ReviewResult(
        review_path=review_path,
        review_status_path=review_status_path,
        review_input_path=review_input_path,
        backend_profile=backend_name,
        runner=runner_name,
    )
```

- [ ] **Step 6: Re-run the standalone review tests**

Run: `python3 -m pytest skill-debug/tests/test_review_runners.py skill-debug/tests/test_review_run.py skill-debug/tests/test_review_queue.py -q`

Expected: PASS with all standalone review tests green

- [ ] **Step 7: Commit the review and queue port**

```bash
git add skill-debug/src/skill_debug_tools/review skill-debug/templates/review.md skill-debug/review_runners skill-debug/runtime/config/backends.example.yaml skill-debug/tests/test_review_run.py skill-debug/tests/test_review_queue.py skill-debug/tests/test_review_runners.py
git commit -m "feat: port standalone skill-debug review infrastructure"
```

## Task 7: Reattach `code-analyse` As The First Target-Local Consumer

**Files:**
- Modify: `code-analyse/SKILL.md`
- Modify: `code-analyse/tests/test_code_analyse_skill_contract.py`
- Modify: `code-analyse/tests/conftest.py`
- Modify: `code-analyse/tests/test_code_analyse_skill_debug_integration.py`
- Create: `code-analyse/skill-debug/config.yaml`
- Create: `code-analyse/skill-debug/evaluation-guide.md`
- Create: `code-analyse/skill-debug/review-prompt.md`
- Create: `code-analyse/skill-debug/injection-state.json`
- Test: `code-analyse/tests/test_code_analyse_skill_contract.py`
- Test: `code-analyse/tests/test_code_analyse_skill_debug_integration.py`

- [ ] **Step 1: Update the `code-analyse` contract test to the new target-local wording**

```python
from pathlib import Path


def test_code_analyse_skill_references_run_tracking_commands() -> None:
    document = Path("SKILL.md").read_text(encoding="utf-8")
    assert "current-run.md" in document
    assert "future-work.md" in document
    assert "python3 scripts/code_analyse_run_tracking.py start" in document
    assert "Do not place debug logs in `code-analyse-docs/`" in document
    assert "Debug config: `skill-debug/config.yaml`" in document
    assert "Debug log root: `skill-debug-logs`" in document
    assert "Manual debug command: `/skill-debug 调试 code-analyse`" in document
```

- [ ] **Step 2: Run the contract and integration tests to verify they fail**

Run: `python3 -m pytest code-analyse/tests/test_code_analyse_skill_contract.py code-analyse/tests/test_code_analyse_skill_debug_integration.py -q`

Expected: FAIL because `code-analyse` still references the old central target config and old embedded imports

- [ ] **Step 3: Rewrite the `code-analyse` managed block and generate the target-local assets**

```md
        <!-- skill-debug:managed:start -->
        ## Debug Capability

This skill supports `skill-debug`.

- Debug support: enabled
- Debug config: `skill-debug/config.yaml`
- Debug log root: `skill-debug-logs`
- Manual debug command: `/skill-debug 调试 code-analyse`
        <!-- skill-debug:managed:end -->
```

```yaml
# code-analyse/skill-debug/config.yaml
schema_version: 1
target_skill: code-analyse
skill_path: SKILL.md
skill_output_root: code-analyse-docs
debug_output_root: skill-debug-logs
auto_debug_allowed: true
default_review_mode: async
default_backend_profile: noop
manual_debug_command: "/skill-debug 调试 code-analyse"
```

- [ ] **Step 4: Rewrite the integration test to use the standalone framework package**

```python
from pathlib import Path
import sys

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2] / "skill-debug" / "src"
if str(FRAMEWORK_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_ROOT))

from skill_debug_tools.attach.target import attach_skill
from skill_debug_tools.debug_run.lifecycle import append_debug_event, start_debug_run
from skill_tools.code_analyse.run_tracking import start_run


def test_code_analyse_target_local_attachment_and_debug_run_stay_separate(tmp_path: Path) -> None:
    skill_root = tmp_path / "code-analyse"
    skill_root.mkdir()
    (skill_root / "SKILL.md").write_text(Path("SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
    attach_skill(workspace_root=tmp_path, skill_name="code-analyse")
    start_run(
        output_root=skill_root / "code-analyse-docs",
        run_id="ca-20260622-120000-auth-login",
        scope_slug="auth-login",
        objective="Trace the auth login workflow",
        status="in_progress",
        module_scoped=True,
    )
    debug_run = start_debug_run(
        skill_root=skill_root,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260622-120000-auth-login",
        linked_skill_run_id="ca-20260622-120000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_command",
        review_mode="async",
    )
    append_debug_event(
        run=debug_run,
        phase="document_update",
        action="Referenced the business run document",
        evidence=["business output exists"],
        artifact_refs=[str(skill_root / "code-analyse-docs" / "runs" / "ca-20260622-120000-auth-login.md")],
    )
    assert (skill_root / "skill-debug" / "config.yaml").exists()
    assert (skill_root / "skill-debug-logs" / "runs").exists()
    assert not (skill_root / "code-analyse-docs" / "debug-log.md").exists()
```

- [ ] **Step 5: Re-run the `code-analyse` contract and integration tests**

Run: `python3 -m pytest code-analyse/tests/test_code_analyse_skill_contract.py code-analyse/tests/test_code_analyse_skill_debug_integration.py -q`

Expected: PASS with the updated target-local assertions

- [ ] **Step 6: Commit the `code-analyse` target-local integration**

```bash
git add code-analyse/SKILL.md code-analyse/skill-debug code-analyse/tests/test_code_analyse_skill_contract.py code-analyse/tests/test_code_analyse_skill_debug_integration.py code-analyse/tests/conftest.py
git commit -m "feat: reattach code-analyse to standalone skill-debug"
```

## Task 8: Remove The Embedded Framework Copy And Verify Both Modules

**Files:**
- Delete: `code-analyse/src/skill_tools/skill_debug/*`
- Delete: `code-analyse/skill-debug/SKILL.md`
- Delete: `code-analyse/skill-debug/scripts/*`
- Delete: `code-analyse/skill-debug/review_runners/*`
- Delete: `code-analyse/skill-debug/runtime/config/backends.example.yaml`
- Delete: `code-analyse/skill-debug/targets/code-analyse/*`
- Delete: `code-analyse/tests/test_skill_debug_init_target.py`
- Delete: `code-analyse/tests/test_skill_debug_run_lifecycle.py`
- Delete: `code-analyse/tests/test_skill_debug_review_queue.py`
- Delete: `code-analyse/tests/test_skill_debug_review_run.py`
- Delete: `code-analyse/tests/test_skill_debug_review_runners.py`
- Test: `skill-debug/tests`
- Test: `code-analyse/tests`

- [ ] **Step 1: Delete the embedded generic framework files from `code-analyse`**

```bash
rm code-analyse/src/skill_tools/skill_debug/__init__.py
rm code-analyse/src/skill_tools/skill_debug/target_init.py
rm code-analyse/src/skill_tools/skill_debug/debug_run.py
rm code-analyse/src/skill_tools/skill_debug/review_run.py
rm code-analyse/src/skill_tools/skill_debug/review_queue.py
rm code-analyse/skill-debug/SKILL.md
rm code-analyse/skill-debug/scripts/init_target.py
rm code-analyse/skill-debug/scripts/start_run.py
rm code-analyse/skill-debug/scripts/append_event.py
rm code-analyse/skill-debug/scripts/finalize_run.py
rm code-analyse/skill-debug/scripts/enqueue_review.py
rm code-analyse/skill-debug/scripts/review_worker.py
rm code-analyse/skill-debug/scripts/review_run.py
rm code-analyse/skill-debug/review_runners/base.py
rm code-analyse/skill-debug/review_runners/noop.py
rm code-analyse/skill-debug/review_runners/openai_api.py
rm code-analyse/skill-debug/review_runners/codex_thread.py
rm code-analyse/skill-debug/runtime/config/backends.example.yaml
rm code-analyse/skill-debug/targets/code-analyse/config.yaml
rm code-analyse/skill-debug/targets/code-analyse/evaluation-guide.md
rm code-analyse/skill-debug/targets/code-analyse/review-prompt.md
rm code-analyse/skill-debug/targets/code-analyse/injection-state.json
rm code-analyse/tests/test_skill_debug_init_target.py
rm code-analyse/tests/test_skill_debug_run_lifecycle.py
rm code-analyse/tests/test_skill_debug_review_queue.py
rm code-analyse/tests/test_skill_debug_review_run.py
rm code-analyse/tests/test_skill_debug_review_runners.py
```

- [ ] **Step 2: Run the standalone framework test suite**

Run: `python3 -m pytest skill-debug/tests -q`

Expected: PASS with all standalone framework tests green

- [ ] **Step 3: Run the remaining `code-analyse` test suite**

Run: `python3 -m pytest code-analyse/tests/test_code_analyse_run_tracking.py code-analyse/tests/test_code_analyse_skill_contract.py code-analyse/tests/test_code_analyse_skill_debug_integration.py -q`

Expected: PASS with only `code-analyse` business and integration tests green

- [ ] **Step 4: Inspect the workspace to verify the final ownership split**

Run: `find skill-debug code-analyse -maxdepth 3 -type f | sort`

Expected: framework files live under `skill-debug/`, target-local integration files live under `code-analyse/skill-debug/`, and embedded generic framework files are gone from `code-analyse`

- [ ] **Step 5: Commit the final extraction cleanup**

```bash
git add skill-debug code-analyse
git commit -m "refactor: extract standalone skill-debug module"
```

## Self-Review Checklist

- Spec coverage:
  - independent sibling module: Tasks 1, 6, and 8
  - target-local integration files: Tasks 3 and 7
  - `/skill-debug list`: Tasks 2 and 4
  - `/skill-debug 接入 <skill-name>`: Tasks 2, 3, and 4
  - target-local debug logs: Tasks 5 and 7
  - removal of embedded framework ownership from `code-analyse`: Task 8
- Placeholder scan:
  - no `TODO`, `TBD`, or “similar to above” placeholders remain
- Type consistency:
  - standalone package name remains `skill_debug_tools`
  - target-local integration root remains `<skill-root>/skill-debug/`
  - target-local debug log root remains `<skill-root>/skill-debug-logs/`

Plan complete and saved to `docs/superpowers/plans/2026-06-22-skill-debug-independent-module.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
