---
status: stable
phase: 0
gate: Gate 0
recorded: 2026-08-18
---

# Gate 0 — closure evidence

ADR-KEM-001 closes Gate 0 when **every consumer validates against a tagged
release**. This records that, per consumer, with what was actually run.

The tag is **`v0.2.1`**. `v0.1.0` and `v0.2.0` remain published and immutable;
`v0.2.0`'s provisioning shape is superseded by ADR-KEM-008 and its version
declaration was inconsistent, which is what `v0.2.1` corrects.

## What each consumer validated

| Repo | Vendored | Verification | Result |
| --- | --- | --- | --- |
| `karyalay-mail-infra` | 12 files | `npm run test:contracts` | 9 checks, 0 failures |
| `karyalay-mail` | 14 files | `php artisan test --testsuite=Contract` | 13 tests, 0 failures |
| `karyalay-webmail` | 6 files | `pnpm run contracts:verify` | pin OK, client current |
| `karyalay-mail-ops` | 9 files | `go test ./internal/contracts/` | 5 tests, 0 failures |

Each consumer records the tag, the **annotated tag object**, the commit, and a
**SHA-256 per vendored file**. Each fails on a hand edit, on a moved tag, and on
a file pinned without a manifest entry stating why it is vendored.

## The transport deviation, stated plainly

No repository in this programme has a git remote. The tag therefore cannot be
fetched by URL, and every pin resolves through a sibling clone recorded as
`source.kind: local-clone`.

This is a deviation, not a workaround, and it does not weaken what the pin rule
protects. Immutability here is enforced by the per-file digest, which holds
whichever transport delivers the bytes. When the remote exists, one field
changes in each pin file; if a digest then differs, the tag moved, and that is
the finding rather than something to re-pin around.

**Gate 0 is closed on validation. It is not closed on distribution** — no
consumer outside this machine can fetch the tag, and that remains the
outstanding owner action.

## Three findings surfaced by closing it

**1. `v0.2.0` declared two different versions of itself.** Six artifacts said
`0.2.0`; `observability/telemetry-contract-v1.yaml` and
`dns/domain-record-contract-v1.yaml` still said `0.1.0`. Both are hand-authored
from prose, so they sat outside the regeneration stage, and the version check
read only OpenAPI `info.version` — no stage compared an artifact's self-declared
version against the release it shipped in. The number had **eight sources of
truth**. Fixed in `v0.2.1`: one source, a stamping step inside `derive`, and a
check that fails if fewer than six artifacts are inspected.

**2. ADR-KEM-008 Amendment 1 item 1 is live in the published tag.**
`DesiredStateResourceType` is lower_snake with ten values;
`ProvisioningOperation.resource_type` is UPPER with six. `dkim_key`/`DKIM` and
`filter_set`/`FILTER` are the same concept spelled twice, and **`alias`,
`group`, `restriction` and `organisation` cannot be named in a provisioning
operation at all** — Repo 1 can ask for an alias and there is no operation shape
to report on it. A test in `karyalay-mail-infra` now pins the gap to exactly
what the ADR recorded, so closing or widening it fails and forces the ADR to
move with the contract. **This needs an owner ruling.**

**3. `desired_status` has no enumerated vocabulary in either specification.** It
ships grammar-constrained. Fixtures asserting a rejected unknown status would be
asserting behaviour the contract does not specify.
