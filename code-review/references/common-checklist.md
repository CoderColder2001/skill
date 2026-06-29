# Common Checklist

Use this checklist for every `code-review` run before any targeted pack.

The goal is to find correctness bugs caused by partial modification of a change across related code paths. Stay close to the current diff and gather nearby evidence instead of drifting into repository-wide cleanup.

## 1. Field and Data Shape Propagation

Check whether newly added or changed fields were propagated consistently through:

- constructors and object initialization
- defaults and fallback values
- clone / merge / spread paths
- mappers, adapters, and DTO translation layers
- serializers and parsers
- validators and guard logic
- fixtures, mocks, builders, and test helpers if they exist

Look for mismatches between static shape changes and runtime object handling.

## 2. Contract Drift Across Boundaries

Check whether the change introduced drift between:

- producer and consumer
- frontend and backend payload assumptions
- repository models and service DTOs
- event payload definitions and event consumers
- cache shapes and read paths

High-confidence issues need both a changed contract and a nearby consumer or producer still operating on the old contract.

## 3. Path and Branch Drift

Check whether the change updated only one path while leaving parallel paths behind, such as:

- create vs update
- sync path vs async path
- main flow vs retry / rollback / compensation flow
- user-facing path vs export / batch / background path
- success path vs failure path

Treat this as a likely source of high-value findings.

## 4. Enum, Status, and Branch Expansion

When statuses, modes, enums, or unions change, inspect:

- `switch` or conditional branches
- mapping tables
- permission checks
- display logic
- export logic
- filtering and aggregation logic

Look for silent default branches that may now swallow a new case.

## 5. Persistence, Cache, and Derived State

Check whether the change impacts:

- persistence read/write paths
- repository queries
- cache keys or cache invalidation
- derived projections or denormalized views
- computed summaries or secondary indexes

Look for one side of the read/write flow moving while the other side stays on the old assumptions.

## 6. Error Handling and Observability

Check whether new or changed behavior also updated:

- error propagation
- logs
- metrics
- trace context
- audit records
- alerting or event publish paths

Do not report style-only logging preferences. Focus on correctness and diagnosability gaps caused by the change.

## 7. Test Synchronization

This section is evidence-bound.

Only perform test-synchronization review when the repository gives concrete signals such as:

- nearby test files
- fixtures, mocks, builders, or factories
- visible test naming conventions
- obvious test utilities related to the changed area

If such evidence exists:

- check whether those assets stayed consistent with the current change
- report concrete mismatches as high-confidence issues only when the mismatch is clear
- if a helper still transparently forwards caller-supplied fields through `...overrides` or an equivalent mechanism, do not treat lack of an explicit default property as a confirmed defect unless project evidence shows the default is semantically required

If such evidence does not exist:

- skip this check
- state explicitly in the final report that no relevant test assets were found

Do not turn “no tests were added” into a defect without repository evidence.

## Output Discipline

- Keep findings tied to the current diff.
- Every high-confidence issue must cite both change evidence and omission evidence.
- Lower-confidence concerns belong in `疑似风险 / 待人工确认`.
- Ignore style nits, naming preferences, and unrelated cleanup opportunities unless they directly affect correctness for this change.
- When a generic forwarding mechanism or optional-field convention may already preserve correctness, prefer a cautious lower-confidence note over a definitive omission claim.
