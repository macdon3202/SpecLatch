# UI transaction and state reconciliation

Verified against the production frontend build on 2026-09-26.

## Transaction acceptance

The frontend accepts a write only when:

1. the transaction reaches `FINALIZED`;
2. the actual leader receipt does not contain an execution error; and
3. the relevant contract state is read again after finality.

Cancelled `idle` validators after quorum are not treated as failed transaction
execution. This Studionet receipt shape has a dedicated regression test.

## Live readback parity

Production preview loaded contract
`0x2435Fdb65cFDA8e36A3A22CEaaf7f573Dc0Ad70b` directly from Studionet.

| Bundle | On-chain readback | UI display | Result |
|---|---|---|---|
| 3 | `SPEC_READY / ALL_SPEC_REQUIREMENTS_SATISFIED`, 4/4 verified | same state, reason, manifest digest, wallets and four requirement rows | PASS |
| 4 | `BLOCKED / MISSING_DEPENDENCY`, 1/1 verified | same state, reason, manifest digest and counts | PASS |

The UI does not infer these states locally. It renders `get_bundle` and
`get_requirement` readbacks from the deployed contract.

## Automated frontend tests

- malformed wallet transaction hash rejected;
- finalized leader execution error rejected;
- finalized successful leader receipt accepted;
- idle validator cancellation ignored after quorum;
- transaction hash normalization verified.
