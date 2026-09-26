# Test resource manifest

All live checks use publisher-controlled, public EIP resources. The contract
does not accept report documents supplied by a bundle author.

| Fixture | Primary | Commit-pinned fallback | Expected use |
|---|---|---|---|
| EIP-1559 | `https://eips.ethereum.org/EIPS/eip-1559` | `https://raw.githubusercontent.com/ethereum/EIPs/{commit}/EIPS/eip-1559.md` | Final Core EIP with dependencies 2718 and 2930 |
| EIP-2718 | `https://eips.ethereum.org/EIPS/eip-2718` | `https://raw.githubusercontent.com/ethereum/EIPs/{commit}/EIPS/eip-2718.md` | Dependency fixture |
| EIP-2930 | `https://eips.ethereum.org/EIPS/eip-2930` | `https://raw.githubusercontent.com/ethereum/EIPs/{commit}/EIPS/eip-2930.md` | Dependency fixture; itself requires 2718 and 2929 |
| EIP-2929 | `https://eips.ethereum.org/EIPS/eip-2929` | `https://raw.githubusercontent.com/ethereum/EIPs/{commit}/EIPS/eip-2929.md` | Transitive dependency fixture |
| EIP-7701 | `https://eips.ethereum.org/EIPS/eip-7701` | `https://raw.githubusercontent.com/ethereum/EIPs/{commit}/EIPS/eip-7701.md` | Withdrawn negative fixture |

## Pinning procedure

Before live E2E, choose one full 40-character commit from the official
`ethereum/EIPs` repository that contains all fixture files. Record that exact
commit, retrieval UTC time, source digests, contract address, and transaction
hashes in `STUDIONET_E2E.md`. Never use `master`, a tag, or a shortened SHA.

The two URLs are independent delivery origins for the same canonical EIP
repository, not independent publishers. A `MATCH` receipt therefore means the
two canonical representations agree; it is not a claim of multi-publisher
corroboration.

## Test-only failures

Source outage, malformed output, oversized content, prompt injection, conflict,
and truncation are tested through gltest mocks. Mock fixtures are clearly
labelled and are not presented as live web evidence.
