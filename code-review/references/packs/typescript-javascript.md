# TypeScript / JavaScript Pack

Use this pack when the diff changes TypeScript or JavaScript code in ways that may cause runtime propagation drift.

## Focus Areas

### 1. Static Shape vs Runtime Shape

When `type`, `interface`, payload, or DTO shapes change, check whether runtime object construction changed too.

Common misses:

- type updated but object literal initialization stayed old
- optional field added but spread/clone path drops it
- serializer or parser still emits or expects the old shape

### 2. Spread and Destructuring Omissions

Inspect `...spread`, destructuring, `pick`, `omit`, or mapper code when a field is added or renamed.

Common misses:

- `const { a, b } = obj` now silently ignores new data needed downstream
- mapper returns a shape missing the newly added property
- shallow clone path preserves only legacy keys

Counter-signal:

- if a builder or helper uses `...overrides` or another transparent forwarding pattern that still carries the new field end-to-end, do not overstate the absence of an explicit property literal

### 3. Enum and Union Expansion

When enums, literal unions, or mode strings change, inspect:

- branch exhaustiveness
- mapping tables
- display labels
- validators
- downstream consumers using older literal sets

Do not assume the type checker caught everything, especially when runtime string comparisons or default branches exist.

### 4. Runtime Validators and Guards

Check whether zod/yup/custom validators or hand-written guards still reflect the old assumptions.

Common misses:

- type accepts new field but validator strips or rejects it
- runtime guard still assumes field is absent or mandatory in the old way
- parser defaulting logic conflicts with new optionality

### 5. Nullability and Optionality Drift

Pay attention when a change introduces or alters:

- `undefined`
- `null`
- optional properties
- default values

Common misses:

- UI or service path treats `undefined` and `false` the same
- old fallback logic now masks a newly significant value
- consumer assumes field always exists because static type locally widened without runtime support

## Reporting Guidance

- Prefer concrete propagation findings over general type-safety advice.
- If a mismatch is only theoretical and you cannot point to a real runtime path, downgrade it to `疑似风险 / 待人工确认`.
- Pair this pack with `react-hooks` or `node-service` when the diff crosses UI or backend service boundaries.
- Distinguish between “the new field is dropped” and “the default-value convention for the new field is not yet explicit.” The first can be high-confidence; the second often cannot.
