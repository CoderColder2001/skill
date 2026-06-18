---
name: "code-analyse"
description: "Guides source architecture analysis and docs. Invoke only when user runs /code-analyse or explicitly asks to use this skill."
---

# Code Analyse

Use this skill to perform evidence-based source architecture analysis and produce maintainable Markdown documentation.

## Invocation Rules

- Invoke this skill only when the user explicitly runs `/code-analyse` or clearly asks to use the source analysis skill.
- Do not automatically invoke the full analysis workflow for ordinary source questions, bug fixes, small explanations, file-specific changes, or local refactors.
- If the user asks for a narrow answer after invoking this skill, keep the workflow scoped to that topic while preserving the documentation rules below.

## Language Rules

- Default to Simplified Chinese for user-facing messages and generated Markdown documentation.
- Preserve source identifiers, file paths, package names, command names, framework names, APIs, and quoted code in their original language.
- Use another language only when the user explicitly requests it or when updating an existing document that already has a clear language convention.

## Scope Resolution

Before analyzing source files or writing documents, determine and state the analysis scope.

- If the user does not specify a module, directory, package, or topic, treat the request as a repository-wide analysis.
- If the user specifies a module, directory, package, feature, workflow, or entrypoint, treat the request as module-scoped analysis.
- For module-scoped analysis, inspect the requested scope plus its direct upstream callers, downstream dependencies, public interfaces, configuration, tests, and runtime wiring when they are needed to explain the module accurately.
- If the requested scope is ambiguous and materially affects the result, ask one concise clarification question before continuing.
- Record the scope in `code-analyse-docs/project-architecture.md` and every affected topic document using a clear `Analysis scope` section.
- Do not present module-scoped findings as repository-wide conclusions.

## Progress Reporting

During analysis, send concise progress updates to the user. Each substantial phase should include:

- `当前进度`: what has been completed and what is being inspected next.
- `当前发现`: concrete source-backed facts discovered so far.
- `建议下一步`: the next useful analysis action and why it matters.

Use progress reporting especially after scope resolution, entrypoint discovery, major flow tracing, document creation or update, and final review.

## Core Principles

- Read relevant source files before writing or updating any document.
- Base conclusions on concrete files, symbols, entrypoints, configuration, tests, and runtime wiring.
- Avoid unsupported assumptions. If evidence is incomplete, state the uncertainty explicitly.
- Prefer incremental updates when documentation already exists; do not regenerate duplicate documents.
- Write analysis documents to `code-analyse-docs/` by default unless the user explicitly requests another output directory.
- Keep `code-analyse-docs/project-architecture.md` as the central overview, navigation map, and reading-order index.

## Analysis Workflow

1. Resolve and report the analysis scope.
2. Establish the project or module overview first.
3. Identify language, package layout, build scripts, configuration files, commands, generated artifacts, and test structure relevant to the scope.
4. Locate core entrypoints such as CLI commands, app bootstrap files, servers, workers, plugins, routes, task runners, or exported public APIs.
5. Identify the architecture and framework/runtime model before writing detailed documents:
   - Architecture view: layers, module boundaries, dependency direction, ownership, core abstractions, and runtime topology.
   - Framework/runtime view: framework conventions, lifecycle hooks, plugin systems, configuration loading, routing, dependency injection, build/runtime integration, and extension points.
   - Execution view: important call chains from entrypoint to orchestration layer, domain logic, persistence, external integrations, and error handling.
   - Data/state view: state ownership, data flow, caches, persistence, events, concurrency, lifecycle, and invalidation.
   - Integration view: external services, SDKs, generated artifacts, protocols, runtime capabilities, and unresolved external dependencies.
6. Trace the most important execution flows with concrete file and symbol references.
7. Identify module boundaries by ownership, public interfaces, dependency direction, state ownership, and file layout.
8. Identify cross-cutting mechanisms such as state flow, event buses, hooks, middleware, caching, logging, telemetry, auth, feature flags, configuration, concurrency, and lifecycle management.
9. Then create or update topic documents for deep dives into individual modules, mechanisms, workflows, or integration points.
10. Finally, add relationship details across documents: collaboration points, call chains, data flow, state transitions, ownership boundaries, and sequence diagrams where useful.

## External Dependency Handling

- If a module, protocol, data source, generated artifact, runtime capability, SDK behavior, or implementation detail appears to depend on another project or repository, pause that portion of analysis and ask the user for the relevant local path or repository location.
- If the user provides the path, inspect that source before making conclusions about the dependency.
- If the user cannot provide the path, document the item as an `unresolved assumption`, explain what is known from the current repository, and avoid inventing missing details.

## Document Outputs

By default, create or update all analysis documents under `code-analyse-docs/`. If the user requests a different output directory, use that directory consistently and apply the same structure.

### project-architecture.md

Create or maintain `code-analyse-docs/project-architecture.md` as the primary entry point. Recommended structure:

- Analysis scope.
- Project purpose and scope.
- Repository layout and responsibility map.
- Architecture and framework overview.
- Build, run, test, and generated-file overview.
- Core entrypoints and startup sequence.
- Main execution flows.
- Key modules and ownership boundaries.
- State flow and cross-cutting systems.
- External dependencies and unresolved assumptions.
- Documentation map with recommended reading order.
- Next topics to analyze.

The body of `project-architecture.md` must be organized in the same order a reader should consume the documentation. The document must include a directory tree ordered by recommended reading sequence, for example:

```text
code-analyse-docs/
  project-architecture.md        # Start here
  query-state-machine.md         # Then read topic docs in this order
  session-memory.md
  tool-system.md
```

### Topic Documents

Create dedicated Markdown documents under `code-analyse-docs/` for detailed analysis of modules or mechanisms. Use concise kebab-case names that describe the topic, such as:

- `query-state-machine.md`
- `session-memory.md`
- `tool-system.md`
- `compact-conversation.md`
- `runtime-bridge.md`

Recommended structure for each topic document:

- Analysis scope.
- Purpose and when the mechanism is used.
- Source files and symbols inspected.
- Architecture position and framework/runtime role.
- Responsibilities and boundaries.
- Important data structures, state ownership, and lifecycle.
- Main control flow or sequence diagram.
- Interactions with other modules.
- Edge cases, failure modes, and unresolved assumptions.
- Links back to `code-analyse-docs/project-architecture.md`, previous and next documents in the reading order, and related topic documents.

Each topic document must answer these questions with source-backed evidence:

- Where does this module or mechanism sit in the overall architecture?
- Which framework, runtime, lifecycle, or convention does it rely on?
- Who calls it, what does it call, and what public interfaces or extension points does it expose?
- Who owns its state and how does data move through it?
- Which conclusions are verified from source, and which remain unresolved assumptions?

## Reading Order Rules

- The reading order in `project-architecture.md` is the canonical order for all generated analysis documents.
- The directory tree, documentation map, body section order, and topic-document previous/next links must stay consistent.
- For repository-wide analysis, start with `project-architecture.md`, then arrange topic documents from broad architectural foundations to specific mechanisms and workflows.
- For module-scoped analysis, start with the scoped overview, then order documents by dependency and execution flow: entrypoint or caller, target module, downstream dependencies, cross-cutting mechanisms, and unresolved external dependencies.
- When adding, removing, renaming, or reordering topic documents, update every affected reading-order reference.

## Size and Splitting Rules

- Keep every document focused on one overview, module, mechanism, or flow.
- Split a planned document when it covers multiple independent mechanisms, becomes difficult to scan, or duplicates another topic.
- Use `code-analyse-docs/project-architecture.md` as the index instead of turning it into a long deep-dive document.
- Prefer several coherent topic documents over one oversized file.

## Incremental Update Rules

- Before creating new documentation, check whether `code-analyse-docs/project-architecture.md` and related topic documents already exist.
- Update existing documents when a topic is already covered and the new analysis refines or corrects it.
- Create a new topic document only when it represents a distinct module, mechanism, flow, or integration point.
- When adding or changing a topic, update the architecture overview, reading-order tree, cross-document links, and module collaboration notes.
- Preserve useful existing content unless the source evidence shows it is outdated or incorrect.

## Final Review

Before finishing, review all affected analysis documents and check for:

- Contradictions between overview and topic documents.
- Repeated explanations that should be consolidated or cross-linked.
- Ambiguous terminology or inconsistent module names.
- Stale links, missing backlinks, and broken reading order.
- Mismatches between directory tree order, documentation map order, body section order, and previous/next links.
- Missing `Analysis scope` sections or module-scoped findings presented as repository-wide conclusions.
- Missing architecture, framework/runtime, execution, data/state, or integration views.
- Missing relationships between modules, data flow, state ownership, or execution flow.
- Unresolved assumptions that need user-provided external paths.

After the review, polish `code-analyse-docs/project-architecture.md` so it remains the main entry point, includes the recommended reading-order directory tree, and accurately links every new or updated topic document.

## Completion Report

When the analysis task is complete, report:

- Current completion status.
- Documents created or updated.
- Key source areas inspected.
- Analysis scope and known uninspected areas.
- Important unresolved assumptions or external paths still needed.
- Suggested next analysis topics in priority order.
- Why those next topics are the highest-priority follow-ups.
