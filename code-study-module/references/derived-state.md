# Derived-state tracing

Use this reference when a prominent output depends on state populated across multiple functions, callbacks, or components. Keep the analysis scoped to the main output, significant branches, lifetime, or the user's explicit concern.

## Two provenance questions

- **Value provenance:** Which request, config, service result, model, or event supplies each important value?
- **Container provenance:** Who creates and owns the state holder, at what scope, and through which paths do values enter and leave?

Knowing the final JSON shape does not answer either question by itself.

## Trace forward, then back from output

1. Locate creation and owner. Record the key, scope, and lifetime: request, page, session, process, subscription, or another source-backed scope.
2. Find behaviorally distinct writers/registration points and their gates. Search the state symbol, wrapper methods, and protocol/config keys; a type definition or one representative writer is insufficient.
3. Follow transformation, aggregation, replacement, indexing, or placeholder generation. Explain the relation between the original value and any reference that replaces it.
4. Find the reader/materializer and final placement: response envelope, stream/chunk, UI model, queue, cache, event, or other consumer.
5. Reverse-trace the important output from its materializer to backing state and producers. Reconcile this with the forward chain; investigate discrepancies instead of describing only the happy path.
6. Check removal, overwrite/collision, ordering, and missing-reference behavior when they can affect the output or the user's concern. Distinguish observed code behavior from an undocumented concurrency or downstream contract.

Useful search targets include assignment, append/add, registration, Store/Load, put/get, replacement, conversion, materialization, serialization, and their local equivalents. Adapt the search to the actual implementation; do not assume naming conventions cover all paths.

## Coverage and stopping rule

Follow all behaviorally distinct producers found in the relevant module and its direct callers/producers. Equivalent paths may be grouped, with their shared behavior and source references stated. Expand the search when an unresolved output or reference points outside that scope; stop when the contract is established or the implementation is unavailable.

Do not claim “all writers” or “no cleanup” from one search. Describe the searched scope and say “not found in the inspected scope” where that is the actual evidence. An external consumer or dynamically injected implementation may remain unknown; explain how that limits the conclusion.

For simple state, a paragraph can close the loop. For complex state, a compact evidence table can help:

| Holder | Owner/scope | Writers and gates | Transformation | Materializer/sink | Lifetime and remaining uncertainty |
|---|---|---|---|---|---|

Do not mechanically turn every column into a chapter. Keep the reader's main question visible.
