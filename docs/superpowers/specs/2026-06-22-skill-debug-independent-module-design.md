# `skill-debug` Independent Module Design

## Summary

This design extracts `skill-debug` into a standalone sibling module at the workspace root and makes each target skill own its own `skill-debug` integration files. The new design removes the central `skill-debug/targets/<skill-name>/` registry model and replaces it with target-local integration directories plus a workspace-level discovery and attach flow.

The first supported target after the extraction is `code-analyse`, but the design is intentionally general so that other skills can be attached quickly through `/skill-debug 接入 <skill-name>`.

## Context

The current workspace places the generic `skill-debug` framework physically inside `code-analyse`. Although the implementation is written as reusable helpers, the package layout, scripts, templates, runtime directory, and tests all live under `code-analyse/`, which causes ownership confusion and makes other skills feel like secondary tenants of `code-analyse`.

The desired end state is stronger than a directory move:

- `skill-debug` must become an independent sibling module.
- Each target skill must own its own integration metadata.
- New target skills must be attachable through a fast prompt entrypoint.
- The workspace must provide a list view of attachable, attached, and broken targets.

## Goals

- Extract `skill-debug` into `/Users/bytedance/workspace/skill/skill-debug`.
- Make `skill-debug` framework code, templates, scripts, review runners, and framework tests independent from `code-analyse`.
- Replace the central target registry with target-local integration files under `<skill-root>/skill-debug/`.
- Support `/skill-debug list` to discover workspace skills and report integration state.
- Support `/skill-debug 接入 <skill-name>` to attach or repair a target skill quickly.
- Make repeated attach operations idempotent.
- Keep `code-analyse` as the first real attached target while allowing other skills to adopt the same pattern later.

## Non-Goals

- Do not redesign `code-analyse` business run tracking in this change.
- Do not add automatic attachment for every skill in the workspace.
- Do not build a new remote service or network dependency for review execution.
- Do not require every skill to define a business output root; target skills may leave that field empty.

## Proposed Workspace Structure

```text
skill/
  docs/
    superpowers/
      specs/
        2026-06-22-skill-debug-independent-module-design.md
  skill-debug/
    SKILL.md
    pyproject.toml
    src/
      skill_debug_tools/
        common/
        cli/
        attach/
        debug_run/
        review/
        workspace/
    scripts/
      skill_debug.py
    templates/
      injected-debug-block.md
      evaluation-guide.md
      review-prompt.md
      review.md
    review_runners/
      noop.py
      openai_api.py
      codex_thread.py
    runtime/
      config/
        backends.example.yaml
      review-queue/
        pending/
        running/
        done/
        failed/
    tests/
      test_workspace_discovery.py
      test_skill_debug_list.py
      test_skill_debug_attach.py
      test_debug_run_lifecycle.py
      test_review_queue.py
      test_review_run.py
  code-analyse/
    SKILL.md
    pyproject.toml
    src/
      skill_tools/
        code_analyse/
    scripts/
      code_analyse_run_tracking.py
    skill-debug/
      config.yaml
      evaluation-guide.md
      review-prompt.md
      injection-state.json
    skill-debug-logs/
      runs/
    tests/
      test_code_analyse_run_tracking.py
      test_code_analyse_skill_contract.py
      test_code_analyse_skill_debug_integration.py
```

## Ownership Model

### `skill-debug` Framework Module

The standalone `skill-debug` module owns only generic framework concerns:

- workspace skill discovery
- integration status evaluation
- attach and repair logic
- managed block rendering
- debug run lifecycle helpers
- review input assembly and execution
- asynchronous review queue management
- review backend runners
- generic templates
- shared runtime config and queue state

The framework must not own or persist a central target configuration registry for attached skills.

### Target Skill Ownership

Each target skill owns its own integration metadata under `<skill-root>/skill-debug/`:

- `config.yaml`
- `evaluation-guide.md`
- `review-prompt.md`
- `injection-state.json`

Each target skill also owns its own debug run artifacts under `<skill-root>/skill-debug-logs/`.

This means that if a target skill is moved, copied, or split into a new repository, its `skill-debug` integration files and debug logs travel with it instead of staying behind in a framework-owned target registry.

## Discovery Model

### Skill Discovery

`/skill-debug list` and `/skill-debug 接入 <skill-name>` both use the same workspace discovery logic:

1. scan the workspace for directories that contain `SKILL.md`
2. read frontmatter from each `SKILL.md`
3. treat the `name` field as the canonical skill name
4. build a workspace skill index keyed by skill name and path

Discovery rules:

- if exactly one skill matches a requested `<skill-name>`, use it
- if no skills match, return the known skill names
- if multiple skills share the same `name`, require a path-qualified disambiguation flow later; for this change, report the ambiguity and refuse to attach automatically

### Integration Status Categories

Each discovered skill is classified into one of three states:

- `attachable`
  - `SKILL.md` exists
  - no local `skill-debug/config.yaml` exists yet
- `attached`
  - local integration files exist
  - `SKILL.md` managed block matches the current render rules
  - `injection-state.json` agrees with the discovered skill identity
- `broken`
  - attachment is partial, stale, mismatched, or drifted
  - examples: missing files, mismatched skill name, stale managed block, inconsistent injection fingerprint

`/skill-debug list` reports these states directly.

## Command Model

### `/skill-debug list`

Purpose:

- enumerate all discovered workspace skills
- report which skills are attachable, attached, or broken

Behavior:

- uses the workspace discovery model above
- sorts output deterministically by skill name, then by path
- includes enough path detail for the user to understand where the skill lives
- shows broken skills with a short reason so the user understands whether `/skill-debug 接入 <skill-name>` will repair it

Expected user value:

- users can see which skills are available to attach
- users can see which skills are already attached
- users can spot drift or partial attachment quickly

### `/skill-debug 接入 <skill-name>`

Purpose:

- attach `skill-debug` to a target skill
- repair an already attached target if its state is broken

Behavior:

1. discover the target skill by `name`
2. create or repair `<skill-root>/skill-debug/`
3. inject or refresh the managed block in `<skill-root>/SKILL.md`
4. preserve target-owned custom files when safe
5. update `injection-state.json` to reflect the current attachment state

Expected effects:

- first attach creates default integration files
- repeated attach is idempotent
- running attach on a broken target repairs the target toward the canonical state

## Target-Local Integration Contract

Every attached target skill owns these files:

### `<skill-root>/skill-debug/config.yaml`

This is the main user-facing integration contract for the target skill.

Initial schema:

```yaml
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

Field rules:

- `schema_version`: required integer for future migrations
- `target_skill`: must match the discovered `SKILL.md` frontmatter `name`
- `skill_path`: relative path to the skill contract file, default `SKILL.md`
- `skill_output_root`: optional relative path to target business outputs; may be omitted or set to null
- `debug_output_root`: relative path to target-local debug artifacts, default `skill-debug-logs`
- `auto_debug_allowed`: target-specific policy flag
- `default_review_mode`: default review execution mode, initially `async`
- `default_backend_profile`: default framework review backend profile, initially `noop`
- `manual_debug_command`: rendered help text for the target skill

### `<skill-root>/skill-debug/evaluation-guide.md`

This file is generated from a framework template on first attach. After creation it becomes target-owned content. Later attach operations do not overwrite it unless the user explicitly requests regeneration in a future feature.

### `<skill-root>/skill-debug/review-prompt.md`

This file is generated from a framework template on first attach. Like the evaluation guide, it becomes target-owned and is preserved on re-attach.

### `<skill-root>/skill-debug/injection-state.json`

This is a tool-managed status file, not a manual configuration surface.

It records:

- `schema_version`
- `target_skill`
- `skill_path`
- `managed_block_marker`
- `managed_block_version`
- `managed_block_fingerprint`
- `last_attach_result`
- `last_attach_at` or equivalent timestamp when available

Its main purpose is to support:

- drift detection
- idempotent re-attach
- broken-state reporting in `/skill-debug list`

## Managed Block Contract

Each attached target `SKILL.md` receives a `skill-debug` managed block. The block must describe the local integration paths, not framework-owned target registry paths.

Required content shape:

- `Debug support: enabled`
- `Debug config: skill-debug/config.yaml`
- `Debug log root: skill-debug-logs`
- `Manual debug command: /skill-debug 调试 <skill-name>`

The managed block must never mention a central path like `skill-debug/targets/<skill-name>/config.yaml`.

The block is rendered by the framework and tracked through the fingerprint stored in `injection-state.json`.

## Runtime and Artifact Model

### Framework-Owned Shared Runtime

The independent `skill-debug` module keeps only shared runtime concerns under its own root:

- `skill-debug/runtime/config/backends.local.yaml`
- `skill-debug/runtime/review-queue/`

These are shared because they are not logically owned by any one target skill.

### Target-Owned Debug Artifacts

Each target skill stores debug artifacts under its own root:

- `<skill-root>/skill-debug-logs/runs/<debug-run-id>/debug-log.md`
- `<skill-root>/skill-debug-logs/runs/<debug-run-id>/artifacts/artifact-index.md`
- `<skill-root>/skill-debug-logs/runs/<debug-run-id>/review.md`
- `<skill-root>/skill-debug-logs/runs/<debug-run-id>/review-status.json`

This keeps debug traces physically close to the skill they belong to and prevents the framework module from becoming the owner of target debug history.

## Data Flow

### List Flow

1. discover all `SKILL.md` files in the workspace
2. parse skill names from frontmatter
3. inspect local target integration files under each discovered skill root
4. inspect the managed block in each target `SKILL.md`
5. compute `attachable`, `attached`, or `broken`
6. render the result to the user

### Attach Flow

1. discover the requested target skill
2. compute current integration state
3. create missing integration files under `<skill-root>/skill-debug/`
4. preserve target-owned prompt and guide files if they already exist
5. render and write the managed block into `<skill-root>/SKILL.md`
6. compute the new fingerprint
7. write `injection-state.json`
8. return a result that says whether the target was newly attached, already aligned, or repaired

### Debug Review Flow

1. read target-local config from `<skill-root>/skill-debug/config.yaml`
2. write target-local logs to `<skill-root>/<debug_output_root>/runs/<debug-run-id>/`
3. resolve shared backend and queue config from `/skill-debug/runtime/`
4. assemble review input from:
   - target-local `review-prompt.md`
   - target-local `evaluation-guide.md`
   - target-local debug log and artifact index
   - referenced business artifacts when available
5. execute the review runner
6. persist review outputs back under the target-local debug run directory

## Idempotency Rules

`/skill-debug 接入 <skill-name>` must be safe to run repeatedly.

Rules:

- if `config.yaml` exists, parse and merge defaults without erasing target-owned values
- if `evaluation-guide.md` exists, preserve it
- if `review-prompt.md` exists, preserve it
- if the managed block exists, replace only that block
- if `injection-state.json` exists, refresh its computed fields
- if the target is already aligned, return a no-op success result rather than rewriting unrelated content

## Error Handling

### Discovery Errors

- no matching skill name: return a clear not-found result with known skills
- ambiguous skill name: return an ambiguity result and do not attach
- invalid or missing frontmatter name: list the directory as non-discoverable and exclude it from attach candidates

### Attachment Errors

- missing `SKILL.md`: cannot attach
- local files partially exist: classify as `broken`, then repair on attach where possible
- local files contain a different `target_skill` than discovered name: classify as `broken` and refuse silent overwrite; attach may repair by rewriting canonical fields because the requested target is explicit

### Review Errors

- missing target-local config: classify target as broken before run start
- missing backend profile: fail the review with explicit status metadata
- bad path escapes in debug run identifiers or configured paths: reject the run

## Testing Strategy

### Framework Tests in `/skill-debug/tests`

Move generic `skill-debug` tests out of `code-analyse` and into the new framework module. These tests cover:

- workspace skill discovery
- status classification for `attachable`, `attached`, and `broken`
- attach idempotency
- attach repair behavior for broken targets
- managed block rendering and replacement
- target-local config parsing
- debug run lifecycle
- review queue behavior
- review input assembly and runner selection

### Target Integration Tests in `/code-analyse/tests`

Keep `code-analyse` tests focused on `code-analyse`, plus a narrow integration layer:

- `code-analyse` business run tracking tests remain local
- `test_code_analyse_skill_debug_integration.py` proves that `code-analyse` can be discovered, attached, and debugged through the new target-local contract

`code-analyse` must no longer host the entire generic framework test suite.

## Migration Plan

### Step 1: Create the Independent Framework Module

- create `/skill-debug`
- add standalone packaging and tests
- move reusable framework code there
- rename the generic package to `skill_debug_tools`

### Step 2: Move Generic Framework Tests

- migrate `test_skill_debug_*` from `code-analyse/tests` into `skill-debug/tests`
- update imports to the independent package
- make framework tests pass without relying on the `code-analyse` source tree

### Step 3: Introduce Target-Local Integration

- replace central target registry reads and writes
- implement target-local integration files under `<skill-root>/skill-debug/`
- implement workspace discovery and status classification
- implement `/skill-debug list`
- implement `/skill-debug 接入 <skill-name>`

### Step 4: Reattach `code-analyse` as the First Real Target

- generate or repair `code-analyse/skill-debug/`
- update `code-analyse/SKILL.md` to the new managed block format
- direct debug artifacts to `code-analyse/skill-debug-logs/`
- keep only the narrow integration tests inside `code-analyse`

### Step 5: Remove Old Embedded Framework Copies

- delete the old `code-analyse/src/skill_tools/skill_debug/`
- delete old framework scripts, templates, review runners, runtime directories, and central target assets under `code-analyse`
- verify that `skill-debug` no longer depends on `code-analyse` layout

## Acceptance Criteria

- `skill-debug` is a standalone sibling module at the workspace root.
- `skill-debug` no longer stores target configs under a central `targets/<skill-name>/` directory.
- `/skill-debug list` correctly reports attachable, attached, and broken skills in the workspace.
- `/skill-debug 接入 code-analyse` creates or repairs target-local integration files under `code-analyse/skill-debug/`.
- repeated attach for the same target is idempotent.
- `code-analyse` debug logs are written under `code-analyse/skill-debug-logs/`, not under the framework module.
- generic `skill-debug` tests live under `/skill-debug/tests`.
- `code-analyse` keeps only its own business tests plus narrow integration coverage.

## Open Questions Resolved In This Design

- Should target configs stay centralized under the framework module?
  - No. Target configs become target-local.
- Should debug logs stay centralized?
  - No. Debug logs become target-local.
- Should users have a quick attach command?
  - Yes. `/skill-debug 接入 <skill-name>` is the default attach entrypoint.
- Should users have a workspace listing command?
  - Yes. `/skill-debug list` is part of the base command set.

## Recommendation

Implement this change as one extraction and target-localization effort rather than a two-step migration through a long-lived central registry compatibility layer. A short compatibility shim during refactoring is acceptable inside the implementation, but the final committed design should expose only the target-local model.
