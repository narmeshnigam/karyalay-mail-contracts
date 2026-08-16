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

## Consumers

`karyalay-mail` · `karyalay-webmail` · `karyalay-mail-infra` · `karyalay-mail-ops`

## Precedence

Master Contract → contracts in this repository → repository specification →
approved ADRs → implementation. On conflict, stop and raise an ADR — never
resolve a shared-contract conflict by invention (Master §0.2).
