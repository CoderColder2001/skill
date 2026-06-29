# `code-review` Skill Design

## Summary

This design adds a new skill named `code-review` for review-first analysis of uncommitted code changes. The skill is aimed at finding change-propagation bugs introduced by partial modifications, such as missing field initialization, inconsistent contract updates, omitted branch handling, stale React hook dependencies, and backend path drift.

The workflow is intentionally narrow: inspect the current uncommitted diff, read a small set of directly relevant files, run a common checklist plus a small number of language/framework packs, and write a Markdown review report with evidence-backed findings and concrete repair suggestions. The skill is review-only in v1 and does not edit production code.

## Context

The existing `coding-review` skill in this repository is a pre-implementation spec workflow that writes task-scoped specs before code changes begin. It is useful when the user wants to clarify what should be built before implementation.

This new `code-review` skill serves a different point in the workflow:

- the code changes already exist locally
- the user wants to inspect the current diff
- the main risk is not broad architecture ambiguity but incomplete propagation of a concrete change

Typical examples include:

- adding a new optional field like `valid?: boolean` but failing to initialize or serialize it everywhere
- extending an enum or status while leaving some `switch` branches, mappers, or UI paths unchanged
- modifying a React callback but forgetting a dependency and introducing stale closure behavior
- changing a Node service path while forgetting retry, audit, or async job variants

## Goals

- Add a new skill at `/Users/bytedance/workspace/skill/code-review`.
- Review the current uncommitted changes by default, including staged and unstaged diffs.
- Focus on correctness risks caused by incomplete propagation of a change across related code paths.
- Produce a concise conversational summary plus a full Markdown report saved into the target repository.
- Keep findings split into high-confidence issues versus lower-confidence risks that need human confirmation.
- Support a general core review flow plus a first batch of targeted packs for TypeScript/JavaScript, React hooks, and Node service code.

## Non-Goals

- Do not turn into a general style review or naming review tool.
- Do not rewrite or patch code in v1.
- Do not perform repository-wide architecture review unless the user explicitly asks for that broader scope.
- Do not invent testing frameworks, commands, or validation patterns that are not evidenced in the repository.
- Do not treat missing tests as a standalone defect unless there is concrete repository evidence that a related test asset should have been updated.

## Trigger Model

The skill uses a mixed trigger model.

### Explicit trigger

The skill should trigger when the user explicitly invokes `/code-review`.

### Automatic trigger

The skill may also trigger when the user clearly asks to inspect the current code diff or current uncommitted changes, such as:

- review current diff
- check my uncommitted changes
- help inspect this code change for omissions
- review these unstaged or staged modifications

### Do not auto-trigger for

- broad brainstorming about how a future feature should work
- generic implementation planning
- conceptual questions about design patterns with no current code changes under review
- generic requests to “make code better” without a concrete diff-focused review request

## Default Review Target

Unless the user specifies otherwise, the review target is the current repository's uncommitted changes:

1. staged diff
2. unstaged diff

If there are no uncommitted changes, the skill should say so plainly and ask for a different review target instead of inventing scope.

## Output Model

The output is dual-path by default.

### In conversation

Provide a concise summary of:

- review scope
- highest-priority findings
- major risks needing human confirmation

### In the target repository

Write a full Markdown report into:

```text
code-review-docs/
  reviews/
    YYYY-MM-DD-HHmm-<topic>.md
  current-review.md
```

Rules:

- Save the current full report under `code-review-docs/reviews/`.
- Refresh `code-review-docs/current-review.md` as the stable entry point to the latest review.
- Derive `<topic>` from the dominant change intent in concise kebab-case.
- If the repository already has a similar review-docs structure, extend it incrementally rather than creating a competing structure.

## Review Boundary

This skill is intentionally review-only in v1.

- Inspect the diff and relevant nearby files.
- Explain problems and suggest fixes.
- Do not patch code automatically.
- Do not stage or commit anything.

If the user later wants the fixes implemented, that should happen outside this skill's review report step.

## Confidence Model

All findings must be classified into one of two buckets.

### High-confidence issues

Use this only when the reviewer has both:

1. change evidence: where the current diff introduced or modified behavior
2. omission evidence: another related place that should plausibly have changed but did not

Each high-confidence issue should name both kinds of evidence directly.

### Suspected risks / manual confirmation

Use this for lower-confidence cases where the signal is real enough to mention but the reviewer cannot responsibly claim a defect with current evidence.

This lets the skill surface meaningful concerns without turning into a noisy guess generator.

## Review Workflow

1. Resolve the target repository and confirm the review target is the current uncommitted diff unless the user overrides it.
2. Read staged and unstaged diffs.
3. Identify the main changed entities and surfaces, such as fields, DTOs, interfaces, hooks, services, jobs, clients, schemas, or status values.
4. Read the common checklist.
5. Select and read the relevant targeted packs using explicit routing rules.
6. Read only the nearby upstream and downstream files needed to verify propagation or omissions.
7. Write the Markdown report.
8. Summarize the result in conversation.

The workflow should stay diff-first and evidence-first. It should not widen into a full repository sweep.

## Pack Strategy

The skill should not implement each pack as a separate top-level skill. Instead, `code-review` owns the routing and loads internal reference packs.

Recommended structure:

```text
code-review/
  SKILL.md
  templates/
    review-report.md
    current-review.md
  references/
    pack-selection.md
    common-checklist.md
    packs/
      typescript-javascript.md
      react-hooks.md
      node-service.md
  evals/
    evals.json
```

This keeps invocation stable while still allowing specialized review logic.

## Pack Selection Rules

The common checklist is always loaded.

Then load one or more targeted packs based on evidence from the diff and nearby files.

### `typescript-javascript`

Load when the diff touches TypeScript or JavaScript files, runtime object construction, type/interface definitions, DTOs, mappers, serializers, parsers, validators, or enum/union expansions.

### `react-hooks`

Load when the diff touches React components, custom hooks, or hook-dependent logic, especially `useEffect`, `useMemo`, `useCallback`, subscriptions, async state updates, or form state synchronization.

### `node-service`

Load when the diff touches backend service flows, jobs, queues, cron tasks, retry behavior, external clients, audit paths, metrics, or async side-effect chains in a Node-based service.

## Required Report Structure

Every review report should include these sections in this order:

1. `## 审查范围`
2. `## 变更摘要`
3. `## 本次启用的检查 pack`
4. `## 高置信问题`
5. `## 疑似风险 / 待人工确认`
6. `## 测试与验证缺口`
7. `## 建议补充的回归场景`
8. `## 未覆盖范围`

### Section guidance

#### `## 审查范围`

State whether the review covered staged diff, unstaged diff, or both. List the main files or surfaces inspected.

#### `## 变更摘要`

Restate what this change appears to be doing in engineering terms, using evidence from the diff rather than user intention alone.

#### `## 本次启用的检查 pack`

List the common checklist and any targeted packs that were loaded, plus a short reason for each one. This makes pack usage auditable.

#### `## 高置信问题`

Each issue should include:

- short title
- evidence location in the changed code
- omission location or inconsistency evidence
- why this is a correctness problem
- suggested fix direction

#### `## 疑似风险 / 待人工确认`

List lower-confidence concerns that deserve targeted manual checking but lack enough evidence to be called a defect.

#### `## 测试与验证缺口`

This section is evidence-bound.

- If the repository contains related tests, fixtures, mocks, builders, or established test conventions, comment on whether the current change appears to have updated them consistently.
- If such evidence does not exist, explicitly state that test-synchronization review was skipped because no relevant test assets were found.
- Do not claim “missing tests” as a defect without repository evidence.

#### `## 建议补充的回归场景`

Suggest concrete scenarios only when the repository provides enough evidence about how validation is normally done. These can be behavior scenarios rather than framework-specific prescriptions.

Do not invent commands, frameworks, or test styles.

#### `## 未覆盖范围`

State which adjacent areas were not reviewed so the report is not misread as a repository-wide conclusion.

## Common Checklist Scope

The common checklist should focus on change-propagation risks that occur across languages and business domains:

- newly added fields not propagated through constructors, defaults, mappers, serializers, validators, fixtures, or tests
- expanded enum or status values not propagated through branch handling, mapping tables, permission checks, display logic, or export logic
- API and data-contract drift between producer and consumer
- create/update/retry/batch/rollback paths drifting apart
- persistence, cache, and derived-view updates becoming inconsistent
- logging, metrics, tracing, audit, or failure handling drifting behind behavior changes

## Targeted Pack Scope

### TypeScript / JavaScript

Focus on:

- optional field propagation gaps
- spread and destructuring omissions
- enum or union exhaustiveness gaps
- runtime validator drift from type definitions
- shared type changes consumed unevenly across boundaries
- `undefined` / `null` semantic drift

### React Hooks

Focus on:

- missing hook dependencies
- stale closures in callbacks and effects
- missing cleanup for timers, listeners, or subscriptions
- async result races that overwrite newer state
- drift between source state and derived state
- form initialization, reset, submit, or dirty-state handling not updated for new fields

### Node Service

Focus on:

- service/job/queue/cron path drift
- retry behavior around non-idempotent operations
- timeout, cancel, rollback, or partial failure handling gaps
- audit, metrics, event publish, or alerting omissions
- configuration-flag and rollout path inconsistencies
- DTO, repository, and external-client propagation gaps

## Testing Guidance

This skill should not pretend to know how to test a project from first principles.

Testing commentary must be evidence-based:

1. inspect nearby test files and naming patterns
2. inspect repository-level test tooling if visible
3. inspect fixtures, mocks, builders, and test utilities related to the changed area

Rules:

- If related test assets exist, review whether they were updated consistently with the change.
- If no related test assets or test conventions can be found, skip test-synchronization review and say so explicitly.
- If the repository shows a broader test system but this diff does not touch visible validation assets, mention it only as a lower-confidence verification gap, not as a confirmed defect.
- Never invent a test framework, command, or concrete test implementation style without repository evidence.

## Quality Bar

Before finalizing a review report, confirm:

- the review really focused on the current uncommitted diff unless otherwise requested
- the report names which packs were used and why
- each high-confidence issue includes both change evidence and omission evidence
- low-confidence concerns are kept out of the high-confidence section
- test-related commentary is grounded in repository evidence
- the report stays scoped to the impacted surfaces rather than drifting into unrelated cleanup advice

## Validation Plan

Create evals that verify:

- common propagation omission detection for a newly added field
- React hook dependency or stale-closure detection
- Node async path or retry-path inconsistency detection
- mixed cases where both common and targeted packs should be activated
- reports correctly skip or downgrade test commentary when test evidence is missing

## Open Decisions Resolved

- Trigger model: mixed explicit plus clear diff-review auto-trigger
- Output model: conversational summary plus repository Markdown report
- Default behavior: review-only, no code edits
- Confidence model: high-confidence findings plus suspected risks
- Test handling: evidence-based only, skip when no relevant test assets exist
- Pack strategy: internal reference packs, not separate top-level skills
