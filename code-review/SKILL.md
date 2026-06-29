---
name: "code-review"
description: "Use when the user explicitly invokes /code-review, or clearly asks to review current staged or unstaged code changes for遗漏、影响面不一致、契约漂移、hook 依赖问题或服务链路漏改."
---

# Code Review

Use this skill to review the current uncommitted code diff for change-propagation bugs and incomplete follow-through. Produce an evidence-based Markdown report in the target repository and a concise summary in conversation.

## Invocation Rules

- Trigger this skill when the user explicitly runs `/code-review`.
- Also trigger this skill when the user clearly asks to review the current code diff, current uncommitted changes, staged changes, unstaged changes, or a just-made local modification set for omissions or inconsistencies.
- Do not auto-trigger this skill for broad product brainstorming, implementation planning, generic architecture discussion, or vague “make this code better” requests that are not diff-focused.
- If there is no clear current review target, ask one concise clarification question.

## Language Rules

- Default to Simplified Chinese for user-facing messages and generated Markdown reports.
- Preserve source identifiers, file paths, package names, command names, framework names, APIs, and quoted code in their original language.
- If the target repository already has a strong document language convention and the user prefers it, follow that convention consistently.

## Default Review Target

Unless the user explicitly chooses another scope, review the current repository's uncommitted changes in this order:

1. staged diff
2. unstaged diff

If there are no uncommitted changes, say so directly and ask the user for another review target. Do not invent scope.

## Output Location Rules

Write documentation into the repository being reviewed, not into this skill repository.

Default structure inside the target repository:

```text
code-review-docs/
  current-review.md
  reviews/
    YYYY-MM-DD-HHmm-<topic>.md
```

Rules:

- Create `code-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md` for the current review.
- Create or refresh `code-review-docs/current-review.md` as the stable entry point for the latest review.
- Derive `<topic>` from the dominant change intent using concise kebab-case.
- If `code-review-docs/` already exists, update it incrementally instead of creating a parallel structure.

## Review Boundary

This skill is review-only in v1.

- Inspect the diff and directly relevant nearby files.
- Explain problems and suggest repair directions.
- Do not patch production code.
- Do not stage, commit, or revert changes.
- If the user later wants fixes implemented, treat that as a separate step after the review report.

## Core Review Goal

Prioritize correctness risks caused by partial modifications across related code paths. Typical examples:

- a new field is added but not propagated through constructors, defaults, mappers, serializers, validators, fixtures, or test helpers
- an enum or status is extended but some branches, mapping tables, or UI flows stay on the old set
- a React callback or effect changes but the dependency list does not follow
- a backend service path changes but retries, jobs, audit logging, metrics, or alternate paths drift behind

## Confidence Rules

Every finding must go into one of two buckets.

### High-confidence issues

Use this only when both of the following are present:

1. **Change evidence**: where the current diff introduced or changed behavior
2. **Omission evidence**: a related place that should plausibly have changed but did not

Each high-confidence issue must name both kinds of evidence directly.

### Suspected risks / manual confirmation

Use this for lower-confidence concerns where the signal is real enough to mention but current evidence is insufficient to call it a defect.

Do not mix these two classes together. Keep noisy guesses out of the high-confidence section.

## Testing Rules

Do not pretend to know how a project should be tested from first principles.

- Only make concrete testing comments when the repository contains relevant test files, fixtures, mocks, builders, test utilities, or visible test conventions near the changed area.
- If relevant test assets exist, review whether they were updated consistently with the current change.
- If no relevant test assets or test conventions can be found, skip test-synchronization review and say so explicitly.
- If the repository shows a broader test system but the current diff does not touch visible validation assets, mention this only as a lower-confidence verification gap.
- Do not invent test frameworks, commands, or implementation styles without repository evidence.
- Do not convert a generic desire for “more tests” into a finding. Testing commentary must stay tied to the changed behavior and to concrete nearby assets or conventions.

## Workflow

1. Resolve the target repository and confirm the review target is the current uncommitted diff unless the user overrides it.
2. Read staged and unstaged diffs.
3. Identify the main changed entities and surfaces, such as fields, DTOs, interfaces, hooks, services, jobs, clients, schemas, or status values.
4. Read `references/common-checklist.md`.
5. Read `references/pack-selection.md` and select the relevant targeted packs.
6. Read only the nearby upstream and downstream files needed to verify propagation or omissions.
7. Write the report to `code-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md`.
8. Refresh `code-review-docs/current-review.md`.
9. Summarize the most important findings in conversation.

Stay diff-first and evidence-first. Do not widen into a full repository sweep.

## False-Positive Guardrails

Be especially careful around situations that look suspicious at first glance but may still be correct.

- If a helper, builder, or mapper already forwards unknown or optional properties through a generic mechanism such as `...overrides`, do not call it a high-confidence omission unless the current change proves that the mechanism no longer preserves the relevant field.
- If a field is absent only from a default object literal but the code path still accepts and forwards caller-supplied values correctly, treat the issue as a lower-confidence semantics question unless the repository shows a clear default-value convention that is now broken.
- If the repository has tests somewhere in the project but none are clearly related to the changed area, do not infer that this specific diff should have touched them.
- Prefer “this may need confirmation” over “this is broken” whenever the evidence depends on unwritten project conventions rather than concrete code behavior.

## Required Report Structure

Every review report must include these sections in this exact order:

1. `## 审查范围`
2. `## 变更摘要`
3. `## 本次启用的检查 pack`
4. `## 高置信问题`
5. `## 疑似风险 / 待人工确认`
6. `## 测试与验证缺口`
7. `## 建议补充的回归场景`
8. `## 未覆盖范围`

### Section Guidance

#### `## 审查范围`

State whether the review covered staged diff, unstaged diff, or both. List the main files or surfaces inspected.

#### `## 变更摘要`

Restate what this change appears to be doing in engineering terms using source evidence from the diff and nearby files.

#### `## 本次启用的检查 pack`

List `common-checklist` and every targeted pack used for this review, plus a short reason for each.

#### `## 高置信问题`

For each issue, include:

- short title
- change evidence
- omission evidence or inconsistency evidence
- why this is a correctness problem
- suggested fix direction

#### `## 疑似风险 / 待人工确认`

List lower-confidence concerns that deserve targeted manual checking.

#### `## 测试与验证缺口`

- If relevant test assets exist, explain whether they stayed in sync with the current change.
- If no relevant test assets exist, say that test-synchronization review was skipped because no relevant assets were found.
- Do not present “missing tests” as a confirmed defect without repository evidence.

#### `## 建议补充的回归场景`

Suggest behavior scenarios only when the repository gives enough evidence about how validation is normally done. Keep suggestions concrete and evidence-based.

#### `## 未覆盖范围`

State which adjacent areas were not inspected so the report is not misread as a repository-wide conclusion.

## Pack Routing

Use `references/pack-selection.md` to decide which targeted packs to load. The common checklist is always loaded first.

The first v1 targeted packs are:

- `references/packs/typescript-javascript.md`
- `references/packs/react-hooks.md`
- `references/packs/node-service.md`

Only read the packs that are actually justified by the current diff and nearby files.

## Boundary With Other Skills

- Use `code-plan` when the user wants a pre-coding spec before implementation starts.
- Use `brainstorming` for broader design discovery across ambiguous product or workflow requests.
- Use `writing-plans` after a spec is accepted and a detailed implementation plan is needed.
- Use `test-driven-development` when actual implementation begins.
- Use `requesting-code-review` or `receiving-code-review` when the workflow is about post-implementation review exchange rather than local diff inspection.
- Use `code-analyse` when the user wants repository or module architecture documentation instead of a diff-centered review report.

## Quality Bar

Before finalizing a review report, confirm:

- the review really focused on the intended diff target
- the report names which packs were used and why
- every high-confidence issue contains both change evidence and omission evidence
- lower-confidence concerns stay out of the high-confidence section
- test commentary is grounded in repository evidence
- the report stays scoped to impacted surfaces instead of drifting into unrelated cleanup advice

## Template

Use `templates/review-report.md` as the default structure for the dated review report and `templates/current-review.md` for `current-review.md`.
