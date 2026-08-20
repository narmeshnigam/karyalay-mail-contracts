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

---

## Distribution closure — 2026-08-20

**All five repositories green on GitHub Actions in the same round.** This is the
first time it has happened, and it is the condition ADR-KEM-001 names that the
2026-08-18 entry could not satisfy: that entry closed the gate *on validation*,
with every pin resolving through a sibling clone on one machine.

Twenty-six of twenty-six jobs, on runners that had never seen this code:

| Repository | Run | Jobs |
| --- | --- | --- |
| `karyalay-mail-contracts` | [32313013165](https://github.com/narmeshnigam/karyalay-mail-contracts/actions/runs/32313013165) | 2 success, 1 skipped (`tag-is-immutable`, tag-triggered) |
| `karyalay-mail-infra` | [32313009001](https://github.com/narmeshnigam/karyalay-mail-infra/actions/runs/32313009001) | 4 success |
| `karyalay-mail` | [32316896963](https://github.com/narmeshnigam/karyalay-mail/actions/runs/32316896963) | 7 success, **including the container build** |
| `karyalay-webmail` | [32316046000](https://github.com/narmeshnigam/karyalay-webmail/actions/runs/32316046000) | 8 success, **including e2e on all three engines** |
| `karyalay-mail-ops` | [32313017272](https://github.com/narmeshnigam/karyalay-mail-ops/actions/runs/32313017272) | 4 success |

### What getting here found

Every one of these was invisible on the machine the code was written on. That is
the argument for the gate, stated as evidence rather than as principle.

| Defect | Why only CI could see it |
| --- | --- |
| Role-scoped nftables rules emitted invalid syntax | `nft` does not run on macOS. The rulesets would not have loaded on a real host. |
| The import-boundary lint had never inspected a single import | Unresolved path aliases were classified as external packages. It reported zero violations because it was looking at nothing. |
| 36 ops directories, 13 mail modules and 4 test suites absent from a clone | git does not track empty directories. The trees existed only locally. |
| `karyalay-webmail` had no application entry point at all | Only the production build reads `index.html`; typecheck, lint and unit tests all pass without one. |
| `upgrade-insecure-requests` in the meta tag killed the app in WebKit | Chromium and Gecko exempt loopback; WebKit does not. Two of three engines were perfectly green. |
| The fail-closed diagnostic pages rendered unstyled | `style-src-attr` blocks the attribute form. The pages still *read* correctly, so every content assertion passed. |
| The CSP feature probe used a property name no browser has | `"securitypolicyviolation" in window` is false everywhere; the attribute is `onsecuritypolicyviolation`. Every real user would have been shown the upgrade page. |
| The runtime container had none of its five PHP extensions | The image would have died on its first request. |
| `--testsuite` repeated: 7 tests ran while four suites were reported | PHPUnit silently uses only the last occurrence. |
| A CI job hung for three hours on an interactive apt prompt | No job had a timeout; the default is six. |

### Standing caveat

`tag-is-immutable` is skipped on push and runs on tag. It has therefore never
executed. It is not evidence of anything yet, and this entry does not claim it
is.
