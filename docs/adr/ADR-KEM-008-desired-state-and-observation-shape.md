# ADR-KEM-008 — Reconciling the desired-state and observation shapes between Repo 1 and Repo 3

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** |
| Date | 2026-08-18 |
| Raised by | Gate 0 task T00.05 (internal provisioning OpenAPI) |
| Affects | Repo 1 §12.2, §29, Appendix A.31/A.32, Appendix C.97–C.100; Repo 3 §49, §50 |
| Approvers | Architecture owner — accepted 2026-08-18 |

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

---

# Amendment 1 — resolutions surfaced during implementation

The union was implemented in `v0.2.0` on 2026-08-18. Decisions 1–8 above
resolved every divergence the ADR enumerated. Implementation surfaced two more
that the enumeration missed, because both live in Repo 3 **Appendix O/P**,
which §49/§50 delegate to and which the original comparison did not open.

Neither is resolved by invention. Each is resolved by applying the accepted
union principle — *take both sides; where the two spell the same concept
differently, publish one* — and each is recorded here as an **open item** for
confirmation, because extending an accepted decision is not the same as having
made it.

## Open item 1 — the `resource_type` vocabulary

The two specifications carry different resource vocabularies, and neither the
ADR nor the reconciliation noticed:

| Concept | Repo 1 Appendix A.31 | Repo 3 Appendix O.1 | Published in `v0.2.0` |
| --- | --- | --- | --- |
| domain | `DOMAIN` | `domain` | `domain` |
| mailbox | `MAILBOX` | `mailbox` | `mailbox` |
| quota | `QUOTA` | `quota` | `quota` |
| DKIM key | `DKIM` | `dkim_key` | **`dkim_key`** — same concept, two spellings |
| filter set | `FILTER` | `filter_set` | **`filter_set`** — same concept, two spellings |
| alias | — | `alias` | `alias` — Repo 3 only |
| group | — | `group` | `group` — Repo 3 only |
| restriction | — | `restriction` | `restriction` — Repo 3 only |
| organisation | `ORGANISATION` | — | `organisation` — **Repo 1 only** |
| placement | `PLACEMENT` | — | `placement` — **Repo 1 only** |

Resolution applied: Repo 3's spelling wins the two collisions, because
Appendix O.1 maps each kind to a named Repo 3 materialization and is therefore
the side with the operational referent. Repo 1 Appendix A.31 takes the
correction.

**Open:** `organisation` and `placement` are dispatched by Repo 1 and have **no
Appendix O.1 materialization row**. They are published so nothing is lost, but
Repo 3 cannot currently say what it would build for either. Repo 3 either adds
two Appendix O.1 rows or Repo 1 stops dispatching them as desired-state
resources. This is the same class of gap as divergence 2 and should not be left
to Wave 3 to discover.

## Open item 2 — `desired_status` has no fixed vocabulary

Decision 4 adopted `desired_status` from Repo 3 §49. Neither §49 (`"ACTIVE"`,
by example) nor Appendix O.1 (`"..."`) enumerates it, and Appendix Q says only
`"ACTIVE/RESTRICTED/DELETING etc mapped from desired state"` — the `etc` is in
the source.

Repo 1's lifecycle vocabularies are per resource and richer: Appendix A.14
mailboxes carry
`REQUESTED/CONFIGURING/ACTIVE/RESTRICTED/SUSPENDED/PROVISIONING_FAILED/DELETION_PENDING/RECOVERY_WINDOW/DELETED`,
and domains a different nine.

Resolution applied: `desired_status` is published as a **grammar-constrained
string** (`^[A-Z][A-Z0-9_]*$`, ≤40) whose per-type vocabulary is that
resource's own Appendix A lifecycle column. Enumerating a single cross-type
set here would have invented one, which Master §0.2 forbids.

**Open:** a controller cannot reject an unknown `desired_status` at the schema
boundary, only at the projection. If a closed per-type enum is wanted, it needs
a `resource_type`-discriminated schema and an owner ruling on whether every
Repo 1 lifecycle value is meaningful to Repo 3.

## Noted, not applied — the richer observation shape

Decision 8 added `checksum` alone, on the ADR's judgement that
`details_json` carries Repo 3 Appendix P.1's component statuses and
`source_service` carries its `controller_instance`. That judgement was kept.

Appendix P.1 is nonetheless more specific than what `v0.2.0` publishes: it
defines `components[]` as typed entries of `{name, state, generation, checksum,
details}` plus a `warnings[]` array. Carrying them inside a free-form
`details_json` means neither side can validate them and per-component checksums
stay unaddressable.

Not applied, because decision 8 is what was accepted. Raise as a follow-up if
per-component drift attribution is wanted before Repo 3 Phase 3.

## What `v0.2.0` publishes

`openapi/internal-provisioning-api-v1.yaml`, schemas `DesiredState`,
`DesiredStateSpec`, `DesiredStateResourceType`, `ResourceDependency` and
`ObservationReport`. Three validator checks pin the union
(`tools/validate/validate.mjs`) and fail if either side's shape reappears alone.

Specifications revised: Repo 1 §12.2, Appendix A.31, Appendix A.32; Repo 3
§49, §50, Appendix O.1, Appendix P.1.
