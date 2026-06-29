# Skill Debug And Code Analyse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build stable run-tracking for `/code-analyse` and a reusable `skill-debug` trace/debug framework with isolated debug artifacts, target injection, and configurable review backends.

**Architecture:** Keep `code-analyse` business outputs under `code-analyse-docs/` and move all debug logs, review artifacts, and runtime queue state into `skill-debug-logs/` and `skill-debug/runtime/`. Implement reusable Python helpers under `src/skill_tools/`, expose skill-facing CLIs under `scripts/` and `skill-debug/scripts/`, and materialize the first target attachment by generating `skill-debug/targets/code-analyse/` plus a managed debug block in the root `SKILL.md`.

**Tech Stack:** Python 3.11, PyYAML, pytest, Markdown templates, YAML config, argparse-based CLIs

---

## Planned File Structure

### Modify

- `SKILL.md` - extend the `code-analyse` contract so every `/code-analyse` invocation writes run-tracking artifacts, references the new run-tracking CLI, and later receives a managed `skill-debug` capability block.
- `.gitignore` - ignore local backend credentials, runtime queues, caches, and generated debug logs while keeping committed target configs and templates tracked.

### Create

- `pyproject.toml` - define the Python package, runtime dependency on `PyYAML`, and pytest configuration.
- `templates/current-run.md` - root skill template for stable latest-run documents.
- `templates/future-work.md` - root skill template for persistent backlog documents.
- `templates/run.md` - root skill template for append-only historical run documents.
- `scripts/code_analyse_run_tracking.py` - CLI entrypoint for `start`, `append-event`, `sync-future-work`, and `finalize`.
- `src/skill_tools/__init__.py` - package marker.
- `src/skill_tools/common/__init__.py` - common helper package marker.
- `src/skill_tools/common/files.py` - reusable path creation, atomic writes, and JSON/YAML helpers.
- `src/skill_tools/common/markdown.py` - Markdown section rendering helpers and managed-block replacement helpers.
- `src/skill_tools/code_analyse/__init__.py` - package marker.
- `src/skill_tools/code_analyse/run_tracking.py` - core business run-tracking and future-work logic.
- `skill-debug/SKILL.md` - generic skill trace/debug skill instructions.
- `skill-debug/templates/injected-debug-block.md` - declarative injected block template.
- `skill-debug/templates/debug-log.md` - readable main debug log template.
- `skill-debug/templates/review.md` - review output template.
- `skill-debug/templates/review-prompt.md` - global prompt base for review requests.
- `skill-debug/templates/evaluation-guide.md` - generic guide base used when generating target guides.
- `skill-debug/scripts/init_target.py` - attach a target skill, generate target assets, and maintain the injected debug block.
- `skill-debug/scripts/start_run.py` - create debug run directories and initialize `debug-log.md`.
- `skill-debug/scripts/append_event.py` - append debug step events and artifact references.
- `skill-debug/scripts/finalize_run.py` - close debug runs and emit review requests.
- `skill-debug/scripts/enqueue_review.py` - create asynchronous review jobs.
- `skill-debug/scripts/review_worker.py` - process queued review jobs.
- `skill-debug/scripts/review_run.py` - run one review synchronously from a request or queue job.
- `skill-debug/review_runners/base.py` - shared review-runner protocol.
- `skill-debug/review_runners/noop.py` - deterministic no-op backend for local tests and fallback.
- `skill-debug/review_runners/openai_api.py` - HTTP backend for future user-provided URL/token/model settings.
- `skill-debug/review_runners/codex_thread.py` - stub or adapter for thread-based review execution.
- `skill-debug/runtime/config/backends.example.yaml` - example backend profiles.
- `src/skill_tools/skill_debug/__init__.py` - package marker.
- `src/skill_tools/skill_debug/target_init.py` - target attachment orchestration and managed-block generation.
- `src/skill_tools/skill_debug/debug_run.py` - debug run lifecycle and artifact separation logic.
- `src/skill_tools/skill_debug/review_queue.py` - queue file creation and job state transitions.
- `src/skill_tools/skill_debug/review_run.py` - prompt assembly, backend selection, and review output writing.
- `tests/conftest.py` - shared temp-repo and fixture helpers.
- `tests/test_code_analyse_run_tracking.py` - unit tests for business run-tracking and future-work behavior.
- `tests/test_code_analyse_skill_contract.py` - contract tests that assert `SKILL.md` references the run-tracking workflow.
- `tests/test_skill_debug_init_target.py` - target attachment and managed-block tests.
- `tests/test_skill_debug_run_lifecycle.py` - debug log and artifact-separation tests.
- `tests/test_skill_debug_review_queue.py` - queue creation and state transition tests.
- `tests/test_skill_debug_review_run.py` - backend selection, prompt composition, and review output tests.
- `tests/test_code_analyse_skill_debug_integration.py` - end-to-end integration tests for `code-analyse` plus `skill-debug`.

### Generated During Integration

- `skill-debug/targets/code-analyse/config.yaml` - target-specific debug policy and paths.
- `skill-debug/targets/code-analyse/evaluation-guide.md` - generated once for `code-analyse`.
- `skill-debug/targets/code-analyse/review-prompt.md` - generated once as the target-specific prompt overlay.
- `skill-debug/targets/code-analyse/injection-state.json` - managed-block version and fingerprint metadata.

### Not Committed

- `skill-debug/runtime/config/backends.local.yaml` - local credentials and per-user backend connection details.
- `skill-debug/runtime/review-queue/` - queue state for asynchronous review jobs.
- `skill-debug-logs/` - generated debug logs and raw artifacts.

## Task 1: Bootstrap Python Tooling And Shared Helpers

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/skill_tools/__init__.py`
- Create: `src/skill_tools/common/__init__.py`
- Create: `src/skill_tools/common/files.py`
- Create: `src/skill_tools/common/markdown.py`
- Create: `tests/conftest.py`
- Create: `tests/test_common_helpers.py`
- Test: `tests/test_common_helpers.py`

- [ ] **Step 1: Write the failing helper tests**

```python
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
```

- [ ] **Step 2: Run the helper tests to verify they fail**

Run: `python3 -m pytest tests/test_common_helpers.py -q`

Expected: FAIL with import errors for `skill_tools.common.files` and `skill_tools.common.markdown`

- [ ] **Step 3: Add project metadata and ignore rules**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "skill-runtime-tools"
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
skill-debug-logs/
skill-debug/runtime/review-queue/
skill-debug/runtime/config/backends.local.yaml
```

- [ ] **Step 4: Implement the shared helper modules**

```python
# src/skill_tools/common/files.py
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
# src/skill_tools/common/markdown.py
from __future__ import annotations

from textwrap import dedent


def render_bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


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

Run: `python3 -m pytest tests/test_common_helpers.py -q`

Expected: PASS with `3 passed`

- [ ] **Step 6: Commit the bootstrap changes**

```bash
git add pyproject.toml .gitignore src/skill_tools tests/test_common_helpers.py tests/conftest.py
git commit -m "chore: bootstrap skill runtime tooling"
```

## Task 2: Implement `code-analyse` Run Tracking And Future Work

**Files:**
- Create: `templates/current-run.md`
- Create: `templates/future-work.md`
- Create: `templates/run.md`
- Create: `src/skill_tools/code_analyse/__init__.py`
- Create: `src/skill_tools/code_analyse/run_tracking.py`
- Create: `scripts/code_analyse_run_tracking.py`
- Create: `tests/test_code_analyse_run_tracking.py`
- Test: `tests/test_code_analyse_run_tracking.py`

- [ ] **Step 1: Write the failing run-tracking tests**

```python
from pathlib import Path

from skill_tools.code_analyse.run_tracking import (
    append_run_event,
    finalize_run,
    start_run,
    sync_future_work,
)


def test_start_run_creates_global_and_scope_documents(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "code-analyse-docs",
        run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        objective="Trace the auth login workflow",
        status="needs_clarification",
        module_scoped=True,
    )
    assert run.global_current.exists()
    assert run.global_run.exists()
    assert run.scope_current and run.scope_current.exists()
    assert run.scope_run and run.scope_run.exists()


def test_append_event_updates_current_run_and_history(tmp_path: Path) -> None:
    run = start_run(
        output_root=tmp_path / "code-analyse-docs",
        run_id="ca-20260618-153000-repo",
        scope_slug="repo",
        objective="Map repository-wide architecture",
        status="in_progress",
        module_scoped=False,
    )
    append_run_event(
        output_root=tmp_path / "code-analyse-docs",
        run_id=run.run_id,
        phase="scope_resolution",
        action="Marked repository-wide scope",
        evidence=["user omitted module"],
        outputs=[],
        next_step="Inspect entrypoints",
    )
    history = run.global_run.read_text()
    current = run.global_current.read_text()
    assert "scope_resolution" in history
    assert "Inspect entrypoints" in current


def test_sync_future_work_keeps_status_per_topic(tmp_path: Path) -> None:
    sync_future_work(
        output_root=tmp_path / "code-analyse-docs",
        scope_slug="auth-login",
        topics=[
            {"topic": "request-flow", "priority": "high", "status": "open"},
            {"topic": "session-state", "priority": "medium", "status": "deferred"},
        ],
    )
    future_work = (tmp_path / "code-analyse-docs" / "scopes" / "auth-login" / "future-work.md").read_text()
    assert "request-flow" in future_work
    assert "session-state" in future_work
    assert "deferred" in future_work
```

- [ ] **Step 2: Run the run-tracking tests to verify they fail**

Run: `python3 -m pytest tests/test_code_analyse_run_tracking.py -q`

Expected: FAIL with import errors for `skill_tools.code_analyse.run_tracking`

- [ ] **Step 3: Implement the templates and core run-tracking module**

```python
# src/skill_tools/code_analyse/run_tracking.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skill_tools.common.files import atomic_write_text


@dataclass(frozen=True)
class RunPaths:
    run_id: str
    global_current: Path
    global_run: Path
    scope_current: Path | None
    scope_run: Path | None


def start_run(
    *,
    output_root: Path,
    run_id: str,
    scope_slug: str,
    objective: str,
    status: str,
    module_scoped: bool,
) -> RunPaths:
    global_current = output_root / "current-run.md"
    global_run = output_root / "runs" / f"{run_id}.md"
    scope_current = output_root / "scopes" / scope_slug / "current-run.md" if module_scoped else None
    scope_run = output_root / "scopes" / scope_slug / "runs" / f"{run_id}.md" if module_scoped else None
    current_body = f"# Current Run\n\n- Run ID: `{run_id}`\n- Scope: `{scope_slug}`\n- Status: `{status}`\n- Objective: {objective}\n"
    history_body = f"# Run {run_id}\n\n- Scope: `{scope_slug}`\n- Status: `{status}`\n- Objective: {objective}\n\n## Timeline\n"
    atomic_write_text(global_current, current_body)
    atomic_write_text(global_run, history_body)
    if scope_current:
        atomic_write_text(scope_current, current_body)
    if scope_run:
        atomic_write_text(scope_run, history_body)
    return RunPaths(run_id, global_current, global_run, scope_current, scope_run)


def append_run_event(
    *,
    output_root: Path,
    run_id: str,
    phase: str,
    action: str,
    evidence: list[str],
    outputs: list[str],
    next_step: str,
) -> None:
    run_doc = next(output_root.glob(f"runs/{run_id}.md"))
    existing = run_doc.read_text(encoding="utf-8")
    event_block = (
        f"\n### {phase}\n"
        f"- Action: {action}\n"
        f"- Evidence: {', '.join(evidence) or 'none'}\n"
        f"- Outputs: {', '.join(outputs) or 'none'}\n"
        f"- Next Step: {next_step}\n"
    )
    atomic_write_text(run_doc, existing + event_block)
```

```python
# scripts/code_analyse_run_tracking.py
from __future__ import annotations

import argparse
from pathlib import Path

from skill_tools.code_analyse.run_tracking import append_run_event, finalize_run, start_run, sync_future_work


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    start = subparsers.add_parser("start")
    start.add_argument("--output-root", type=Path, required=True)
    start.add_argument("--run-id", required=True)
    start.add_argument("--scope-slug", required=True)
    start.add_argument("--objective", required=True)
    start.add_argument("--status", required=True)
    start.add_argument("--module-scoped", action="store_true")
    args = parser.parse_args()
    if args.command == "start":
        start_run(
            output_root=args.output_root,
            run_id=args.run_id,
            scope_slug=args.scope_slug,
            objective=args.objective,
            status=args.status,
            module_scoped=args.module_scoped,
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Complete `sync_future_work` and `finalize_run` behavior**

```python
def sync_future_work(*, output_root: Path, scope_slug: str, topics: list[dict[str, str]]) -> None:
    lines = ["# Future Work", ""]
    for topic in topics:
        lines.extend(
            [
                f"## {topic['topic']}",
                f"- Priority: `{topic['priority']}`",
                f"- Status: `{topic['status']}`",
                "",
            ]
        )
    scope_future = output_root / "scopes" / scope_slug / "future-work.md"
    atomic_write_text(scope_future, "\n".join(lines).rstrip() + "\n")


def finalize_run(*, output_root: Path, run_id: str, status: str, next_topics: list[str]) -> None:
    run_doc = next(output_root.glob(f"runs/{run_id}.md"))
    existing = run_doc.read_text(encoding="utf-8")
    tail = "\n## Completion\n" + f"- Status: `{status}`\n" + f"- Next Topics: {', '.join(next_topics) or 'none'}\n"
    atomic_write_text(run_doc, existing + tail)
```

- [ ] **Step 5: Re-run the run-tracking tests**

Run: `python3 -m pytest tests/test_code_analyse_run_tracking.py -q`

Expected: PASS with `3 passed`

- [ ] **Step 6: Commit the run-tracking implementation**

```bash
git add templates scripts/code_analyse_run_tracking.py src/skill_tools/code_analyse tests/test_code_analyse_run_tracking.py
git commit -m "feat: add code-analyse run tracking"
```

## Task 3: Update The Root `SKILL.md` To Use Run Tracking

**Files:**
- Modify: `SKILL.md`
- Create: `tests/test_code_analyse_skill_contract.py`
- Test: `tests/test_code_analyse_skill_contract.py`

- [ ] **Step 1: Write the failing skill-contract test**

```python
from pathlib import Path


def test_code_analyse_skill_references_run_tracking_commands() -> None:
    document = Path("SKILL.md").read_text(encoding="utf-8")
    assert "current-run.md" in document
    assert "future-work.md" in document
    assert "python3 scripts/code_analyse_run_tracking.py start" in document
    assert "Do not place debug logs in `code-analyse-docs/`" in document
```

- [ ] **Step 2: Run the contract test to verify it fails**

Run: `python3 -m pytest tests/test_code_analyse_skill_contract.py -q`

Expected: FAIL because the root `SKILL.md` does not yet reference the run-tracking CLI and output contract

- [ ] **Step 3: Modify `SKILL.md` with an explicit run-tracking workflow**

```md
## Execution Artifact Rules

- Every `/code-analyse` invocation must create or update run-tracking documents under `code-analyse-docs/`.
- Before asking a clarification question, start or refresh the current run record.
- Use `python3 scripts/code_analyse_run_tracking.py start ...` when a run begins.
- Use `python3 scripts/code_analyse_run_tracking.py append-event ...` after each major phase.
- Use `python3 scripts/code_analyse_run_tracking.py sync-future-work ...` before finishing.
- Use `python3 scripts/code_analyse_run_tracking.py finalize ...` when the run concludes.
- Do not place debug logs in `code-analyse-docs/`.
```

- [ ] **Step 4: Re-run the contract and run-tracking tests**

Run: `python3 -m pytest tests/test_code_analyse_skill_contract.py tests/test_code_analyse_run_tracking.py -q`

Expected: PASS with `4 passed`

- [ ] **Step 5: Commit the `SKILL.md` contract update**

```bash
git add SKILL.md tests/test_code_analyse_skill_contract.py
git commit -m "docs: add code-analyse run tracking contract"
```

## Task 4: Scaffold `skill-debug` Target Attachment

**Files:**
- Create: `skill-debug/SKILL.md`
- Create: `skill-debug/templates/injected-debug-block.md`
- Create: `skill-debug/templates/debug-log.md`
- Create: `skill-debug/templates/review.md`
- Create: `skill-debug/templates/review-prompt.md`
- Create: `skill-debug/templates/evaluation-guide.md`
- Create: `src/skill_tools/skill_debug/__init__.py`
- Create: `src/skill_tools/skill_debug/target_init.py`
- Create: `skill-debug/scripts/init_target.py`
- Create: `tests/test_skill_debug_init_target.py`
- Test: `tests/test_skill_debug_init_target.py`

- [ ] **Step 1: Write the failing target-attachment tests**

```python
from pathlib import Path

from skill_tools.skill_debug.target_init import attach_target


def test_attach_target_generates_target_assets(tmp_path: Path) -> None:
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("---\nname: code-analyse\ndescription: test\n---\n\n# Code Analyse\n", encoding="utf-8")
    result = attach_target(
        repo_root=tmp_path,
        skill_name="code-analyse",
        skill_path=skill_path,
        manual_entrypoints=["/code-analyse-debug_mode"],
        skill_output_root="code-analyse-docs",
        debug_output_root="skill-debug-logs/code-analyse",
    )
    assert (tmp_path / "skill-debug" / "targets" / "code-analyse" / "config.yaml").exists()
    assert result.injected_block_path == skill_path


def test_attach_target_inserts_managed_debug_block(tmp_path: Path) -> None:
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("---\nname: code-analyse\ndescription: test\n---\n\n# Code Analyse\n", encoding="utf-8")
    attach_target(
        repo_root=tmp_path,
        skill_name="code-analyse",
        skill_path=skill_path,
        manual_entrypoints=["/code-analyse-debug_mode"],
        skill_output_root="code-analyse-docs",
        debug_output_root="skill-debug-logs/code-analyse",
    )
    document = skill_path.read_text(encoding="utf-8")
    assert "<!-- skill-debug:managed:start -->" in document
    assert "/code-analyse-debug_mode" in document
```

- [ ] **Step 2: Run the target-attachment tests to verify they fail**

Run: `python3 -m pytest tests/test_skill_debug_init_target.py -q`

Expected: FAIL with import errors for `skill_tools.skill_debug.target_init`

- [ ] **Step 3: Implement the target attachment module and CLI**

```python
# src/skill_tools/skill_debug/target_init.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skill_tools.common.files import atomic_write_text, write_json
from skill_tools.common.markdown import replace_managed_block


@dataclass(frozen=True)
class AttachmentResult:
    injected_block_path: Path
    target_root: Path


def attach_target(
    *,
    repo_root: Path,
    skill_name: str,
    skill_path: Path,
    manual_entrypoints: list[str],
    skill_output_root: str,
    debug_output_root: str,
) -> AttachmentResult:
    target_root = repo_root / "skill-debug" / "targets" / skill_name
    body = "\n".join(
        [
            "## Debug Capability",
            "",
            "This skill supports `skill-debug`.",
            "",
            "- Debug support: enabled",
            "- Manual debug entrypoints:",
            *[f"  - `{entry}`" for entry in manual_entrypoints],
            "- Automatic debug trigger: allowed",
            "- Default debug review mode: async",
            f"- Debug log root: `{debug_output_root}`",
            f"- Skill output root: `{skill_output_root}`",
            f"- Debug target config: `skill-debug/targets/{skill_name}/config.yaml`",
        ]
    )
    updated = replace_managed_block(skill_path.read_text(encoding="utf-8"), marker="skill-debug", body=body)
    atomic_write_text(skill_path, updated)
    atomic_write_text(target_root / "config.yaml", f"target_skill: {skill_name}\n")
    atomic_write_text(target_root / "evaluation-guide.md", f"# {skill_name} Evaluation Guide\n")
    atomic_write_text(target_root / "review-prompt.md", f"# {skill_name} Review Prompt Overlay\n")
    write_json(target_root / "injection-state.json", {"skill_name": skill_name, "manual_entrypoints": manual_entrypoints})
    return AttachmentResult(injected_block_path=skill_path, target_root=target_root)
```

```python
# skill-debug/scripts/init_target.py
from __future__ import annotations

import argparse
from pathlib import Path

from skill_tools.skill_debug.target_init import attach_target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--skill-path", type=Path, required=True)
    parser.add_argument("--manual-entrypoint", action="append", dest="manual_entrypoints", default=[])
    parser.add_argument("--skill-output-root", required=True)
    parser.add_argument("--debug-output-root", required=True)
    args = parser.parse_args()
    attach_target(
        repo_root=args.repo_root,
        skill_name=args.skill_name,
        skill_path=args.skill_path,
        manual_entrypoints=args.manual_entrypoints,
        skill_output_root=args.skill_output_root,
        debug_output_root=args.debug_output_root,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Add the generic `skill-debug` skill and templates**

```md
# skill-debug/SKILL.md

Use this skill to attach structured trace/debug support to a target skill, generate target-specific debug assets, and review debug runs without mixing debug outputs into business output roots.

## Core Rules

- Keep debug artifacts outside the target skill output root.
- Generate one target config directory per attached skill.
- Use managed debug blocks when modifying a target `SKILL.md`.
- Default review mode is asynchronous unless the target overrides it.
```

```md
<!-- skill-debug/templates/injected-debug-block.md -->
## Debug Capability

This skill supports `skill-debug`.

- Debug support: enabled
- Manual debug entrypoints:
{{manual_entrypoints}}
- Automatic debug trigger: allowed
- Default debug review mode: async
- Debug log root: `{{debug_output_root}}`
- Skill output root: `{{skill_output_root}}`
- Debug hooks:
  - run_start
  - step_event
  - artifact_ref
  - run_finalize
  - review_trigger
- Debug target config: `skill-debug/targets/{{skill_name}}/config.yaml`
```

- [ ] **Step 5: Re-run the target-attachment tests**

Run: `python3 -m pytest tests/test_skill_debug_init_target.py -q`

Expected: PASS with `2 passed`

- [ ] **Step 6: Commit the target-attachment scaffold**

```bash
git add skill-debug src/skill_tools/skill_debug tests/test_skill_debug_init_target.py
git commit -m "feat: scaffold skill-debug target attachment"
```

## Task 5: Implement Debug Run Lifecycle And Artifact Separation

**Files:**
- Create: `src/skill_tools/skill_debug/debug_run.py`
- Create: `skill-debug/scripts/start_run.py`
- Create: `skill-debug/scripts/append_event.py`
- Create: `skill-debug/scripts/finalize_run.py`
- Create: `tests/test_skill_debug_run_lifecycle.py`
- Test: `tests/test_skill_debug_run_lifecycle.py`

- [ ] **Step 1: Write the failing debug lifecycle tests**

```python
from pathlib import Path

from skill_tools.skill_debug.debug_run import append_debug_event, finalize_debug_run, start_debug_run


def test_start_debug_run_writes_only_under_debug_root(tmp_path: Path) -> None:
    run = start_debug_run(
        repo_root=tmp_path,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
        linked_skill_run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_alias",
        review_mode="async",
    )
    assert run.debug_log.exists()
    assert "skill-debug-logs" in str(run.debug_log)
    assert not (tmp_path / "code-analyse-docs" / "debug-log.md").exists()


def test_append_debug_event_tracks_artifact_references_without_copying(tmp_path: Path) -> None:
    business_output = tmp_path / "code-analyse-docs" / "runs" / "ca-20260618-153000-auth-login.md"
    business_output.parent.mkdir(parents=True, exist_ok=True)
    business_output.write_text("# Run\n", encoding="utf-8")
    run = start_debug_run(
        repo_root=tmp_path,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
        linked_skill_run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_alias",
        review_mode="async",
    )
    append_debug_event(
        run=run,
        phase="document_update",
        action="Updated scoped overview",
        evidence=["overview existed already"],
        artifact_refs=[str(business_output)],
    )
    assert str(business_output) in run.debug_log.read_text(encoding="utf-8")
    assert not (run.run_root / "artifacts" / "ca-20260618-153000-auth-login.md").exists()
```

- [ ] **Step 2: Run the debug lifecycle tests to verify they fail**

Run: `python3 -m pytest tests/test_skill_debug_run_lifecycle.py -q`

Expected: FAIL with import errors for `skill_tools.skill_debug.debug_run`

- [ ] **Step 3: Implement debug run creation and event appending**

```python
# src/skill_tools/skill_debug/debug_run.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skill_tools.common.files import atomic_write_text, write_json


@dataclass(frozen=True)
class DebugRun:
    run_root: Path
    debug_log: Path
    artifact_index: Path
    review_request: Path


def start_debug_run(
    *,
    repo_root: Path,
    skill_name: str,
    debug_run_id: str,
    linked_skill_run_id: str,
    scope_slug: str,
    trigger_source: str,
    review_mode: str,
) -> DebugRun:
    run_root = repo_root / "skill-debug-logs" / skill_name / "runs" / debug_run_id
    debug_log = run_root / "debug-log.md"
    artifact_index = run_root / "artifacts" / "artifact-index.md"
    review_request = run_root / "review-request.json"
    atomic_write_text(
        debug_log,
        "\n".join(
            [
                "# Debug Log",
                "",
                f"- Debug Run ID: `{debug_run_id}`",
                f"- Linked Skill Run ID: `{linked_skill_run_id}`",
                f"- Scope: `{scope_slug}`",
                f"- Trigger Source: `{trigger_source}`",
                f"- Review Mode: `{review_mode}`",
                "",
                "## Timeline",
            ]
        )
        + "\n",
    )
    atomic_write_text(artifact_index, "# Artifact Index\n\n")
    write_json(review_request, {"debug_run_id": debug_run_id, "review_mode": review_mode})
    return DebugRun(run_root=run_root, debug_log=debug_log, artifact_index=artifact_index, review_request=review_request)


def append_debug_event(*, run: DebugRun, phase: str, action: str, evidence: list[str], artifact_refs: list[str]) -> None:
    current = run.debug_log.read_text(encoding="utf-8")
    block = [
        f"### {phase}",
        f"- Action: {action}",
        f"- Evidence: {', '.join(evidence) or 'none'}",
        f"- Artifact Refs: {', '.join(artifact_refs) or 'none'}",
        "",
    ]
    atomic_write_text(run.debug_log, current + "\n".join(block))
```

- [ ] **Step 4: Implement finalization and queue handoff metadata**

```python
def finalize_debug_run(*, run: DebugRun, review_mode: str) -> None:
    current = run.debug_log.read_text(encoding="utf-8")
    atomic_write_text(run.debug_log, current + "## Review Trigger\n\n" + f"- Mode: `{review_mode}`\n")
    artifact_index = run.artifact_index.read_text(encoding="utf-8")
    atomic_write_text(run.artifact_index, artifact_index + "- `debug-log.md` - human-readable execution trace\n")
```

- [ ] **Step 5: Re-run the debug lifecycle tests**

Run: `python3 -m pytest tests/test_skill_debug_run_lifecycle.py -q`

Expected: PASS with `2 passed`

- [ ] **Step 6: Commit the debug lifecycle implementation**

```bash
git add src/skill_tools/skill_debug/debug_run.py skill-debug/scripts/start_run.py skill-debug/scripts/append_event.py skill-debug/scripts/finalize_run.py tests/test_skill_debug_run_lifecycle.py
git commit -m "feat: add skill-debug run lifecycle"
```

## Task 6: Implement Review Queue, Backend Config, And Review Execution

**Files:**
- Create: `src/skill_tools/skill_debug/review_queue.py`
- Create: `src/skill_tools/skill_debug/review_run.py`
- Create: `skill-debug/scripts/enqueue_review.py`
- Create: `skill-debug/scripts/review_worker.py`
- Create: `skill-debug/scripts/review_run.py`
- Create: `skill-debug/review_runners/base.py`
- Create: `skill-debug/review_runners/noop.py`
- Create: `skill-debug/review_runners/openai_api.py`
- Create: `skill-debug/review_runners/codex_thread.py`
- Create: `skill-debug/runtime/config/backends.example.yaml`
- Create: `tests/test_skill_debug_review_queue.py`
- Create: `tests/test_skill_debug_review_run.py`
- Test: `tests/test_skill_debug_review_queue.py`
- Test: `tests/test_skill_debug_review_run.py`

- [ ] **Step 1: Write the failing queue and review tests**

```python
from pathlib import Path

from skill_tools.skill_debug.review_queue import enqueue_review_job, move_job
from skill_tools.skill_debug.review_run import load_backend_profile, select_backend_name


def test_enqueue_review_job_creates_pending_file(tmp_path: Path) -> None:
    job = enqueue_review_job(
        runtime_root=tmp_path / "skill-debug" / "runtime",
        request_path=tmp_path / "request.json",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
    )
    assert job.exists()
    assert "pending" in str(job)


def test_select_backend_name_prefers_run_override() -> None:
    selected = select_backend_name(
        run_override="test-openai",
        target_default="code-analyse-default",
        global_default="noop",
    )
    assert selected == "test-openai"


def test_load_backend_profile_reads_example_yaml(tmp_path: Path) -> None:
    config = tmp_path / "backends.local.yaml"
    config.write_text(
        "profiles:\n  test-openai:\n    runner: openai_api\n    base_url: https://example.invalid/v1\n    model: gpt-5\n    api_key_env: TEST_KEY\n",
        encoding="utf-8",
    )
    profile = load_backend_profile(config, "test-openai")
    assert profile["runner"] == "openai_api"
```

- [ ] **Step 2: Run the queue and review tests to verify they fail**

Run: `python3 -m pytest tests/test_skill_debug_review_queue.py tests/test_skill_debug_review_run.py -q`

Expected: FAIL with import errors for `skill_tools.skill_debug.review_queue` and `skill_tools.skill_debug.review_run`

- [ ] **Step 3: Implement queue state transitions and backend loading**

```python
# src/skill_tools/skill_debug/review_queue.py
from __future__ import annotations

from pathlib import Path

from skill_tools.common.files import atomic_write_text


def enqueue_review_job(*, runtime_root: Path, request_path: Path, debug_run_id: str) -> Path:
    pending_dir = runtime_root / "review-queue" / "pending"
    job_path = pending_dir / f"{debug_run_id}.json"
    atomic_write_text(job_path, "{\n" f'  "debug_run_id": "{debug_run_id}",\n' f'  "request_path": "{request_path}"\n' "}\n")
    return job_path


def move_job(*, job_path: Path, destination: str) -> Path:
    target = job_path.parents[1] / destination / job_path.name
    job_path.replace(target)
    return target
```

```python
# src/skill_tools/skill_debug/review_run.py
from __future__ import annotations

from pathlib import Path

from skill_tools.common.files import read_yaml


def select_backend_name(*, run_override: str | None, target_default: str | None, global_default: str | None) -> str:
    return run_override or target_default or global_default or "noop"


def load_backend_profile(config_path: Path, profile_name: str) -> dict[str, str]:
    config = read_yaml(config_path)
    return config.get("profiles", {}).get(profile_name, {})
```

- [ ] **Step 4: Implement review composition and backend runners**

```python
# skill-debug/review_runners/base.py
from __future__ import annotations

from typing import Protocol


class ReviewRunner(Protocol):
    def run(self, *, prompt: str, profile: dict[str, str]) -> str: ...
```

```python
# skill-debug/review_runners/noop.py
from __future__ import annotations


def run(*, prompt: str, profile: dict[str, str]) -> str:
    return "# Review\n\n- Runner: `noop`\n- Result: review skipped for offline or test execution\n"
```

```python
# skill-debug/runtime/config/backends.example.yaml
default_profile: noop
profiles:
  noop:
    runner: noop
  openai-compatible:
    runner: openai_api
    base_url: https://example.invalid/v1
    model: gpt-5
    api_key_env: SKILL_DEBUG_API_KEY
```

- [ ] **Step 5: Re-run the queue and review tests**

Run: `python3 -m pytest tests/test_skill_debug_review_queue.py tests/test_skill_debug_review_run.py -q`

Expected: PASS with `5 passed`

- [ ] **Step 6: Commit the review infrastructure**

```bash
git add src/skill_tools/skill_debug/review_queue.py src/skill_tools/skill_debug/review_run.py skill-debug/scripts/enqueue_review.py skill-debug/scripts/review_worker.py skill-debug/scripts/review_run.py skill-debug/review_runners skill-debug/runtime/config/backends.example.yaml tests/test_skill_debug_review_queue.py tests/test_skill_debug_review_run.py
git commit -m "feat: add skill-debug review infrastructure"
```

## Task 7: Attach `code-analyse` As The First Target And Validate End To End

**Files:**
- Modify: `SKILL.md`
- Create: `skill-debug/targets/code-analyse/config.yaml`
- Create: `skill-debug/targets/code-analyse/evaluation-guide.md`
- Create: `skill-debug/targets/code-analyse/review-prompt.md`
- Create: `skill-debug/targets/code-analyse/injection-state.json`
- Create: `tests/test_code_analyse_skill_debug_integration.py`
- Test: `tests/test_code_analyse_skill_debug_integration.py`

- [ ] **Step 1: Write the failing integration test**

```python
from pathlib import Path

from skill_tools.code_analyse.run_tracking import start_run
from skill_tools.skill_debug.debug_run import append_debug_event, start_debug_run
from skill_tools.skill_debug.target_init import attach_target


def test_code_analyse_target_attachment_and_debug_run_stay_separate(tmp_path: Path) -> None:
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(Path("SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
    attach_target(
        repo_root=tmp_path,
        skill_name="code-analyse",
        skill_path=skill_path,
        manual_entrypoints=["/code-analyse-debug_mode"],
        skill_output_root="code-analyse-docs",
        debug_output_root="skill-debug-logs/code-analyse",
    )
    start_run(
        output_root=tmp_path / "code-analyse-docs",
        run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        objective="Trace the auth login workflow",
        status="in_progress",
        module_scoped=True,
    )
    debug_run = start_debug_run(
        repo_root=tmp_path,
        skill_name="code-analyse",
        debug_run_id="dbg-code-analyse-20260618-153000-auth-login",
        linked_skill_run_id="ca-20260618-153000-auth-login",
        scope_slug="auth-login",
        trigger_source="manual_alias",
        review_mode="async",
    )
    append_debug_event(
        run=debug_run,
        phase="document_update",
        action="Referenced the business run document",
        evidence=["business output exists"],
        artifact_refs=[str(tmp_path / "code-analyse-docs" / "runs" / "ca-20260618-153000-auth-login.md")],
    )
    assert (tmp_path / "skill-debug" / "targets" / "code-analyse" / "config.yaml").exists()
    assert (tmp_path / "skill-debug-logs" / "code-analyse").exists()
    assert not (tmp_path / "code-analyse-docs" / "debug-log.md").exists()
```

- [ ] **Step 2: Run the integration test to verify it fails**

Run: `python3 -m pytest tests/test_code_analyse_skill_debug_integration.py -q`

Expected: FAIL until target attachment, generated target assets, and debug lifecycle are wired together

- [ ] **Step 3: Materialize the first target attachment**

Run: `python3 skill-debug/scripts/init_target.py --repo-root . --skill-name code-analyse --skill-path SKILL.md --manual-entrypoint /code-analyse-debug_mode --skill-output-root code-analyse-docs --debug-output-root skill-debug-logs/code-analyse`

Expected:
- `skill-debug/targets/code-analyse/config.yaml` exists
- `skill-debug/targets/code-analyse/evaluation-guide.md` exists
- `skill-debug/targets/code-analyse/review-prompt.md` exists
- `skill-debug/targets/code-analyse/injection-state.json` exists
- `SKILL.md` contains the managed debug block

- [ ] **Step 4: Run the full targeted test suite**

Run: `python3 -m pytest tests/test_code_analyse_run_tracking.py tests/test_code_analyse_skill_contract.py tests/test_skill_debug_init_target.py tests/test_skill_debug_run_lifecycle.py tests/test_skill_debug_review_queue.py tests/test_skill_debug_review_run.py tests/test_code_analyse_skill_debug_integration.py -q`

Expected: PASS with all tests green

- [ ] **Step 5: Commit the integrated target setup**

```bash
git add SKILL.md skill-debug/targets/code-analyse tests/test_code_analyse_skill_debug_integration.py
git commit -m "feat: attach skill-debug to code-analyse"
```

## Self-Review Checklist

- Spec coverage:
  - `code-analyse` run tracking: Tasks 2, 3, and 7
  - business/debug artifact separation: Tasks 5 and 7
  - generic `skill-debug` attachment flow: Task 4
  - async review queue and backend config: Task 6
  - first target generation for `code-analyse`: Task 7
- Placeholder scan:
  - no `TODO`, `TBD`, or "implement later" steps remain
  - each task has exact file paths and exact commands
- Type consistency:
  - `run_id`, `debug_run_id`, `scope_slug`, `review_mode`, and `manual_entrypoints` names are used consistently across tasks

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-18-skill-debug-and-code-analyse.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
