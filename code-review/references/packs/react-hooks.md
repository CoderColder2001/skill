# React Hooks Pack

Use this pack when the diff touches React components, custom hooks, or hook-driven UI state.

## Focus Areas

### 1. Dependency Drift

Check `useEffect`, `useMemo`, and `useCallback` whenever the underlying logic changes.

Common misses:

- callback reads a new prop or state value but dependency list stays old
- effect depends on a changed function or field without updating dependencies
- memoized value now depends on a new input that was not added to the dependency array

### 2. Stale Closures

When callbacks, effects, async handlers, or event listeners capture values, check whether they can observe stale state or props after the change.

Common misses:

- async completion handler writes using old state assumptions
- event listener closes over outdated filters or flags
- queued callback still references pre-change form or selection state

### 3. Cleanup and Subscription Symmetry

Inspect whether the change affects:

- timers
- listeners
- subscriptions
- abort/cancel handling

Common misses:

- setup changed but cleanup path did not
- new dependency means a subscription is recreated but old instance is not cleaned up
- request cancellation or stale response suppression no longer matches the new flow

### 4. Derived State and Form State

When fields are added or form structure changes, inspect:

- initialization
- reset
- submit
- dirty-state detection
- validation triggers
- derived display state

Common misses:

- field exists in UI but not in initial state
- reset path returns to old shape
- submit payload omits the new value
- dirty check or validation ignores the new field

## Reporting Guidance

- A hook warning is not enough by itself; prefer source-backed reasoning tied to the changed logic.
- If the repository already uses lint rules for hook dependencies, do not assume lint has full semantic coverage.
- When evidence is partial, downgrade to `疑似风险 / 待人工确认` instead of overstating certainty.
