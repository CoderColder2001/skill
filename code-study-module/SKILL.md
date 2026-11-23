---
name: code-study-module
description: Use only when the user explicitly invokes `code-study-module` or `$code-study-module` to study a named code module and produce a source-linked architecture/code-reading document. Covers upstream ownership, lifecycle, data/config provenance, and behavior boundaries as relevant. Do not activate for ordinary code analysis, debugging, implementation, or requests to review/edit the skill itself.
---

# Code Study Module

Turn a specified module's source into a document that helps a reader explain how it works. Lead with the reader's question, build the shortest true input-to-output chain, and expand only where evidence or the reading purpose requires it.

Use Simplified Chinese for the document and final response unless the user requests another language. Preserve code identifiers, filenames, config keys, and quoted source strings.

## Start with available context

- **Subject:** A concrete module, class, file, or mechanism must be named in the request or established conversation. If none is identifiable, ask for the subject and stop; do not explore the repository broadly to invent one.
- **Focus:** Use the user's motivation when supplied. Otherwise proceed with a general architecture/code-reading study. Do not require an optional focus question to be answered.
- **Destination:** Use the requested Markdown path, or `<project-root>/docs/code-study-module/<module-name>.md`. If given a directory, append `<module-name>.md`. Derive a short filename from the subject when it contains path separators or several words. State the chosen path and begin; do not ask the user to reconfirm a default or an already supplied path.
- **Ambiguity:** Perform a narrow lookup first. If several candidates remain materially different and context cannot select one, show the candidates and ask one targeted question. Do not silently combine unrelated modules with the same name.

Detect the project root with `git rev-parse --show-toplevel`, falling back to the current working directory. Follow an explicitly supplied repository location. Read applicable repository and subtree instructions; use `rg` and `rg --files` for discovery.

Keep the investigation read-only until writing the requested document. Do not run builds, tests, app launches, migrations, or network operations unless the user requests them or repository instructions require them for this output. Use normal file-edit discipline for documentation, preserve unrelated user edits, and do not change source code as part of the study.

## Research around one question

### 1. Locate the subject and choose the narrative

Search the literal name, naming variants, registrations, routes, config keys, and public interfaces. Confirm the real entry point before deciding what the subject is. A name presented as a module may actually identify a protocol, adapter, registry, or migration path.

Choose the primary question and use this router as guidance, not a mandatory chapter template:

| Subject | Primary question and useful order |
|---|---|
| Concept / protocol / mechanism | What does it mean here? Definition and common confusion → data forms → lifecycle → implementation and boundaries. |
| Request / execution chain | How does input reach output? Entry → ordered handoffs → state evolution → branches/failures → completion. |
| Business / runtime module | Where does it sit and what does it own? Product position → upstream owner → entry → core flow → outputs. |
| UI child / component | Who owns it and how does state become UI? Product surface → parent → lifecycle → state sources → rendering/interaction. |
| Store / registry / cache | Who owns state and how does it enter and leave? Scope → creation → writers/gates → transformations → readers → cleanup. |
| Adapter / provider / integration | Which contract does it bridge? Both sides → ownership → mapping → fallback/errors → lifetime. |
| Router / policy / strategy | How is the decision made? Inputs → precedence → branches → fallback → final consumer. |
| Migration / V1–V2 | Which version runs? Define labels → traffic routing → behavioral differences → compatibility/exit conditions. |
| Small single-file module | What does it do and where is it called? Purpose → caller/entry → core logic → relevant edge cases. |

For a compound topic, choose one protagonist and embed the other concerns as supporting chains. Split documents only when requested or when a single narrative would be confusing; explain the reason. Prefer one document by default.

Add a compact code organization map only when multiple packages/components need orientation. Link directories and distinguish contracts, implementation, resources, generated/legacy surfaces, and relevant modification boundaries. Place the map after the primary answer; omit it for a small subject. Do not open with an unexplained directory inventory.

### 2. Establish ownership and the shortest mainline

Trace from the nearest meaningful product surface, route, task, or service through the parent/factory/registration that reaches the subject, then to its output. Continue upward only far enough to identify the visible owner and scope; do not trace every framework ancestor.

For each consequential handoff explain the trigger, caller/owner, method or contract, transferred value, and resulting state/output. Anchor decisions and edges to nearby source links with visible line numbers. A diagram is useful when it makes this chain easier to understand; it is not required for a trivial flow.

Define repository-specific version labels and jargon before relying on them. Separate what the subject implements from what a host, framework, remote service, or UI component supplies. Give external frameworks a short context capsule: what holds the subject, where it is registered, and which callback crosses the boundary.

### 3. Follow lifecycle and provenance where behavior depends on them

When meaningful, distinguish parent, module, child/output, and data lifetimes. Identify creation/registration, active callbacks, and exit/cleanup. Explain which values are captured once and which are read lazily on later calls. Do not infer cleanup merely because an object has a lifecycle hook.

Trace important values back to their request, config, service, or state source. If an output depends on a store, registry, cache, accumulator, index, queue, or context side channel populated across paths, read [derived-state tracing](references/derived-state.md). Apply its forward and reverse pass to state that changes the main output, a significant branch, lifetime, or the user's stated concern. A simple local variable does not need a separate provenance section.

Cover relevant fallback/error paths and feature/version gates alongside the mainline. Separate source facts from inference; record missing evidence explicitly instead of completing a chain from convention or names.

### 4. Bound the investigation

An item is important when it changes the answer to the primary question: output contents, route/branch selection, ownership/lifetime, or a behavior the user explicitly asks about.

- Follow supporting code until the input contract, owner, handoff, and output needed by the main subject are explained. Reuse that boundary instead of recursively studying the dependency.
- For prominent derived state, search the state symbol and related keys within the relevant module and its direct callers/producers. Cover each behaviorally distinct producer; group equivalent paths with a stated reason and source references.
- Stop expanding a branch when additional implementation detail would not change the reader's explanation. Put useful secondary inventories after the core narrative rather than giving them equal weight.
- Stop at an unavailable repository, generated implementation, runtime reflection boundary, or remote consumer when the actual implementation cannot be inspected. State the known contract, the unverified part, and its effect on the conclusion.
- Finish when the primary question, mainline, relevant branches/lifetimes, and important output provenance are supported, with remaining unknowns clearly bounded. Do not claim exhaustive coverage beyond the searches performed. If the user explicitly requests completeness, cover all relevant paths in the stated scope and disclose any gaps.

## Write and verify the document

The first substantive section should answer the primary question. Keep the core explanation readable without opening every source file. Use tables for ownership or lifecycle comparisons only when they help. Add a short source-linked reading order when the subject spans several files.

### Snapshot metadata

Include a compact snapshot block near the beginning:

- **Repository and scope:** repository/project identity, studied subject, and reading focus.
- **Revision:** current branch and full HEAD commit; state detached HEAD when applicable. For a non-Git directory, say so rather than inventing a revision.
- **Working tree:** whether studied source includes staged, unstaged, or untracked changes relative to HEAD. Identify relevant changed paths; do not dump unrelated changes. If status cannot be checked, mark it unknown.
- **Study date:** use the user's current date/timezone when available. State that claims and line numbers describe this local snapshot, including relevant uncommitted changes.

Collect metadata with read-only commands. If relevant source changes during the investigation, recheck affected claims and citations before delivery.

### Source links and evidence

Use the repository's working link convention. Otherwise, for a Markdown document saved in the repository, prefer links relative to that document:

```markdown
[PaymentRouter.kt](../../src/PaymentRouter.kt)（L42）
```

Use a filename and line next to the claim, not only in a detached source appendix. Link filenames mentioned in prose/tables and directories in navigation maps. Keep line numbers in visible text; put them in the target only when the target renderer supports that format. Follow the host app's file-link convention in chat.

Before delivery, resolve every local link relative to the document (or as an absolute path when used) and verify it exists. Recheck cited lines and symbols against the source: an existing file or in-range line number alone does not establish that it supports the claim. For out-of-repository dependencies, explain the boundary and use links supported by the actual environment.

### Final self-review

Review the result against these acceptance questions and fix failures:

1. Does the opening answer the selected question, with one clear protagonist and no unexplained jargon?
2. Can a reader follow the owner → entry → handoffs → output chain, including relevant decisions and failures?
3. Are meaningful lifecycle differences and important value/state sources explained, with no assumed producers, cleanup, or external behavior?
4. Do the snapshot and source citations match the inspected code, and are facts, inference, and coverage limits distinct?
5. Are navigation and reading order useful at this module's scale, without framework detours, repeated explanations, or irrelevant inventories?
6. Were the requested path, language, scope, and existing user edits respected? On revision, rewrite/remove stale sections instead of appending contradictory explanations.

## Delivery

Keep the final response brief: link the document, summarize what it explains, and state verification performed plus material unknowns. Mention that builds/tests were not run when relevant; do not imply runtime verification from source reading.
