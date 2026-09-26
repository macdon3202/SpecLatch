# Test matrix

| Branch | Expected outcome | Automated |
|---|---|---|
| Four Final Core EIPs with transitive dependency closure | `SPEC_READY` | yes |
| Withdrawn EIP | `BLOCKED/NON_FINAL_EIP` | yes |
| EIP-1559 without 2718/2930 | `BLOCKED/MISSING_DEPENDENCY` | yes |
| Canonical representations conflict | `BLOCKED/SOURCE_CONFLICT` | yes |
| Source unavailable then restored | append-only retry revision | yes |
| Author attempts own source check | revert | yes |
| Mutation after seal | revert | yes |
| Duplicate EIP | revert | yes |
| Mutable/short commit reference | revert | yes |
| Finalize before checking | revert | yes |
| Terminal replay | revert, state unchanged | yes |
| Malformed/unsorted/unknown AI output | fail closed | yes |
| Finalized receipt with execution error in UI | rejected | yes |
| Successful finality | accepted then state readback | yes |
