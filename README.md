# SpecLatch

SpecLatch is a permissionless GenLayer dApp that seals an EIP manifest, creates
one independently verified receipt per EIP, and deterministically issues a
`SPEC_READY` certificate only when canonical metadata and declared dependencies
satisfy the bundle policy.

> `SPEC_READY` is deliberately narrow. It does **not** prove that a consumer
> migrated, that code was deployed, or that an upgrade is safe to execute.

## Why this is not self-authored evidence

Users cannot upload reports or choose arbitrary URLs. The contract constructs
both routes from an EIP number and a full 40-character commit:

- `https://eips.ethereum.org/EIPS/eip-{id}`
- `https://raw.githubusercontent.com/ethereum/EIPs/{commit}/EIPS/eip-{id}.md`

The AI consensus layer extracts a bounded metadata schema. The contract—not the
prompt—then checks `Final`, `Standards Track`, policy category, source agreement,
and complete dependency membership.

## Permission model

- The deployer is not stored and receives no administrator capability.
- Wallet A creates, appends, and seals a bundle.
- Any different wallet B verifies its requirements and finalizes the gate.
- Any reviewer can create a fresh bundle and reproduce the complete flow.

## Architecture

```text
Draft manifest (Wallet A)
   -> immutable seal + digest
   -> per-EIP canonical receipt (Wallet B, one transaction each)
   -> deterministic dependency/policy gate
   -> SPEC_READY | BLOCKED | UNRESOLVED
```

Receipts are append-only by `(bundle, slot, revision)`. Only source-unavailable
requirements may be retried. Sealed manifests and terminal bundle decisions are
immutable; changes use a new bundle with `supersedes`.

## Local verification

```bash
python -m pytest -q
cd frontend
npm ci
npm test
npm run build
```

Current verification: **12 contract tests and 5 frontend transaction-state
tests passing**.

## Studionet deployment

Current deployment:
[`0x2435Fdb65cFDA8e36A3A22CEaaf7f573Dc0Ad70b`](https://explorer-studio.genlayer.com/address/0x2435Fdb65cFDA8e36A3A22CEaaf7f573Dc0Ad70b)

Live application: [https://spec-latch.pages.dev/](https://spec-latch.pages.dev/)

1. Deploy `contracts/spec_latch.py` on GenLayer Studionet with the main wallet.
2. Put the returned address in `frontend/.env.production` as
   `VITE_CONTRACT_ADDRESS`.
3. Use secondary wallet A to create/add/seal a bundle.
4. Use secondary wallet B to verify/finalize it.
5. Record finalized transaction URLs and post-write readbacks in
   `docs/STUDIONET_E2E.md`.

Do not present a transaction as successful merely because it is finalized. The
execution result must be successful and the frontend must read the resulting
contract state back after finality.

## Repository map

- `contracts/spec_latch.py` — Intelligent Contract
- `tests/test_spec_latch.py` — local and adversarial contract suite
- `frontend/` — release-console UI and finality reconciliation
- `docs/TEST_RESOURCE_MANIFEST.md` — exact source policy and fixtures
- `docs/TEST_MATRIX.md` — expected branch coverage
- `docs/STUDIONET_E2E.md` — live evidence ledger (filled only with real receipts)
