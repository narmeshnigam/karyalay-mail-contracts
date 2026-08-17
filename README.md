# karyalay-mail-contracts

**Shared contract authority for Karyalay Email.** The single source of truth
that the four implementation repositories consume — never fork, never vendor.

Established by [ADR-KEM-001](docs/adr/ADR-KEM-001-shared-contracts-ownership.md),
which closes the ownership gap identified against Master Contract §0.3/§4.3.

## What lives here

| Path | Contents | Status |
| --- | --- | --- |
| `docs/spec/master-contract-v1.0.md` | Master Architecture & Integration Contract v1.0 (canonical working copy) | Baseline |
| `docs/adr/` | Cross-repository ADRs (`ADR-KEM-*`) and the decision register | Active |
| `docs/BUILD-ORDER.md` | Programme build sequence and cross-repo blocking matrix | Custody only — see below |
| `docs/INFRASTRUCTURE-PLAN.md` | Host, DNS and provider plan; deviation register | Custody only — see below |
| `openapi/` | Public, mailbox, internal-provisioning and operations API contracts | **Empty — Gate 0 deliverable** |
| `events/` | Event envelope + payload JSON Schemas | **Empty — Gate 0 deliverable** |
| `errors/` | Machine-readable error catalog | **Empty — Gate 0 deliverable** |
| `auth/` | Claims, roles, permissions contracts | **Empty — Gate 0 deliverable** |
| `observability/` | Telemetry contract | **Empty — Gate 0 deliverable** |
| `dns/` | Domain record contract | **Empty — Gate 0 deliverable** |

## Rules

- Consumers pin an **immutable version tag**; no repository tracks a branch.
- Change classes and approvals follow Master Contract §0.4. Shared-breaking
  changes require a master-contract revision, not a schema edit.
- Private forks of any schema are prohibited (Master §0.3).
- Gate 0 does not close until the machine-readable directories above are
  populated and every consumer's CI validates against a tagged release.

## Work plan

The Gate 0 work plan lives in [tasks/](tasks/README.md) — twelve tasks ending
in the `v0.1.0` tag that unblocks Phase 0 in every consumer repository.

Programme-wide sequencing lives in [docs/BUILD-ORDER.md](docs/BUILD-ORDER.md)
and [docs/INFRASTRUCTURE-PLAN.md](docs/INFRASTRUCTURE-PLAN.md).

## Custody-only documents

The two documents above are held here because this is the only repository every
other one already consumes — not because they carry contract authority. They sit
**below** the repository specifications in the precedence order at the foot of
this file, no consumer validates against them, and they are **not release
artifacts**: a tag captures the whole tree, but neither appears in T00.12's
release inventory and neither is something a consumer pins. When one of them
disagrees with a repository's task tree, the task tree wins and the document is
stale.

They change on their own cadence, not on the contract change classes of Master
§0.4. Editing either is never a contract change and never requires a version
bump.

## Consumers

`karyalay-mail` · `karyalay-webmail` · `karyalay-mail-infra` · `karyalay-mail-ops`

## Precedence

Master Contract → contracts in this repository → repository specification →
approved ADRs → implementation. On conflict, stop and raise an ADR — never
resolve a shared-contract conflict by invention (Master §0.2).
