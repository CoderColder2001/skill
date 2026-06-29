# Skill Debug And Code Analyse Design

## Status

Approved design draft for implementation.

## Context

The current `code-analyse` skill defines how repository-wide and module-scoped architecture analysis should be performed, but it does not yet guarantee that each `/code-analyse` run leaves behind a stable run record and future-work record in files. Progress reporting and completion reporting are currently conversation-level behaviors.

The workspace also needs a reusable `skill-debug` capability that can be attached to any skill, not only `code-analyse`. That capability should support debug-mode execution, trace logging, evaluation-guide generation, and post-run review without mixing debug artifacts into the target skill's business output directory.

## Goals

- Make every `/code-analyse` invocation create or update stable run-tracking documents.
- Preserve both historical run snapshots and stable "latest state" entry points.
- Preserve both global future work and scope-local future work.
- Introduce a reusable `skill-debug` module for trace/debug across arbitrary skills.
- Allow both manual debug entrypoints and automatic debug activation through configuration.
- Keep debug artifacts physically separate from target skill business artifacts.
- Generate target-specific evaluation and review assets when a skill is attached to `skill-debug`.
- Support configurable review backends that can later be driven by user-provided URL, token, model, and related settings.

## Non-Goals

- Do not attempt to record private model chain-of-thought.
- Do not make `skill-debug` own or rewrite target skill business logic.
- Do not make the first version support every possible purely conversational skill with no file outputs or no stable phases.
- Do not merge debug logs into `code-analyse-docs/` or any other target skill output root.

## Design Summary

The design has two linked parts:

1. `code-analyse` gains a stable run-tracking and future-work file model under `code-analyse-docs/`.
2. `skill-debug` becomes a generic trace/debug framework that can attach to a target skill through a small declarative debug capability block plus external target configuration, scripts, templates, and review backends.

The target skill produces business artifacts. `skill-debug` produces debug artifacts. `skill-debug` may reference target business artifacts, but may not store them as canonical debug outputs.

## Decisions

- Every `/code-analyse` invocation creates or updates run-tracking documents, even if the run pauses immediately for clarification.
- Run semantics are "one parent run plus turn events", not "one run per assistant turn".
- `code-analyse` maintains both global and scope-local `current-run.md` and `future-work.md`.
- `skill-debug` is generic and target-agnostic at the framework layer.
- `skill-debug` attaches to a target skill through a declarative injected debug block plus target-specific configuration.
- Manual debug entrypoints and automatic debug flags are both supported.
- Debug logging uses a layered model: readable main log, artifact index, and raw artifacts.
- Review is configurable but defaults to asynchronous post-processing.
- Evaluation guides and target-specific review prompt overlays are generated when the target skill is attached to `skill-debug`, not regenerated on every run.
- Review backend connection details live in `skill-debug/runtime/config/`, not in target configuration.

## Artifact Boundaries

### `code-analyse` Business Artifacts

Business artifacts remain under `code-analyse-docs/`.

```text
code-analyse-docs/
  current-run.md
  future-work.md
  runs/
    <run-id>.md
  scopes/
    <scope-slug>/
      overview.md
      current-run.md
      future-work.md
      runs/
        <run-id>.md
      ...
```

These files represent analysis state, analysis outputs, and future-work planning. They are the canonical outputs of `code-analyse`.

### `skill-debug` Debug Artifacts

Debug artifacts remain outside the target skill output root.

```text
skill-debug-logs/
  <skill-name>/
    runs/
      <debug-run-id>/
        debug-log.md
        review.md
        review-status.json
        review-request.json
        artifacts/
          artifact-index.md
          tool-events.jsonl
          files-read.md
          files-written.md
          review-input.md
          command-output/
            001.txt
            002.txt
```

These files represent execution tracing, debug review, and raw or semi-raw supporting material.

### Boundary Rules

- `code-analyse` may write only to `code-analyse-docs/`.
- `skill-debug` may write only to `skill-debug-logs/`, `skill-debug/targets/`, and `skill-debug/runtime/`.
- Debug logs may reference business artifacts by path.
- Debug logs may not absorb business artifacts as canonical copies.
- Review runtime state must live under `skill-debug/runtime/`, not under `skill-debug-logs/`.

## `code-analyse` Stable Run Model

### File Layout

Global files:

- `code-analyse-docs/current-run.md`
- `code-analyse-docs/future-work.md`
- `code-analyse-docs/runs/<run-id>.md`

Scope-local files:

- `code-analyse-docs/scopes/<scope-slug>/overview.md`
- `code-analyse-docs/scopes/<scope-slug>/current-run.md`
- `code-analyse-docs/scopes/<scope-slug>/future-work.md`
- `code-analyse-docs/scopes/<scope-slug>/runs/<run-id>.md`

### Run Identity

Business run ids should be readable and deterministic enough for humans, for example:

- `ca-20260618-153000-repo`
- `ca-20260618-153000-auth-login`

A run id includes:

- skill prefix
- timestamp
- scope slug or `repo`

### Run Creation Rules

On every `/code-analyse` invocation:

- create or update global `current-run.md`
- create `runs/<run-id>.md`

If scope is already known and module-scoped:

- create or update `scopes/<scope-slug>/current-run.md`
- create `scopes/<scope-slug>/runs/<run-id>.md`

If the run pauses for clarification before real source inspection:

- still create run-tracking documents
- set status to `needs_clarification`
- record the reason for clarification

### Run Lifecycle

Each parent run contains turn events. The run persists across clarification and follow-up turns until the analysis is complete or explicitly stopped.

Suggested business statuses:

- `needs_clarification`
- `in_progress`
- `completed`
- `partial`
- `stopped`

### `current-run.md`

Purpose:

- stable latest-state entry point
- overwritten on newer relevant runs

Contents:

- current run metadata
- current status
- current scope
- current objective
- most recent event timeline
- current output files
- current unresolved items
- next immediate action

### `future-work.md`

Purpose:

- persistent future-analysis backlog
- not a single-run summary

Global file contents:

- global topic backlog
- priority
- rationale
- blockers
- suggested evidence or source paths
- status (`open`, `deferred`, `resolved`)
- last touched by run

Scope file contents:

- scope-local next topics
- missing evidence
- external dependency gaps
- recommended reading order for follow-up work
- status and last touched by run

### `runs/<run-id>.md`

Purpose:

- immutable or append-only historical parent-run record

Contents:

- run metadata
- trigger source
- analysis scope
- status history
- turn event timeline
- files inspected
- files produced or updated
- key findings
- unresolved assumptions
- next topics
- references to `current-run.md`, `future-work.md`, and scope outputs

### Event Model

Each run event should include:

- event timestamp
- turn index
- phase
- action summary
- evidence
- outputs
- next step

For `code-analyse`, the initial phase set should be:

- `scope_resolution`
- `clarification`
- `source_inspection`
- `flow_tracing`
- `document_update`
- `future_work_update`
- `final_review`

## `skill-debug` Generic Architecture

### Workspace Layout

```text
skill-debug/
  SKILL.md
  templates/
    injected-debug-block.md
    debug-log.md
    review.md
    review-prompt.md
    evaluation-guide.md
  scripts/
    init_target.py
    start_run.py
    append_event.py
    finalize_run.py
    enqueue_review.py
    review_worker.py
    review_run.py
  review_runners/
    base.py
    noop.py
    codex_thread.py
    openai_api.py
  targets/
    <skill-name>/
      config.yaml
      evaluation-guide.md
      review-prompt.md
      injection-state.json
  runtime/
    config/
      backends.example.yaml
      backends.local.yaml
    review-queue/
      pending/
      running/
      done/
      failed/
```

### Responsibilities

#### `templates/`

- hold generic templates
- contain framework-wide prompt and log shapes

#### `targets/<skill-name>/`

- hold persistent target-specific debug assets
- separate target policy from runtime state

`config.yaml` contains:

- target skill name
- path to target `SKILL.md`
- manual debug entrypoints
- auto debug permission
- default review mode
- business output root
- debug output root
- enabled hooks
- default backend profile

`evaluation-guide.md`:

- generated once when target is attached
- long-lived review rubric for the target skill

`review-prompt.md`:

- generated once when target is attached
- target-specific prompt overlay, not the full final prompt

`injection-state.json`:

- injected block version
- last injection time
- target skill fingerprint
- drift detection metadata

#### `runtime/config/`

- hold environment-local backend connection settings
- allow future user-provided URL, token, model, timeout, retry, and related values

`backends.local.yaml` should normally be local-only and ignored by version control.

#### `runtime/review-queue/`

- hold asynchronous review jobs and state transitions
- act as runtime machinery, not user-facing logs

## Target Attachment Model

### Declarative Injected Debug Block

Each attached skill receives a small declarative block in its `SKILL.md`.

Example shape:

```md
## Debug Capability

This skill supports `skill-debug`.

- Debug support: enabled
- Manual debug entrypoints:
  - `/code-analyse-debug_mode`
- Automatic debug trigger: allowed
- Default debug review mode: async
- Debug log root: `skill-debug-logs/code-analyse/`
- Skill output root: `code-analyse-docs/`
- Debug hooks:
  - run_start
  - step_event
  - artifact_ref
  - run_finalize
  - review_trigger
- Debug target config: `skill-debug/targets/code-analyse/config.yaml`
```

Rules:

- do not alter frontmatter
- do not rewrite the target skill's business workflow
- do not embed heavy templates or review instructions in the target `SKILL.md`

### Attachment Flow

`skill-debug/scripts/init_target.py` should:

1. read the target `SKILL.md`
2. generate `targets/<skill-name>/config.yaml`
3. generate `targets/<skill-name>/evaluation-guide.md`
4. generate `targets/<skill-name>/review-prompt.md`
5. inject or refresh the declarative debug capability block
6. update `targets/<skill-name>/injection-state.json`

## Debug Run Model

### Debug Run Identity

Debug run ids are separate from business run ids, for example:

- `dbg-code-analyse-20260618-153000-auth-login`

Each debug run stores:

- target skill name
- debug run id
- linked skill run id
- scope slug
- trigger source (`manual_alias`, `auto_flag`)
- review mode (`async`, `sync`, `disabled`)

### Entry Modes

Both entry modes are supported:

- manual debug entrypoint, such as `/code-analyse-debug_mode`
- automatic debug through configuration or flag

Priority order:

1. manual debug alias
2. explicit auto debug flag
3. target default behavior

### Hook Protocol

The generic first-version hook set is:

- `run_start`
- `step_event`
- `artifact_ref`
- `run_finalize`
- `review_trigger`

Responsibilities:

`run_start`

- allocate debug run id
- create debug run directory
- initialize `debug-log.md`

`step_event`

- append a structured event for a significant skill step

`artifact_ref`

- add references to target business artifacts without copying them

`run_finalize`

- close out the run
- write final summary
- write artifact index
- write review request metadata

`review_trigger`

- enqueue or run review based on configured mode

## Debug Log and Artifact Design

### `debug-log.md`

The main debug log must be readable on its own.

Recommended sections:

- run metadata
- skill objective
- debug objective
- execution timeline
- key decisions
- tool activity summary
- skill output references
- issues and uncertainty
- review trigger status

The log should include human-readable reasons and evidence, not private chain-of-thought.

### Artifact Files

`artifact-index.md`

- list all artifacts
- explain their purpose
- provide suggested reading order

`tool-events.jsonl`

- one structured event per line
- suitable for programmatic or secondary model consumption

`files-read.md`

- path
- reason read
- important symbols or sections used

`files-written.md`

- path
- action (`create`, `update`)
- reason changed
- linked event ids

`review-input.md`

- reproducible review input snapshot

`command-output/*.txt`

- full raw output for important commands

### Main Log Compression Rule

- main log includes summary plus key excerpts
- raw output goes to artifacts
- review documents must judge execution, not restate the log

## Review Design

### Review Flow

Default mode is asynchronous post-processing.

Asynchronous flow:

1. `finalize_run.py` writes `review-request.json`
2. `enqueue_review.py` writes a queue job
3. `review_worker.py` moves the job to `running/`
4. `review_worker.py` calls `review_run.py`
5. `review_run.py` selects a backend runner
6. `review.md` and `review-status.json` are written
7. queue state moves to `done/` or `failed/`

Synchronous flow:

- `finalize_run.py` calls `review_run.py` directly

### `review_run.py`

Responsibilities:

1. read target config
2. read target evaluation guide
3. read target review prompt overlay
4. read main debug log and artifact index
5. gather referenced business outputs as needed
6. build a reproducible review input snapshot
7. compose final prompt from:
   - global review prompt template
   - target review prompt overlay
   - target evaluation guide
   - run-specific materials
8. select backend runner
9. write `review.md`
10. write `review-status.json`

### Backend Configuration

Backends are configured separately from target configuration.

`runtime/config/backends.example.yaml` documents the shape.

`runtime/config/backends.local.yaml` holds live configuration such as:

- runner type
- base URL
- model
- api key env name or token source
- extra headers
- timeout
- retry settings

Backend selection priority:

1. run-specific override
2. target default backend profile
3. global default backend profile

### Review Runners

Initial runner set:

- `noop.py`
- `codex_thread.py`
- `openai_api.py`

The target skill never calls a backend directly. It only triggers the review hook.

## Error Handling

### Target Skill Run Tracking

If `code-analyse` cannot continue because clarification is needed:

- write run state first
- then ask the clarification question

If global and scope files disagree:

- latest run document is source of truth
- `current-run.md` and `future-work.md` must be reconciled during final review

### Debug Failures

Manual debug mode:

- if debug initialization fails, surface the failure clearly
- do not pretend debug mode succeeded

Automatic debug mode:

- fail open by default
- business execution may continue if debug setup fails
- debug failure is recorded in debug-side state if possible

Review failures:

- business outputs remain valid
- debug run records review failure status
- queue state moves to `failed/`
- failed reviews can be retried later

## Testing Strategy

### `code-analyse`

- verify first run creates global run-tracking files
- verify module-scoped run creates scoped run-tracking files
- verify clarification-only run still creates run documents
- verify `future-work.md` persists item state across runs
- verify global and scoped current-run files update correctly

### `skill-debug`

- verify target initialization creates config, guide, prompt overlay, and injected block
- verify debug mode creates debug run directory without writing into target output root
- verify artifact references point to business outputs without copying them
- verify asynchronous review enqueues correctly
- verify synchronous review executes directly
- verify backend config selection precedence
- verify failure handling for missing backend or failed review

### Integration

- attach `skill-debug` to `code-analyse`
- run a clarification-only debug session
- run a full module-scoped debug session
- verify:
  - business outputs appear only in `code-analyse-docs/`
  - debug outputs appear only in `skill-debug-logs/`
  - review runtime state appears only in `skill-debug/runtime/`
  - cross-references are correct

## Rollout Order

Implementation should proceed in this order:

1. extend `code-analyse` run-tracking and future-work model
2. scaffold `skill-debug` generic directory and templates
3. implement target attachment flow
4. connect `code-analyse` as the first target
5. implement debug log lifecycle
6. implement review queue and review runners
7. validate end-to-end with `code-analyse`

## Success Criteria

The design is successful when:

- every `/code-analyse` invocation leaves behind consistent business run-tracking documents
- future-work state is maintained consistently across runs
- `skill-debug` can attach to `code-analyse` without mixing debug and business outputs
- debug runs produce readable logs plus raw artifacts
- a target-specific evaluation guide and review prompt overlay are generated at target-attachment time
- review execution can later be configured with user-provided backend URL, token, and related settings without changing the target skill's `SKILL.md`
