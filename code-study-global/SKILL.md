---
name: "code-study-global"
description: "Use only when the user explicitly invokes /code-study-global or code-study-global for global repository architecture study. Maintain a source-backed docs/code-study-global knowledge base covering modules, dependency boundaries, execution flows, runtime topology, state/data flow, integration points, and, when warranted, designs worth learning and the problems they solve. Do not activate for ordinary code questions, module-only study, code review, debugging, implementation, or requests to review/edit this skill itself."
---

# Code Study Global

Use this skill to perform global, source-backed architecture study for an entire repository and to maintain a persistent Markdown knowledge base under `docs/code-study-global/`.

This skill is for long-running architecture understanding: module maps, runtime model, important chains, ownership boundaries, state/data flow, cross-document navigation, and future study backlog.

## Invocation Rules

- Invoke this skill only when the user explicitly runs `/code-study-global` or names `code-study-global`.
- Do not invoke this skill for generic source-reading questions, small explanations, file-specific questions, refactors, bug fixes, debugging, code review, or implementation planning.
- Do not use this skill for module-only deep dives. If the user wants one specific module analyzed in depth, use `code-study-module` instead.
- If the user explicitly invokes this skill while also naming a module, treat that module as a global-study focus topic, not as a module-scoped output root.
- A request to analyze or improve the skill itself is skill maintenance, not a repository-study invocation.

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

Resolve the project root from the user's path or `git rev-parse --show-toplevel`, falling back to the current directory. Read applicable repository instructions. Use `rg` and `rg --files` for discovery.

Use the user's focus, downstream use, and preferred depth when supplied. Otherwise, start with a broad architecture map and one representative execution flow. Do not require answers to optional preference questions. If the target repository is ambiguous, inspect available context and ask one targeted question before creating artifacts.

Capture these fields in `current-run.md`:

- Primary focus topics, such as startup, runtime, module boundaries, dependency graph, request chain, state flow, plugin mechanism, storage, tests, or generated code.
- Downstream need, such as onboarding, design review, future refactor, incident investigation context, or architecture documentation.
- Preferred depth, such as broad map first, one critical chain first, or update existing docs incrementally.

Read existing study documents and run state before starting a new run, because `start` replaces `current-run.md`. Keep source inspection read-only; do not change project source, install dependencies, or run builds, tests, apps, or network operations unless requested or required by repository instructions for this output.

## Progress Reporting

Send concise updates at meaningful milestones: what the source establishes, what remains uncertain, and what will be inspected or documented next. Avoid repeating a fixed status template after every search.

## Execution Artifact Rules

Keep lightweight continuity records under the chosen study output root: `current-run.md`, `future-work.md`, and `runs/<run-id>.md`, linked from `index.md`.

Use the bundled helper following [run-tracking instructions](references/run-tracking.md). Resolve its path relative to this `SKILL.md`, and pass the target project's absolute output path; do not assume the target project contains the skill's `scripts/` directory. Record substantive findings and document changes, not every tool call. If Python is unavailable, maintain the same records directly using the bundled `templates/` as a guide.

## Core Principles

- Read relevant source files before writing or updating any architecture conclusion.
- Prefer source-backed explanations over guesses. If evidence is incomplete, write an `unresolved assumption`.
- Preserve and improve existing useful documentation. Update documents incrementally instead of regenerating duplicate files.
- Keep document boundaries sharp. Put navigation and synthesis in `index.md`, stable structural maps in `maps/`, and focused mechanisms or chains in `topics/`.
- Keep documents connected. Whenever a document is added, renamed, reordered, or materially updated, update the index, related links, reading order, and future-work backlog.
- Put source file and line references near the logic or flow step they support, not only in a detached appendix.

## Analysis Workflow

1. Resolve the global study intent, focus topics, downstream need, and output root.
2. Inspect existing documents and run state under the chosen output root before creating or replacing records.
3. Start run tracking under that output root.
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
8. Identify designs worth learning when the inspected source supports a concrete problem–mechanism explanation; apply the Design Lessons Rules below.
9. Update the canonical index and relevant map/topic documents, including design lessons only where useful.
10. Update cross-document links, reading order, coverage matrix, source baseline notes, unresolved assumptions, and future-work backlog.
11. Perform a final consistency review across all affected documents.
12. Finalize the run-tracking record and report the knowledge-base state.

Prioritize the user's focus and representative cross-module paths. Stop expanding a supporting branch once its contract, owner, handoff, and effect on the main flow are clear. Mark uninspected areas and unavailable external implementations explicitly; do not recursively study every dependency or claim complete coverage from a directory inventory.

## Output Structure

Use this structure as a navigation guide. Create maps and topics only when inspected source supports useful content; do not create empty documents to fill the tree.

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
    design-lessons.md              # Optional: cross-module designs worth learning
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
- Links to designs worth learning, if documented, with a one-line summary of the problem each solves.
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
- Optional `值得学习的设计与解决的问题` section, following the Design Lessons Rules.
- Reading links back to `index.md`, previous/next documents, and related maps/topics.

Flow narration should make each step understandable without forcing the reader to open every source file:

- Trigger or input.
- Current owner.
- Method, callback, event, route, or handoff.
- Produced output, state change, side effect, or next owner.
- Nearby source reference.

## Design Lessons Rules

While tracing real flows and boundaries, look for designs that teach a reusable way to solve a concrete problem in this project. Include them only when there is enough evidence to explain why they are useful. A familiar pattern name, abstraction, or large class is not sufficient by itself.

Prefer a `值得学习的设计与解决的问题` section in the relevant map or topic. When several lessons span modules or need a shared explanation, use `topics/design-lessons.md` and link to it from `index.md` and the relevant maps/topics. Keep one canonical explanation; the standalone document follows the same snapshot, evidence, and navigation rules as other topics.

For each selected design, explain:

1. **问题与约束**：项目实际面对的场景、限制或复杂度；缺少这层机制时会出现什么问题。区分源码可见事实与反事实推断，不虚构历史故障或作者动机。
2. **设计与实现**：关键职责、接口、数据结构或协作流程如何解决问题，给出具体类/方法和附近的源码行号链接。
3. **收益与依据**：说明机制带来的实际效果或由源码推导的收益。没有测试、数据或历史证据时，不声称已验证的性能提升、故障减少或演进效果。
4. **代价与适用边界**：引入的复杂度、维护成本或限制，什么条件下值得借鉴、什么情况下不适合照搬。

Keep each lesson proportional to the evidence. Do not force a fixed number of lessons, label ordinary code as an elegant design, or add generic pattern tutorials. If no suitable design is found in the inspected scope, omit the section and standalone file; this is not a coverage gap. When revisiting a lesson, recheck its evidence and revise or remove unsupported claims.

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

When HEAD changes, compare the documented source paths and relevant contracts with the previous baseline, including relevant uncommitted changes. Reuse verified conclusions when that evidence is unchanged and record the comparison. If relevant evidence changed or cannot be compared, refresh the document or mark the coverage row as `stale` with the newer HEAD noted. A different HEAD alone does not make every document stale.

## Document Snapshot Rules

Every `index.md`, map document, and topic document must include a `Document Snapshot` section near the top. This section gives the reader the exact source baseline behind the architecture conclusions, which matters because global architecture documents often outlive the branch or checkout where they were first written.

Record these fields:

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
- Recheck cited symbols and lines against the claim; a valid path or in-range line number alone does not prove the explanation.
- For important flows, cite each major handoff or state transition.
- Distinguish verified conclusions from unresolved assumptions.
- If a dependency, protocol, generated artifact, SDK, or runtime capability depends on another repository, ask for the local path when it materially affects the conclusion.
- If the path is unavailable, document what is known from the current repository and mark the rest as unresolved.

## Incremental Update Rules

- Before writing, inspect the existing `index.md`, relevant maps/topics, `current-run.md`, and `future-work.md` under the chosen output root.
- Compare existing document snapshots with the current source baseline using the Coverage Matrix Rules. Advance a document's verified baseline only after checking its supporting evidence; do not stamp untouched documents with the current HEAD.
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
- Documents whose relevant evidence changed or could not be compared, but are not marked `stale` or refreshed.
- Missing coverage matrix updates.
- Missing source references near flow or logic explanations.
- Module-focused claims accidentally presented as whole-repository conclusions.
- Unresolved assumptions that need user-provided external paths.
- Design lessons that lack a concrete problem, source-backed mechanism, benefit evidence, or tradeoffs; empty optional sections and duplicated lessons.

## Completion Report

When the analysis task is complete, report:

- Current completion status.
- Documents created or updated.
- Key source areas inspected.
- Current global coverage state.
- Designs worth learning and the problems they solve, if any were documented, with links to their explanations.
- Known uninspected areas and unresolved assumptions.
- Suggested next study topics in priority order.
- Why those next topics are the highest-priority follow-ups.
