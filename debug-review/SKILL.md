---
name: "debug-review"
description: "Use only when the user explicitly invokes /debug-review to analyze a described bug in the current or specified target project, write revisable Markdown under debug-review-docs/, and hand off to code-plan only after the user explicitly agrees to enter 修改方案设计."
---

# Debug Review

Use this skill to analyze a described bug by tracing the relevant module, call path, data flow, and nearby configuration or tests, then write a revisable Markdown analysis report into the target repository. The output is a bug-analysis document, not a patch. Stay in analysis mode until the user explicitly agrees to enter `code-plan` for 修改方案设计.

## Invocation Rules

- Invoke this skill only when the user explicitly runs `/debug-review`.
- Do not auto-trigger this skill for ordinary bugfix requests, log explanation requests, diff reviews, or broad architecture discussion.
- After `/debug-review`, keep the thread in this workflow for the current bug-analysis sequence unless the user clearly ends the analysis, changes topic, or explicitly agrees to enter `code-plan`.
- If the user asks a narrow follow-up question while still inside the active `/debug-review` sequence, answer it inside this workflow instead of silently dropping the document contract.

## Language Rules

- Default to Simplified Chinese for user-facing messages and generated Markdown documents.
- Preserve source identifiers, file paths, package names, command names, framework names, APIs, and quoted code in their original language.
- If the target repository already has a clear document language convention and the user prefers it, follow that convention consistently.

## Default Target And Scope Resolution

- Default target: the current working repository.
- If the user explicitly provides another path, use that repository as the target.
- Treat the user-provided bug symptom as the entry signal, not as a confirmed root cause.
- If the symptom description is too thin to choose a module or path responsibly, ask one concise clarification question before widening the read scope.
- Keep the analysis task-scoped. Do not silently expand into repository-wide architecture documentation.

## Output Location Rules

Write documentation into the target repository, not into this skill repository.

Default structure inside the target repository:

```text
debug-review-docs/
  current-review.md
  reviews/
    YYYY-MM-DD-HHmm-<topic>.md
```

Rules:

- Create `debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md` for each material analysis or revision pass.
- Create or refresh `debug-review-docs/current-review.md` as the stable entry point for the latest active analysis.
- Derive `<topic>` from the bug symptom and dominant path in concise kebab-case.
- If `debug-review-docs/` already exists, update it incrementally instead of creating a competing structure.

## Core Analysis Goal

Prioritize evidence-backed reasoning from symptom to cause. Typical examples:

- a request path behaves differently from the user expectation because one mapper, validator, or serializer drops state
- a UI action reaches the wrong submit/reset path due to stale state wiring, effect timing, or branch drift
- a background job, retry path, or alternate service branch still uses old assumptions after a logic change elsewhere
- a feature flag, configuration value, or environment-specific branch changes behavior in only one slice of the flow

Use `references/analysis-checklist.md` before writing the report. Use `references/evidence-rules.md` whenever classifying conclusions.

## Evidence Rules

Every reasoned conclusion must go into one of two buckets.

### High-confidence reasons

Use this only when both are present:

1. **Symptom-alignment evidence**: the traced path or state transition can actually explain the bug symptom
2. **Source evidence**: concrete code, config, tests, or other repository evidence supports the conclusion

Name both kinds of evidence directly in the report. Avoid vague wording.

### Hypotheses / missing evidence

Use this when the signal is meaningful but current evidence is incomplete. Each hypothesis must explain:

- why it deserves attention
- what evidence is still missing
- the smallest next verification action that would confirm or rule it out

Do not upgrade a hypothesis into a high-confidence reason just because it sounds plausible.

## Revision Rules

This skill is designed to keep the analysis document alive across user feedback.

### Feedback in conversation

If the user adds logs, corrects assumptions, clarifies environment differences, or rejects part of the analysis in conversation, treat that as new analysis input.

### Feedback by document edits

If the user directly edits `debug-review-docs/current-review.md` or the latest dated review document, treat those edits as explicit human corrections. Read them before revising the report.

### Revision workflow

1. Read the latest `debug-review-docs/current-review.md` when it exists.
2. Read the latest dated review document when it exists.
3. Compare the current document state with the user’s new evidence or corrections.
4. Decide which conclusions should be kept, downgraded, removed, or strengthened.
5. Write a new dated review document.
6. Refresh `current-review.md`.

Preserve the distinction between facts, high-confidence reasons, and hypotheses throughout the revision flow.

## Workflow

1. Resolve the target repository and the active bug symptom.
2. Read `references/analysis-checklist.md`.
3. Read `references/evidence-rules.md`.
4. Inspect the entrypoint, directly relevant modules, and the smallest useful upstream/downstream path set.
5. Read nearby configuration or tests only when they materially affect the current bug explanation.
6. Write the report to `debug-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md` using `templates/review-report.md`.
7. Refresh `debug-review-docs/current-review.md` using `templates/current-review.md`.
8. Summarize the current findings in conversation.
9. If the user provides more evidence or edits the document, repeat the revision workflow.
10. If the user explicitly agrees to enter 修改方案设计, read `references/handoff-to-code-plan.md` and hand off to `code-plan`.

Stay symptom-first and evidence-first. Do not quietly turn this into a diff review or a general architecture survey.

## Required Report Structure

Every formal analysis report must include these sections in this exact order:

1. `## 审查范围`
2. `## Bug 表现与输入上下文`
3. `## 当前已确认事实`
4. `## 相关模块与关键链路`
5. `## 高置信原因判断`
6. `## 待确认假设与缺失证据`
7. `## 建议补充的验证动作`
8. `## 用户反馈与修订记录`
9. `## 后续入口`
10. `## 未覆盖范围`

### Section Guidance

#### `## 审查范围`

State the repository path, key modules or entrypoints inspected, and the main path boundary for this analysis round.

#### `## Bug 表现与输入上下文`

Record the user’s symptom description, reproduction hints, environment notes, and initial suspicions without upgrading them into conclusions.

#### `## 当前已确认事实`

List only source-backed facts that have been confirmed by code, config, tests, logs, or explicit user evidence.

#### `## 相关模块与关键链路`

Explain the key path from symptom to mechanism. Favor ordered descriptions such as `入口 -> 中间层 -> 下游依赖 / 状态流转`.

#### `## 高置信原因判断`

For each reason, include:

- short title
- symptom-alignment evidence
- source evidence
- why it explains the bug
- modules or surfaces likely to matter during repair

#### `## 待确认假设与缺失证据`

List promising but unconfirmed explanations. Keep them separate from confirmed reasons.

#### `## 建议补充的验证动作`

Suggest the smallest verification actions that would change confidence, such as checking one branch, confirming a config value, or adding one targeted log line.

#### `## 用户反馈与修订记录`

Summarize new user corrections, added evidence, or downgraded/strengthened conclusions since the previous round.

#### `## 后续入口`

Explicitly offer:

- continue revising the bug analysis
- enter `code-plan` only after the user explicitly agrees to enter 修改方案设计

#### `## 未覆盖范围`

Name adjacent areas you did not inspect so the report is not misread as a repository-wide conclusion.

## Handoff To `code-plan`

- Default behavior: stop at analysis.
- Only hand off when the user explicitly agrees to enter 修改方案设计.
- Before handoff, read `references/handoff-to-code-plan.md`.
- Carry forward `debug-review-docs/current-review.md`, the latest dated review, and the user’s latest confirmed corrections as the planning context.
- Do not start production code edits from this skill.

## Boundary With Other Skills

- Use `code-review` for diff-first inspection of current staged or unstaged changes.
- Use `code-analyse` for broader architecture documentation across a repository or module.
- Use `code-plan` only after the user explicitly approves moving from bug analysis into 修改方案设计.
- Use `brainstorming` for broader product or workflow exploration that is not yet anchored to a concrete bug symptom.

## Quality Bar

Before finalizing a report, confirm:

- the target repository is correct
- the analysis stayed inside the bug-relevant path boundary
- facts are separated from hypotheses
- every high-confidence reason names both symptom-alignment evidence and source evidence
- hypotheses name the missing evidence and next verification action
- `current-review.md` was refreshed
- the conversation summary tells the user how to revise the analysis or enter `code-plan`

## Templates

Use `templates/review-report.md` as the default shape for dated review documents and `templates/current-review.md` for `current-review.md`.
