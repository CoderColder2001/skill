# Code Review Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `code-review` skill that reviews the current uncommitted diff, routes through common and targeted review packs, and writes a Markdown report into the target repository without modifying production code.

**Architecture:** Reuse the repository's existing skill layout from `code-plan/` for the top-level structure, then add `references/pack-selection.md`, `references/common-checklist.md`, targeted pack documents, and review report templates. Keep the skill review-only, evidence-based, and explicit about confidence levels and test-evidence boundaries.

**Tech Stack:** Markdown skill files, JSON eval definitions, shell verification commands

---

### Task 1: Scaffold the Skill Directory and Shared Artifacts

**Files:**
- Create: `code-review/SKILL.md`
- Create: `code-review/README.md`
- Create: `code-review/USAGE.md`
- Create: `code-review/evals/evals.json`
- Create: `code-review/templates/review-report.md`
- Create: `code-review/templates/current-review.md`
- Create: `code-review/references/pack-selection.md`
- Create: `code-review/references/common-checklist.md`
- Create: `code-review/references/packs/typescript-javascript.md`
- Create: `code-review/references/packs/react-hooks.md`
- Create: `code-review/references/packs/node-service.md`

- [ ] **Step 1: Create the directory tree**

Run:

```bash
mkdir -p code-review/evals code-review/templates code-review/references/packs
```

Expected: the `code-review/` directory tree exists and is ready for file creation.

- [ ] **Step 2: Draft the stable artifact list**

Mirror the durable pieces already used by `code-plan/`:

```text
code-review/
  SKILL.md
  README.md
  USAGE.md
  evals/evals.json
  templates/review-report.md
  templates/current-review.md
  references/pack-selection.md
  references/common-checklist.md
  references/packs/typescript-javascript.md
  references/packs/react-hooks.md
  references/packs/node-service.md
```

- [ ] **Step 3: Verify the directory tree exists**

Run:

```bash
find code-review -maxdepth 3 -type d | sort
```

Expected: the four directories `code-review`, `code-review/evals`, `code-review/templates`, and `code-review/references/packs` are listed.

### Task 2: Write the Main Skill Contract

**Files:**
- Create: `code-review/SKILL.md`
- Reference: `docs/superpowers/specs/2026-06-22-code-review-design.md`
- Reference: `code-plan/SKILL.md`

- [ ] **Step 1: Write the frontmatter and trigger contract**

The skill must encode:

- mixed trigger model
- explicit `/code-review` path
- diff-review auto-trigger path for clearly phrased review requests
- review-only boundary
- Simplified Chinese default for user-facing output

- [ ] **Step 2: Write the review workflow**

Include the exact sequence:

1. resolve repo and uncommitted diff target
2. read staged and unstaged diff
3. identify changed entities
4. load `common-checklist`
5. select targeted packs using `references/pack-selection.md`
6. inspect only nearby dependent files
7. write `code-review-docs/reviews/YYYY-MM-DD-HHmm-<topic>.md`
8. refresh `code-review-docs/current-review.md`
9. summarize findings in conversation

- [ ] **Step 3: Encode the confidence and testing rules**

The skill must explicitly say:

- high-confidence issues need both change evidence and omission evidence
- lower-confidence concerns belong in `疑似风险 / 待人工确认`
- test commentary is evidence-based only
- if no relevant test assets exist, skip test-synchronization review and say so

- [ ] **Step 4: Verify the main contract mentions all required sections**

Run:

```bash
rg -n "审查范围|变更摘要|本次启用的检查 pack|高置信问题|疑似风险 / 待人工确认|测试与验证缺口|建议补充的回归场景|未覆盖范围" code-review/SKILL.md
```

Expected: all required report section names are found.

### Task 3: Write the Reference Packs and Templates

**Files:**
- Create: `code-review/references/pack-selection.md`
- Create: `code-review/references/common-checklist.md`
- Create: `code-review/references/packs/typescript-javascript.md`
- Create: `code-review/references/packs/react-hooks.md`
- Create: `code-review/references/packs/node-service.md`
- Create: `code-review/templates/review-report.md`
- Create: `code-review/templates/current-review.md`

- [ ] **Step 1: Write `pack-selection.md`**

Document routing cues from diff evidence:

- TS/JS files, DTOs, interfaces, validators, enums -> `typescript-javascript`
- React components, custom hooks, `useEffect`, `useMemo`, `useCallback` -> `react-hooks`
- services, jobs, queues, retries, clients, audit paths -> `node-service`

- [ ] **Step 2: Write `common-checklist.md`**

Cover cross-language propagation failures:

- field propagation
- contract drift
- branch and path drift
- enum/state expansion gaps
- persistence/cache inconsistency
- error-handling and observability drift
- test asset synchronization only when evidence exists

- [ ] **Step 3: Write the targeted packs**

Each pack should state:

- when it applies
- what to inspect
- what not to over-claim
- example omission patterns

- [ ] **Step 4: Write the report templates**

`review-report.md` must contain the exact final report headings in order. `current-review.md` must provide a stable pointer to the latest dated report.

- [ ] **Step 5: Verify the template headings**

Run:

```bash
sed -n '1,220p' code-review/templates/review-report.md
```

Expected: the template shows the eight required report headings in the correct order.

### Task 4: Add Eval Prompts and Basic Usage Docs

**Files:**
- Create: `code-review/evals/evals.json`
- Create: `code-review/README.md`
- Create: `code-review/USAGE.md`

- [ ] **Step 1: Draft realistic eval prompts**

Include at least:

- a field propagation omission case
- a React hooks dependency or stale-closure case
- a Node service path drift case
- a mixed case requiring both common and targeted packs
- a case with no relevant test assets where test-sync review should be skipped

- [ ] **Step 2: Write `README.md`**

Explain:

- what the skill is for
- when it triggers
- where reports land
- what its review-only boundary is
- what packs are bundled in v1

- [ ] **Step 3: Write `USAGE.md`**

Provide explicit `/code-review` examples plus natural-language auto-trigger examples.

- [ ] **Step 4: Verify the eval JSON is valid**

Run:

```bash
python3 -m json.tool code-review/evals/evals.json >/dev/null
```

Expected: command exits successfully with no output.

### Task 5: Run Local Verification and Final Review

**Files:**
- Review: `code-review/`
- Review: `docs/superpowers/specs/2026-06-22-code-review-design.md`

- [ ] **Step 1: Verify file presence**

Run:

```bash
find code-review -maxdepth 3 -type f | sort
```

Expected: all planned files are present.

- [ ] **Step 2: Verify key trigger language and confidence rules**

Run:

```bash
rg -n "/code-review|auto-trigger|高置信|疑似风险|测试与验证缺口|skip test-synchronization" code-review/SKILL.md code-review/references/common-checklist.md code-review/references/pack-selection.md
```

Expected: the contract language for triggers, confidence, and testing is present.

- [ ] **Step 3: Do a manual consistency pass**

Check that:

- `SKILL.md` matches the design doc
- pack names match between `SKILL.md`, `pack-selection.md`, and the report template
- output directories use `code-review-docs/` consistently
- no file claims the skill edits production code

- [ ] **Step 4: Summarize the result for the user**

Report:

- the files created
- the trigger model
- the report output model
- the verification commands run
- any remaining gap, especially that full subagent-based baseline/eval loops were not yet run in this session
