# Pack Selection

Use this file after reading the current diff and `common-checklist`.

The common checklist is always loaded first. Then load only the targeted packs justified by current diff evidence.

## Routing Rule

1. Read staged and unstaged diff.
2. Identify the dominant changed entities and file types.
3. Match them to the smallest useful set of targeted packs.
4. Record the chosen packs and reasons in the final report under `## 本次启用的检查 pack`.

Do not load packs speculatively just because they exist.

## `typescript-javascript`

Load this pack when the diff or nearby files involve one or more of:

- `*.ts`, `*.tsx`, `*.js`, `*.jsx`
- `type`, `interface`, DTO, payload, mapper, adapter
- runtime object construction
- serializer, parser, validator
- enum or union expansion
- spread / destructuring based propagation

Typical trigger questions:

- Did a new field get added to a type but not to runtime object construction?
- Did a runtime validator stay on the old shape?
- Did enum expansion leave some consumers behind?

## `react-hooks`

Load this pack when the diff or nearby files involve one or more of:

- React components or custom hooks
- `useEffect`, `useMemo`, `useCallback`
- event listeners, timers, subscriptions
- async state updates
- forms or derived UI state

Typical trigger questions:

- Did effect or callback dependencies drift behind the changed logic?
- Did the change create a stale closure risk?
- Did a new field enter form state without updating initialize/reset/submit paths?

## `node-service`

Load this pack when the diff or nearby files involve one or more of:

- backend services
- jobs, queues, workers, cron tasks
- retries, timeouts, rollback, compensation
- external clients or integration adapters
- audit logs, metrics, event publish paths
- configuration flags or rollout branches

Typical trigger questions:

- Did one execution path change while retry, job, or audit paths stay behind?
- Did the change create idempotency or partial-failure risk?
- Did DTO, repository, and external client handling drift apart?

## Mixed Cases

It is normal to load more than one targeted pack when the diff crosses boundaries, for example:

- a React form change plus TypeScript DTO propagation
- a Node service change plus TypeScript contract drift

Keep the set small and justified. Prefer the minimum number of packs needed to explain the current risk surface.
