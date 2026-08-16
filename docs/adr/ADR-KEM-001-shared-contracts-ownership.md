# ADR-KEM-001 — Ownership of the shared contracts package

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** (implemented by creation of this repository) |
| Date | 2026-08-16 |
| Supersedes | — |
| Affects | Master Contract §0.3, §4.3, §42.3; all four repository specifications |
| Approvers | Pending: architecture owner |

## Context and problem

Master Contract §0.3 declares a `contracts/` tree — OpenAPI documents, event
envelope and payload schemas, the error catalog, auth claims/roles/permissions,
the telemetry contract and the DNS record contract — as **authoritative for
integration**. Section 4.3 states these "SHOULD live in a dedicated versioned
package or top-level contracts repository that all four projects consume in CI."

All four repository specifications then depend on that package:

- Repo 1 §26.2 commits to generating `contracts/generated/public-mail-api.yaml`
- Repo 2 §47 requires a generated SDK derived from "approved OpenAPI"
- Repo 3 Appendix A assigns `contracts/` as "cross-repo wire authority"
- Repo 4 §0 requires "OpenAPI/internal action contracts and JSON Schemas"

**No document assigns ownership of producing and versioning that package.**
Every repository consumes it; none creates it.

Master Contract §42.3 states the no-silent-gap rule: "a dependency described
only informally in code comments is an integration gap." By the platform's own
governance this is a P0 gap, and it blocks Gate 0 (architecture freeze), whose
exit criteria include "first machine-readable contract package created."

## Decision

Create **`karyalay-mail-contracts`** as a fifth, first-class repository. It owns:

1. The Master Architecture & Integration Contract (canonical copy)
2. All shared machine-readable contracts under the §0.3 tree layout
3. Cross-repository ADRs (this series, `ADR-KEM-*`)
4. The cross-repository delta register consolidating Repo 3 Appendix AB and
   Repo 4 Appendix AI
5. The contract compatibility test suite consumed by all four repositories

Consumption is by **immutable version tag**. No repository may vendor, fork or
locally amend a shared schema; Master §0.3 already forbids private forks and
this repository makes that enforceable.

Write access is restricted independently of the four implementation
repositories, satisfying the §4.3 requirement that the location be "treated as
logically independent."

## Alternatives considered

**Host the contracts inside `karyalay-mail`.** Rejected. Repo 1 is one of four
consumers. Placing the shared authority inside a consumer creates an ownership
asymmetry, and every contract change would arrive coupled to a control-plane
release.

**Duplicate contracts per repository, reconciled by review.** Rejected outright
— directly contrary to Master §0.3.

**Defer until a second repository begins implementation.** Rejected. Gate 0
cannot close without it, and contract drift is cheapest to prevent before any
code exists.

## Impact

**Security / privacy.** Positive. The auth claims, roles and permissions
contracts gain a single reviewable location, so a permission cannot be widened
in one repository without a visible change here.

**Deliverability.** Neutral.

**Cross-repository.** All four repositories add a build-time dependency on a
tagged release of this repository. CI in each must fail on contract drift, per
Repo 1 §45, Repo 2 §48 and Repo 3 §74.

**Migration / rollback.** No migration — this repository is new and currently
empty of machine-readable artifacts. Rollback would mean reverting to the
unowned state, which is the gap being closed.

**Operational.** One additional repository to release and tag. Contract releases
are expected to be infrequent and are gated by the Master §0.4 change classes.

## Open work

The contract directories exist but are **empty**. Populating them is the first
Gate 0 deliverable and must precede implementation in any consuming repository.

## References

- Master Architecture & Integration Contract v1.0 §0.3, §0.4, §4.3, §42.3, §43.1
- Repo 1 §26.2 · Repo 2 §47, Appendix N · Repo 3 Appendix A, AB · Repo 4 Appendix AI
