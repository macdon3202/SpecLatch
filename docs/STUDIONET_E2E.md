# Studionet E2E evidence

Result: **PASS** on GenLayer Studionet. Machine-readable evidence is preserved
in [`studionet-e2e.json`](./studionet-e2e.json).

## Deployment and source binding

- Contract: [`0x2435Fdb65cFDA8e36A3A22CEaaf7f573Dc0Ad70b`](https://explorer-studio.genlayer.com/address/0x2435Fdb65cFDA8e36A3A22CEaaf7f573Dc0Ad70b)
- Contract version readback: `SPEC_LATCH_V1`
- Contract source SHA-256: `3A410ADA0CC07E038461D1DBA8FF93EBCE0C0B25C41229331366605F4FEC0655`
- Canonical repository commit: [`0b8184b1d6ed9fba836222684fd082b32782d4ef`](https://github.com/ethereum/EIPs/commit/0b8184b1d6ed9fba836222684fd082b32782d4ef)
- Claim boundary: `EIP_METADATA_ONLY_NOT_CONSUMER_MIGRATION`

## Wallet separation

- Deployer: deployment only; the contract stores no deployer/admin role.
- Bundle author: `0xFeD97e2aE1A8C1983b7cA206B3545e6A2c685E43`
- Independent auditor: `0xc67532aeF9D2879cBA9375a02E6217A3524657B8`

Roles are derived per bundle. Any reviewer can repeat the flow with two wallets.

## Happy path — bundle 3

Manifest: EIP-1559, EIP-2718, EIP-2930 and transitive dependency EIP-2929.

| Step | Transaction | Result |
|---|---|---|
| Create | [`0x8574…3ef3`](https://explorer-studio.genlayer.com/tx/0x8574c4828b610937aabb1da281d5e3d2f3a7ec340599039f0c1cdc2960aa3ef3) | SUCCESS |
| Add 1559 | [`0x6097…2c8d`](https://explorer-studio.genlayer.com/tx/0x6097530b919666a44572f1053afba4806f53eabf83b74dc4006876a441dc2c8d) | SUCCESS |
| Add 2718 | [`0x9b35…d055`](https://explorer-studio.genlayer.com/tx/0x9b3524e929f789f133e581772226e806a7919484923ab05128cf92930d54d055) | SUCCESS |
| Add 2930 | [`0x8f12…ff41`](https://explorer-studio.genlayer.com/tx/0x8f122116a76aee89071f9d2ab0f04781bea692ebdee28615aaef08fd04ecff41) | SUCCESS |
| Add 2929 | [`0xc227…3b19`](https://explorer-studio.genlayer.com/tx/0xc22763c565613480abcc2c3379d046cc1bed8aa73e2966b89b95d3be8dac3b19) | SUCCESS |
| Seal | [`0x35ee…c90e`](https://explorer-studio.genlayer.com/tx/0x35ee9c4e0f1bdcbbbd858f191db63331fca16b757679d2aeae60b55a78ecc90e) | SUCCESS |
| Verify 1559 | [`0x7895…2d0d`](https://explorer-studio.genlayer.com/tx/0x7895c127ed9c972c9adef8e7d63d868b9b6fd43b6634cee18293d2d981e72d0d) | SUCCESS |
| Verify 2718 | [`0x96b2…03bc`](https://explorer-studio.genlayer.com/tx/0x96b2a3755fe1ca6c49065be5bc1db82cbab33563baef3b600fa8f2820ac103bc) | SUCCESS |
| Verify 2930 | [`0xd276…3816`](https://explorer-studio.genlayer.com/tx/0xd27643c322693c0610c666574c607a01156434a3f2a9f56069a75c2c04b53816) | SUCCESS |
| Verify 2929 | [`0xffd1…51bc`](https://explorer-studio.genlayer.com/tx/0xffd1301b211884db9889ed17088622d36a98502617f55c359ff65da13a4d51bc) | SUCCESS |
| Finalize | [`0xcfc3…ece3`](https://explorer-studio.genlayer.com/tx/0xcfc3ea2b5cf5dc5d2734b1533b7f8a6d864cc147068ca3e02b0376afcaa4ece3) | SUCCESS |

Readback: `SPEC_READY / ALL_SPEC_REQUIREMENTS_SATISFIED`, checked `4 / 4`.
Manifest digest: `ecd16dbaa734127accd2d8ca5d37990ecd0af88f798d840a3476d89c9d69f504`.
Every requirement is `VERIFIED`, `Final`, `Standards Track`, `Core` and stores
primary, fallback and normalized fact digests.

## Adversarial role and replay checks

| Scenario | Transaction | Observed |
|---|---|---|
| Author verifies own bundle | [`0xd01f…49e6`](https://explorer-studio.genlayer.com/tx/0xd01f22e2f4af0bd7b141fe574c7fd163df1f1081bced962effb8bc4cd27549e6) | FINALIZED/ERROR; state unchanged |
| Repeat terminal finalize | [`0xcc45…89b1`](https://explorer-studio.genlayer.com/tx/0xcc45df8cbbfd2599c7f0e99d7956b9a66e8bf99e1601228759f9d894fb4789b1) | FINALIZED/ERROR; state unchanged |

## Failure path — bundle 4

This sealed manifest deliberately contains only EIP-1559. Its canonical receipt
declares `2718,2930`, which are absent.

| Step | Transaction | Result |
|---|---|---|
| Create | [`0x509c…420f`](https://explorer-studio.genlayer.com/tx/0x509c3793338f279285163ee066f08c46771b52d5fa586d0821b8c003dae7420f) | SUCCESS |
| Add 1559 | [`0x7089…cb5d`](https://explorer-studio.genlayer.com/tx/0x7089b5dfde7b53256262ba76bf294879c26c1c4d789f23872aba63f3090bcb5d) | SUCCESS |
| Seal | [`0x99dd…4bbc`](https://explorer-studio.genlayer.com/tx/0x99ddf9d6d1e8945a1bf75774171f05c6737ef9da6c6ddf72bc610ef07d294bbc) | SUCCESS |
| Verify | [`0xe509…8b07`](https://explorer-studio.genlayer.com/tx/0xe50972dafdd16e93bea627d13b028db83d2d39897a65849842736bc778bc8b07) | SUCCESS |
| Finalize | [`0xc8e2…056d`](https://explorer-studio.genlayer.com/tx/0xc8e23d1919831465b03dccca39f4cc4a681d8617b0422da98e2f32f76660056d) | SUCCESS |

Readback: `BLOCKED / MISSING_DEPENDENCY`. A successful source receipt therefore
does not bypass deterministic policy enforcement.

## Live-discovered transitive dependency

Bundle 2, containing only EIP-1559, 2718 and 2930, was correctly blocked because
canonical EIP-2930 additionally requires EIP-2929. The happy fixture was expanded
instead of weakening the gate. Bundle 2 remains on-chain as adversarial evidence.
