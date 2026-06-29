---
name: "code-plan"
description: "Use only when the user explicitly invokes /code-plan before asking to create or modify code in a target project, or when an active /debug-review sequence is explicitly handed off into 修改方案设计."
---

# Code Plan

Use this skill for pre-coding review on implementation requests. Write a task-scoped spec into the target project before production code changes begin.

## Invocation Rules

- Invoke this skill when the user explicitly runs `/code-plan`.
- Also invoke this skill when the current thread is already inside an active `/debug-review` analysis sequence and the user explicitly agrees to enter 修改方案设计.
- Do not auto-trigger this skill for ordinary coding requests.
- After `/code-plan`, keep the thread in this workflow for the current implementation sequence unless the user clearly changes direction.
- If the user asks only conceptual or exploratory questions after invoking the skill, answer them directly and wait to write the spec until an actual implementation request appears.
- Do not start production code edits for a covered task until the spec has been written and shown to the user.
- Do not treat a vague bug conversation as a valid handoff. The debug-review path is valid only when the user clearly approves the move into 修改方案设计.

## Language Rules

- Default to Simplified Chinese for user-facing messages and generated Markdown documents.
- Preserve source identifiers, file paths, package names, command names, framework names, APIs, and quoted code in their original language.
- If the target project already has a strong document language convention and the user prefers it, follow that convention consistently.

## When the Spec Is Required

- `/code-plan` has already been invoked, or an active `/debug-review` sequence has been explicitly handed off into 修改方案设计.
- The user is now asking to create, modify, refactor, or repair code.
- The request is specific enough to identify a target project and implementation direction.

If the request is still ambiguous in a way that changes the project root, task scope, or module boundaries, ask one concise clarification question before writing the spec.

### Handoff Input From `debug-review`

When this skill is entered from `/debug-review`, carry forward the latest bug-analysis context before writing the spec. At minimum, treat the following as upstream planning input when they exist in the target project:

- `debug-review-docs/current-review.md`
- the latest file under `debug-review-docs/reviews/`
- the user's latest confirmed corrections or additions from the conversation

Use that material to shape the spec. Do not restart from a blank interpretation if the handoff context is already available.

## Output Location Rules

Write documentation into the project being modified, not into this skill repository.

Default structure inside the target project:

```text
code-plan-docs/
  current-spec.md
  specs/
    YYYY-MM-DD-<topic>.md
```

Rules:

- Create `code-plan-docs/specs/YYYY-MM-DD-<topic>.md` for the current task.
- Create or refresh `code-plan-docs/current-spec.md` as the stable entry point for the active spec.
- If `code-plan-docs/` already exists, update it incrementally instead of creating a parallel structure.
- Derive `<topic>` from the implementation request using concise kebab-case.

## Scope Rules

Keep the review scoped to the requested code change.

- Read the relevant modules before writing the spec.
- Inspect direct callers, downstream dependencies, interfaces, tests, configuration, and runtime wiring only when they affect the requested change.
- Stay lighter than a repository-wide architecture analysis.
- If evidence is incomplete, write the uncertainty into the spec instead of inventing details.
- Do not quietly widen the task into unrelated refactoring.

## Workflow

1. Determine that the conversation has moved from discussion into implementation.
2. Resolve the target project root and the task slug.
3. If this run came from `/debug-review`, read the latest `debug-review-docs/current-review.md` and the latest dated review before inspecting implementation surfaces.
4. Inspect the code, tests, config, and module boundaries relevant to the requested change.
5. Write the spec to `code-plan-docs/specs/YYYY-MM-DD-<topic>.md`.
6. Refresh `code-plan-docs/current-spec.md`.
7. Summarize the spec for the user and ask for confirmation or requested changes.
8. Wait for the user's response before starting production code edits.
9. If the implementation scope changes materially later, update the spec before continuing.

## Required Spec Structure

Every spec must include these sections in this exact order:

1. `## 当前编码意图`
2. `## 预期目标与完成标准`
3. `## 当前相关模块现状`
4. `## 本次涉及改动模块`
5. `## 新模块架构设计陈述`
6. `## 风险与待确认项`
7. `## 不在本次范围内的内容`

### Section Guidance

#### `## 当前编码意图`

Restate the requested implementation task in engineering terms. Clarify what behavior should change and why.

#### `## 预期目标与完成标准`

List completion conditions that can later be checked through tests, behavior checks, or user-facing outcomes.

#### `## 当前相关模块现状`

Summarize the current behavior of the relevant modules using source-backed observations. Mention responsibilities, key interfaces, and constraints that shape the implementation.

When the task may require a new module, explicitly identify which existing module is currently overloaded, why its current boundary is no longer holding, and what kind of future change pressure is causing the boundary to fail.

#### `## 本次涉及改动模块`

List the modules, files, packages, or surfaces likely to change. For each one, explain why it is in scope.

#### `## 新模块架构设计陈述`

If a new module is needed, explain:

- what responsibility the new module owns
- what it deliberately does not own
- which current module or file is overloaded today
- what concrete pressure makes the old placement insufficient
- the proposed file or directory location
- which existing modules call it or depend on it
- which dependencies it may take on
- what interface or API shape it should expose
- what the caller chain looks like after the change
- why creating this module is cleaner than extending an existing one

If no new module is planned, state that directly and explain why the existing boundaries are sufficient.

#### `## 风险与待确认项`

Call out uncertainty, coupling risk, migration risk, behavior ambiguity, test gaps, dependency concerns, or user decisions that may still affect the implementation.

#### `## 不在本次范围内的内容`

List the adjacent improvements or refactors that might be tempting but should stay out of the current task.

## Current-Spec File Rules

`current-spec.md` should help a reader land on the active task quickly. Keep it short and stable.

Recommended structure:
- Title naming the active task
- Link or pointer to the dated spec file
- One-paragraph summary of the current implementation goal

Use `templates/current-spec-template.md` as the default shape for this file.

## Boundary With Other Skills

- Use `brainstorming` for broader design discovery across product or workflow ambiguity.
- Use `writing-plans` after the spec is accepted and a detailed implementation plan is needed.
- Use `test-driven-development` when actual implementation begins.
- Use `requesting-code-review` and `receiving-code-review` after code exists and review feedback enters the loop.
- Use `code-analyse` when the user wants broader repository or module architecture documentation rather than a task-scoped pre-coding spec.
- Use `debug-review` first when the user still needs a revisable bug-analysis document before deciding on a repair direction. Enter `code-plan` from there only after explicit approval of 修改方案设计.

## Quality Bar

Before considering the spec ready:

- confirm the target project path is correct
- confirm the spec path is correct
- confirm every required section exists
- confirm claims about current modules are grounded in inspected source
- confirm the listed scope is narrow enough for the requested task
- confirm any new-module recommendation has clear boundaries and dependency direction
- confirm any new-module recommendation names the overloaded current module, the proposed path, and the post-change caller chain

## Template

Use `templates/spec-template.md` as the default structure for the dated task spec and `templates/current-spec-template.md` for `current-spec.md`.

If the user or project needs a concrete example, refer to:

- `examples/spec-example.md`
- `examples/current-spec-example.md`
