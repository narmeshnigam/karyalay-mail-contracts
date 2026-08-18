# ADR-KEM-008 — Reconciling the desired-state and observation shapes between Repo 1 and Repo 3

| Field | Value |
| --- | --- |
| Status | **PROPOSED** |
| Date | 2026-08-18 |
| Raised by | Gate 0 task T00.05 (internal provisioning OpenAPI) |
| Affects | Repo 1 §12.2, §29, Appendix A.31/A.32, Appendix C.97–C.100; Repo 3 §49, §50 |
| Approvers | Architecture owner — pending |

## Context

T00.05 required the C.97–C.100 provisioning shapes to be reconciled against
Repo 3 §48–§51 *field by field*, with any mismatch raised as an ADR rather than
silently fixed. This is the single most consequential interface in the
programme: it is the only path by which customer intent reaches real mail
infrastructure, and both sides describe it — differently.

## Divergence 1 — the desired-state document

| Concern | Repo 1 §12.2 | Repo 3 §49 |
| --- | --- | --- |
| Schema versioning | absent | `schema_version: 1`, and "unknown schema version is nonretryable until code upgrade; controller MUST NOT guess" |
| Resource identity | `mailbox_id` (type-specific key) | `resource_id` (uniform) |
| Generation | `generation` | `desired_generation` |
| Target state | absent | `desired_status: "ACTIVE"` |
| Typed fields | flat at the top level | nested under `spec: {}` |
| Dependencies | absent | `dependencies: [{resource_type, resource_id, min_generation}]` |
| Correlation | `correlation: {operation_id, trace_id}` | absent |

Every one of these differences is load-bearing:

- **`schema_version`.** Repo 3 §49 makes an unknown version non-retryable by
  requirement. Repo 1's shape gives the controller nothing to check, so a
  control-plane schema change would be parsed as if it were the old shape —
  the precise failure Repo 3 wrote that rule to prevent.
- **`dependencies`.** Repo 3 §49 states these "prevent exposing a mailbox before
  domain/routing/key prerequisites have converged." Repo 1's shape carries no
  dependency list, so ordering would have to be re-derived by the controller
  from resource type — reconstructing, imperfectly, information the control
  plane already holds.
- **`generation` vs `desired_generation`.** Master §6.3 makes `generation` the
  canonical field name for a resource's desired revision, which favours Repo 1's
  spelling; Repo 3's `desired_generation` is clearer beside `observed_generation`
  in the same exchange. Either is defensible; publishing both is not.
- **`correlation`.** Repo 1 carries `operation_id` and `trace_id`; Repo 3 does
  not mention them. Master §30 requires the correlation to survive this hop.

## Divergence 2 — readiness vocabulary

| Repo 1 Appendix A.32 `status` | Repo 3 §50 readiness |
| --- | --- |
| `READY` | `READY` |
| `DEGRADED` | `DEGRADED` |
| `FAILED` | `FAILED` |
| `ABSENT` | — |
| — | `PENDING` |
| — | `RESTRICTED` |
| — | `DELETING` |

Repo 3 reports six states; Repo 1 stores four; only three overlap. `ABSENT` and
`PENDING` are not synonyms — a resource that was never created and one that is
mid-convergence require different operator responses. `RESTRICTED` is
information Repo 1 cannot currently store at all, yet it is the state that says
*infrastructure is deliberately enforcing a control-plane restriction* — the
observation most likely to be misread as a fault.

## Divergence 3 — observation fields

Repo 3 §50 requires `checksum(s)`, `component statuses` and `controller
instance`. Repo 1 Appendix A.32 has `details_json` and `source_service`.
`source_service` can carry the controller instance, and `details_json` can carry
component statuses, but checksum-based drift detection — which Repo 3 §50 names
as one of its two drift triggers — has no home in the Repo 1 row, so drift
detected by checksum could not be recorded as such.

## What v0.1.0 publishes

`openapi/internal-provisioning-api-v1.yaml` publishes the **Repo 1** shapes:
Repo 1 owns the endpoints (they are Appendix C.97–C.100 and live on Repo 1's
`/internal/v1`), and Appendix C is exhaustive by invariant. The document is
therefore correct as a description of what Repo 1 serves, and incomplete as a
description of what Repo 3 needs.

**This is not a resolution.** It is the honest publication of one side of an
interface whose two sides disagree.

## Decision (proposed)

Adopt the **union**, resolved as follows, in `v0.2.0`:

1. Add `schema_version` — Repo 3's requirement, no Repo 1 objection.
2. Use `resource_id` with `resource_type`, uniform across types. Type-specific
   keys stay inside `spec`.
3. Use `desired_generation` in this exchange, beside `observed_generation`.
   Master §6.3's `generation` remains the canonical name everywhere else,
   including the event envelope.
4. Adopt `desired_status` and `dependencies` from Repo 3.
5. Nest typed fields under `spec` per Repo 3.
6. Keep `correlation {operation_id, trace_id}` from Repo 1.
7. Adopt Repo 3's six-value readiness enum. Repo 1 Appendix A.32 gains
   `PENDING`, `RESTRICTED` and `DELETING`, and keeps `ABSENT` — Repo 3 gains
   `ABSENT` for "observed to not exist", which its enum cannot express today.
8. Add a `checksum` field to the observation.

Items 2, 3, 5 and 7 are **shared breaking** under Master §0.4 and require both
repository specs to be revised. That is the point: this interface must break
once, before either side is implemented, rather than at integration.

## Consequences

- Repo 3 Phase 3 (projection controller) and Repo 1 Phase 6 must not begin
  implementation against `v0.1.0`'s internal-provisioning document without
  reading this ADR.
- If the union is accepted, `v0.2.0` is a breaking contract release before any
  consumer has shipped — the cheapest possible moment for it.
- If the owner instead ratifies one side wholesale, the other repository's spec
  takes the correction. Either outcome is acceptable; leaving both published is
  not.

## Evidence

`docs/reconciliation/provisioning-interface.md`.
