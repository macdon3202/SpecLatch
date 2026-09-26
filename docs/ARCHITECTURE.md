# Architecture and claim boundary

## Claim

`SPEC_READY` means only that every item in a sealed manifest has canonical EIP
metadata matching the configured policy and that all publisher-declared EIP
dependencies occur in the same verified manifest.

It does not authorize shutdown, proxy upgrades, fund movement, release, or
consumer deprecation. It does not establish source-code migration.

## Separation of concerns

1. The author builds and seals the immutable manifest.
2. A distinct wallet initiates independent validator retrieval for each item.
3. Consensus returns only bounded facts and content digests.
4. Deterministic contract code computes the terminal gate state.
5. The UI waits for execution success and then re-reads contract state.

There is no owner, deployer role, arbitrary evidence URL, uploaded report, or
administrator override.

## Bounded execution

- 64 bundles maximum per deployment.
- 8 requirements maximum per bundle.
- 60,000 characters maximum per source representation.
- 8 normalized dependency IDs maximum per receipt.
- 255 receipt revisions maximum per slot.
- Exact enums and exact JSON keys.
- Both source routes are exact-bound to one EIP ID; fallback is commit-pinned.

## Failure semantics

- Retrieval/schema/model failure: `SOURCE_UNAVAILABLE`, retry allowed.
- Source disagreement: `CONFLICT`, terminal requirement.
- Non-final specification: bundle `BLOCKED/NON_FINAL_EIP`.
- Missing declared dependency: bundle `BLOCKED/MISSING_DEPENDENCY`.
- Incomplete receipt set: bundle `UNRESOLVED/UNCHECKED_REQUIREMENT`.

