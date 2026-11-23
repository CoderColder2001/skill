---
name: "code-study-global"
description: "Use only when the user explicitly invokes /code-study-global or code-study-global for global repository architecture study. This skill maintains a persistent docs/code-study-global knowledge base for repository-wide modules, dependency boundaries, important execution flows, runtime topology, state/data flow, integration points, and follow-up study topics. Do not use it for ordinary code questions, module-only study, code review, debugging, bug fixes, or implementation work."
---

# Code Study Global

Use this skill to perform global, source-backed architecture study for an entire repository and to maintain a persistent Markdown knowledge base under `docs/code-study-global/`.

This skill is for long-running architecture understanding: module maps, runtime model, important chains, ownership boundaries, state/data flow, cross-document navigation, and future study backlog.

## Invocation Rules

- Invoke this skill only when the user explicitly runs `/code-study-global` or names `code-study-global`.
- Do not invoke this skill for generic source-reading questions, small explanations, file-specific questions, refactors, bug fixes, debugging, code review, or implementation planning.
- Do not use this skill for module-only deep dives. If the user wants one specific module analyzed in depth, use `code-study-module` instead.
- If the user explicitly invokes this skill while also naming a module, treat that module as a global-study focus topic, not as a module-scoped output root.

## Language Rules

- Default to Simplified Chinese for user-facing messages and generated Markdown documentation.
- Preserve source identifiers, file paths, package names, command names, framework names, APIs, and quoted code in their original language.
- Use another language only when the user explicitly requests it or when updating an existing document that already has a clear language convention.

## Global Scope Model

This skill has one scope: the whole repository.

- Always write the study set to `docs/code-study-global/` unless the user explicitly requests a different output root.
- Keep all topic requests, module mentions, chains, runtime questions, and follow-up needs inside the same global study set.
- Do not create `scopes/<module>/` style module-local study trees.
- Do not present a single focused topic as a complete repository-wide conclusion. Mark what is covered, partial, unknown, or deferred.

## Intake

At the start of each run, determine the user's intended focus and downstream use. If the user already gave enough information, continue without asking. If materially unclear, ask one concise question before source inspection.

Capture these fields in `current-run.md`:

- Primary focus topics, such as startup, runtime, module boundaries, dependency graph, request chain, state flow, plugin mechanism, storage, tests, or generated code.
- Downstream need, such as onboarding, design review, future refactor, incident investigation context, or architecture documentation.
- Preferred depth, such as broad map first, one critical chain first, or update existing docs incrementally.

Before asking a clarification question, start or refresh the run-tracking documents.

## Progress Reporting

During analysis, send concise progress updates to the user. Each substantial phase should include:

- `当前进度`: what has been completed and what is being inspected next.
- `当前发现`: concrete source-backed facts discovered so far.
- `文档影响`: which global study documents will be created or updated.
- `建议下一步`: the next useful analysis action and why it matters.

Use progress reporting after intake, repository inventory, entrypoint discovery, major flow tracing, document creation or update, and final review.

## Execution Artifact Rules

Every invocation must create or update run-tracking documents under `docs/code-study-global/`.

- Use `python3 scripts/code_study_global_run_tracking.py start ...` when a run begins.
- Use `python3 scripts/code_study_global_run_tracking.py append-event ...` after each major phase.
- Use `python3 scripts/code_study_global_run_tracking.py sync-future-work ...` before finishing.
- Use `python3 scripts/code_study_global_run_tracking.py finalize ...` when the run concludes.
- Keep stable run-tracking entrypoints available through `index.md`, `current-run.md`, `future-work.md`, and historical files under `runs/`.
- Do not place debug logs in `docs/code-study-global/`.

Recommended run ids:

- `csg-YYYYMMDD-HHMMSS-global`
- `csg-YYYYMMDD-HHMMSS-<focus-slug>`

## Core Principles

- Read relevant source files before writing or updating any architecture conclusion.
- Prefer source-backed explanations over guesses. If evidence is incomplete, write an `unresolved assumption`.
- Preserve and improve existing useful documentation. Update documents incrementally instead of regenerating duplicate files.
- Keep document boundaries sharp. Put navigation and synthesis in `index.md`, stable structural maps in `maps/`, and focused mechanisms or chains in `topics/`.
- Keep documents connected. Whenever a document is added, renamed, reordered, or materially updated, update the index, related links, reading order, and future-work backlog.
- Put source file and line references near the logic or flow step they support, not only in a detached appendix.

## Analysis Workflow

1. Resolve the global study intent, focus topics, downstream need, and output root.
2. Start run tracking under `docs/code-study-global/`.
3. Inspect existing `docs/code-study-global/` documents before creating new ones.
4. Build or refresh the repository inventory: languages, build files, package layout, configuration, generated artifacts, tests, commands, and runtime entrypoints.
5. Capture the current source baseline for this study run: project root, branch, HEAD, HEAD time and subject, document update time, source link style, and whether `docs/code-study-global/` is ignored by git.
6. Identify global architecture views:
   - Module map: major directories, components, responsibilities, ownership boundaries, and public interfaces.
   - Runtime topology: processes, apps, services, workers, CLIs, plugin systems, lifecycle hooks, and bootstrapping.
   - Dependency boundaries: dependency direction, cross-layer calls, extension points, external SDKs, and generated code.
   - Execution flows: important startup, request, event, task, render, sync, or persistence chains.
   - State/data flow: state ownership, caches, persistence, events, concurrency, lifecycle, and invalidation.
   - Integration points: external services, protocols, storage, telemetry, auth, feature flags, and unresolved external dependencies.
7. Trace the user's requested focus topics through source-backed call chains and data movement.
8. Update the canonical index and relevant map/topic documents.
9. Update cross-document links, reading order, coverage matrix, source baseline notes, unresolved assumptions, and future-work backlog.
10. Perform a final consistency review across all affected documents.
11. Finalize the run-tracking record and report the knowledge-base state.

## Output Structure

By default, create and maintain this structure:

```text
docs/code-study-global/
  index.md                         # Start here; canonical navigation and global synthesis
  current-run.md                   # Latest run state
  future-work.md                   # Persistent global study backlog
  runs/
    <run-id>.md                    # Historical run record
  maps/
    module-map.md                  # Global module/component responsibility map
    runtime-topology.md            # Runtime entrypoints, lifecycle, processes, plugins
    dependency-boundaries.md       # Dependency direction, ownership, integration boundaries
  topics/
    startup-flow.md                # Startup/bootstrap chains
    execution-flows.md             # Important request/event/task/render flows
    state-and-data-flow.md         # State ownership, caches, persistence, events
    integration-points.md          # External systems, SDKs, protocols, unresolved deps
```

Create additional documents only when they represent a distinct global mechanism, stable map, or important cross-module flow.

## `index.md` Rules

`index.md` is the canonical entry point and navigation surface for the global study set.

Maintain these sections:

- Document Snapshot.
- Analysis scope and current focus.
- How to read this knowledge base.
- Coverage matrix with status for each global architecture area.
- Repository-wide architecture summary.
- Reading-order tree with relative Markdown links.
- Topic index grouped by maps, flows, runtime, state/data, and integrations.
- Recently updated documents and why they changed.
- Unresolved assumptions.
- Next study topics linked to `future-work.md`.

The index should synthesize and route. Do not turn it into a long deep dive. Move details into map or topic documents and link to them.

## Map Document Rules

Use `maps/` for stable repository-wide structure.

Map documents should explain:

- Document Snapshot.
- What the architecture area covers.
- Source files and symbols inspected.
- Major components and responsibilities.
- Ownership boundaries and public interfaces.
- Dependency direction and collaboration points.
- Links to relevant topic deep dives.
- Unresolved assumptions and missing evidence.

Module/component names in maps should be Markdown links to source paths or related study documents when possible.

## Topic Document Rules

Use `topics/` for focused cross-module chains, mechanisms, or runtime behaviors.

Each topic document should include:

- Document Snapshot.
- Analysis scope.
- Purpose and when the mechanism is used.
- Source files and symbols inspected.
- Architecture position and related map documents.
- Main control flow or sequence of responsibility handoffs.
- State/data ownership and lifecycle where relevant.
- Interactions with other modules.
- Edge cases, failure modes, and unresolved assumptions.
- Reading links back to `index.md`, previous/next documents, and related maps/topics.

Flow narration should make each step understandable without forcing the reader to open every source file:

- Trigger or input.
- Current owner.
- Method, callback, event, route, or handoff.
- Produced output, state change, side effect, or next owner.
- Nearby source reference.

## Cross-Document Link Rules

Treat links and reading order as part of the deliverable.

- Use relative Markdown links between study documents.
- Every map/topic document must link back to `../index.md` or `index.md` as appropriate.
- Every map/topic document should include `Previous`, `Next`, and `Related` links when there is a meaningful reading order.
- When adding or renaming a document, update `index.md`, affected previous/next links, related links, and `future-work.md`.
- Avoid duplicating long explanations across documents. Keep one canonical explanation and link to it from related documents.
- If two documents overlap, explain their boundary explicitly in both places or consolidate the overlap.

## Coverage Matrix Rules

Maintain a coverage matrix in `index.md` so the knowledge base can grow over multiple runs without losing orientation.

Use statuses such as:

- `not_started`: not inspected yet.
- `inventory_only`: files or entrypoints identified but not explained.
- `partial`: important source paths inspected, but gaps remain.
- `verified`: conclusions are source-backed enough for current use.
- `stale`: document likely needs refresh because related source changed.

Each row should include:

- Architecture area.
- Current status.
- Key documents.
- Source baseline, such as HEAD short SHA or `not_recorded`.
- Source evidence summary.
- Known gaps or next action.

When a document was last verified against an older HEAD than the current run, either refresh the document or mark the coverage row as `stale` with the newer HEAD noted.

## Document Snapshot Rules

Every `index.md`, map document, and topic document must include a `Document Snapshot` section near the top. This section gives the reader the exact source baseline behind the architecture conclusions, which matters because global architecture documents often outlive the branch or checkout where they were first written.

Use the same fields as `code-study-module`, adapted for global study:

- Project root.
- Branch, or `detached HEAD` / `not a git repo` when appropriate.
- HEAD full SHA.
- HEAD time and subject.
- Document update time, including timezone when available.
- Source link style, such as `repo-relative links with visible line numbers`.
- Whether `docs/code-study-global/` or parent `docs/` is ignored by git.

Also record working-tree state when it affects confidence:

- `clean` when no relevant source/doc changes are pending.
- `dirty: relevant source files changed` when uncommitted source changes may affect conclusions.
- `dirty: docs only` when only generated study docs are pending.
- `unknown` when git status could not be checked.

Use commands such as these when the repository is a git checkout:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git show -s --format=%cI%n%s HEAD
git status --short
git check-ignore -q docs/code-study-global
```

If any field cannot be collected, keep the field and write `unknown`, with a short reason. Do not omit the snapshot because one value is unavailable.

Recommended Markdown shape:

```markdown
## Document Snapshot

- Project root: `/path/to/repo`
- Branch: `feature/example`
- HEAD: `abcdef1234567890...`
- HEAD time: `2026-07-16T12:34:56+08:00`
- HEAD subject: `feat: example`
- Document update time: `2026-07-16T13:00:00+08:00`
- Working tree: `dirty: docs only`
- Source link style: repo-relative links with visible line numbers, for example `[File.kt](../../path/File.kt)（L42）`
- Docs ignored by git: `yes`, `no`, or `unknown`
```

## Source Evidence Rules

- Cite source files and visible line numbers near the claim they support.
- Use repository-relative Markdown links from the generated document to source files by default, with line numbers in visible nearby text rather than inside the link target.
- If the active repository already has a working source-link convention, follow it and record that convention in `Document Snapshot`.
- After writing, verify linked source paths exist by resolving them relative to the generated Markdown file.
- For important flows, cite each major handoff or state transition.
- Distinguish verified conclusions from unresolved assumptions.
- If a dependency, protocol, generated artifact, SDK, or runtime capability depends on another repository, ask for the local path when it materially affects the conclusion.
- If the path is unavailable, document what is known from the current repository and mark the rest as unresolved.

## Incremental Update Rules

- Before writing, inspect the existing `docs/code-study-global/index.md`, relevant maps, relevant topics, `current-run.md`, and `future-work.md`.
- Compare existing document snapshots with the current run's source baseline. If the source baseline changed, update the affected document snapshot and mark stale documents in the coverage matrix until refreshed.
- Update existing documents when a topic is already covered.
- Create a new document only for a distinct global mechanism, map, or cross-module flow.
- Preserve useful existing content unless source evidence shows it is outdated or misleading.
- Record why a document changed in the run record.

## Non-Goals

This skill does not:

- Fix code or implement features.
- Perform code review.
- Debug runtime failures.
- Produce module-local documentation under `docs/<module>/`.
- Replace `code-study-module` for module-only deep dives.
- Invent external system behavior that is not visible in the current repository.

## Final Review

Before finishing, review all affected study documents and check for:

- Broken or stale links.
- Missing backlinks to `index.md`.
- Reading-order mismatches.
- Duplicated explanations that should be linked or consolidated.
- Map/topic boundary confusion.
- Missing `Document Snapshot` sections.
- Snapshot fields that are missing branch, HEAD, document update time, source link style, or docs-ignore status.
- Documents whose snapshot HEAD is older than the current source baseline but are not marked `stale` or refreshed.
- Missing coverage matrix updates.
- Missing source references near flow or logic explanations.
- Module-focused claims accidentally presented as whole-repository conclusions.
- Unresolved assumptions that need user-provided external paths.

## Completion Report

When the analysis task is complete, report:

- Current completion status.
- Documents created or updated.
- Key source areas inspected.
- Current global coverage state.
- Known uninspected areas and unresolved assumptions.
- Suggested next study topics in priority order.
- Why those next topics are the highest-priority follow-ups.

<!-- skill-debug:managed:start -->
## Debug Capability

This skill supports `skill-debug`.

- Debug support: enabled
- Debug config: `skill-debug/config.yaml`
- Debug log root: `skill-debug-logs`
- Manual debug command: `/skill-debug 调试 code-study-global`
<!-- skill-debug:managed:end -->
