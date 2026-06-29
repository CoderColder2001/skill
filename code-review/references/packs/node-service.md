# Node Service Pack

Use this pack when the diff touches Node-based service orchestration, integrations, async jobs, or reliability-sensitive backend paths.

## Focus Areas

### 1. Path Consistency Across Service Variants

Check whether the change updated all relevant execution paths, such as:

- request path
- service helper path
- background job path
- retry path
- batch path
- rollback or compensation path

Common misses:

- request flow updated but background job still builds the old payload
- main path changed but retry path still uses outdated assumptions

### 2. Idempotency and Retry Safety

When retry behavior or failure handling is involved, inspect whether the changed action is still safe to repeat.

Common misses:

- duplicate side effects on retried write operations
- audit/event/notification path triggered multiple times
- retry logic unaware of new partial-success state

### 3. Timeout, Cancellation, and Partial Failure

Check whether new behavior also updated:

- timeout handling
- cancellation or abort propagation
- partial failure recording
- rollback / compensation logic

Common misses:

- change adds a new downstream call but failure aggregation stays old
- partial success now possible but error path still assumes all-or-nothing

### 4. Integration Surface Drift

Inspect consistency between:

- service DTOs
- repository models
- external client payloads
- event publish payloads

Common misses:

- one layer adds a field but another strips it
- service branch changed but emitted event stayed old
- client request builder stayed on legacy parameter semantics

### 5. Observability and Audit Symmetry

When important backend behavior changes, inspect whether:

- metrics
- structured logs
- audit records
- alerts
- event publish paths

still represent the new flow accurately.

Focus on diagnosability and operational correctness, not logging style.

## Reporting Guidance

- Prefer concrete drift between service paths over broad architecture advice.
- If the codebase includes feature flags, rollout branches, or config gates, inspect both enabled and disabled paths when the current diff touches them.
- Downgrade findings when evidence is incomplete, especially around external side effects you cannot fully see from local source.
