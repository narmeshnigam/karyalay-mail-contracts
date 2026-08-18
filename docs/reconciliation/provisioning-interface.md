# Reconciliation — internal provisioning interface

T00.05 evidence, compared 2026-08-18. Disposition:
[ADR-KEM-008](../adr/ADR-KEM-008-desired-state-and-observation-shape.md).

This is the field-by-field reconciliation T00.05 requires between Repo 1's
description of the desired-state exchange (§12.2, §29, Appendix A.31/A.32,
Appendix C.97–C.100) and Repo 3's (§48–§51). Both specifications describe the
same four endpoints; they do not describe the same payloads.

## 1. Endpoint agreement

Repo 3 Appendix AB lists all four as `EXISTING / CANONICAL`, with paths
identical to Repo 1 Appendix C:

| Direction | Endpoint | Repo 1 | Repo 3 |
| --- | --- | --- | --- |
| Repo 1 → Repo 3 | `GET /internal/v1/resources/{type}/{id}/desired-state` | C.98 | §49 |
| Repo 3 → Repo 1 | `POST /internal/v1/resources/{type}/{id}/observations` | C.97 | §50 |
| Repo 3 → Repo 1 | `POST /internal/v1/provisioning/{operation}/started` | C.99 | Appendix AB |
| Repo 3 → Repo 1 | `POST /internal/v1/provisioning/{operation}/result` | C.100 | Appendix AB |

No divergence. The endpoints are frozen.

## 2. Desired-state document — field by field

| Field | Repo 1 §12.2 | Repo 3 §49 | Divergence |
| --- | --- | --- | --- |
| `schema_version` | — | `1` | **Repo 3 only.** §49 makes an unknown version non-retryable by requirement; Repo 1's shape gives the controller nothing to check. |
| `resource_type` | present | present | agree |
| resource identity | `mailbox_id` (type-specific) | `resource_id` (uniform) | **Names differ.** A uniform key is what a generic controller loop needs. |
| `organisation_id` | present | present | agree |
| `domain_id` | present | inside `spec` | placement differs |
| generation | `generation` | `desired_generation` | **Names differ.** Master §6.3 canonicalises `generation`; Repo 3's spelling is clearer beside `observed_generation`. |
| `desired_status` | — | `"ACTIVE"` | **Repo 3 only.** |
| typed fields | flat at top level | nested under `spec` | **Structure differs.** |
| `dependencies` | — | `[{resource_type, resource_id, min_generation}]` | **Repo 3 only.** §49: "prevent exposing a mailbox before domain/routing/key prerequisites have converged." |
| `storage_key` | present | inside `spec` | placement differs |
| `primary_address` | present | inside `spec` | placement differs |
| `quota_bytes` | present | inside `spec` | placement differs |
| `auth_state` / `receive_state` / `send_state` | present | inside `spec` | placement differs |
| `filter_generation` | present | inside `spec` | placement differs |
| `correlation` | `{operation_id, trace_id}` | — | **Repo 1 only.** Master §30 requires correlation to survive this hop. |

Shared invariants both sides state identically, and which `v0.1.0` publishes:

- Complete relevant desired state, not an imperative shell command (both).
- Same resource + generation means the same intended state (both).
- Generation is monotonic; a lower generation never overwrites a successfully
  applied higher one (Repo 3 §49, Repo 1 §29.3).
- Secrets are referenced by handle, never embedded (Repo 3 §49, Repo 1 §11.1).

## 3. Readiness vocabulary

| Value | Repo 1 Appendix A.32 | Repo 3 §50 | Note |
| --- | --- | --- | --- |
| `READY` | yes | yes | agree |
| `DEGRADED` | yes | yes | agree |
| `FAILED` | yes | yes | agree |
| `ABSENT` | yes | — | Repo 3 cannot report "observed to not exist". |
| `PENDING` | — | yes | Repo 1 cannot store "known but not yet applied". |
| `RESTRICTED` | — | yes | Repo 1 cannot store "infrastructure is deliberately enforcing a restriction" — the state most likely to be misread as a fault. |
| `DELETING` | — | yes | Repo 1 cannot store "removal convergence underway". |

Three of six Repo 3 values have nowhere to be stored, and one Repo 1 value has
no way to be reported. `v0.1.0` publishes Repo 1's four, because the endpoint is
Repo 1's.

## 4. Observation fields

| Repo 3 §50 requires | Repo 1 Appendix A.32 has | Fit |
| --- | --- | --- |
| resource type and id | `resource_type`, `resource_id` | yes |
| `desired_generation` | (compared against the desired row) | yes |
| `observed_generation` | `generation` | yes |
| readiness | `status` | partial — see §3 |
| component statuses | `details_json` | carriable, unstructured |
| **checksum(s)** | — | **no home.** §50 names checksum mismatch as one of its two drift triggers, so drift found that way could not be recorded as such. |
| timestamp | `observed_at` | yes |
| controller instance | `source_service` | yes |

## 5. What `v0.1.0` publishes, and what it does not

`openapi/internal-provisioning-api-v1.yaml` publishes the **Repo 1** shapes.
Repo 1 owns these endpoints — they are Appendix C.97–C.100 on Repo 1's
`/internal/v1`, and Appendix C is exhaustive by invariant.

The document is therefore an accurate description of what Repo 1 serves and an
incomplete description of what Repo 3 needs. That is a deliberate, recorded
position, not an oversight: Master §0.2 forbids resolving a shared-contract
conflict by invention, and merging the two shapes here would bind both repository
owners to a design neither has approved.

**Neither Repo 1 Phase 6 nor Repo 3 Phase 3 should begin implementing against
this document without reading ADR-KEM-008.**

---

# Resolution — v0.2.0, 2026-08-18

ADR-KEM-008 accepted. The union is published in
`openapi/internal-provisioning-api-v1.yaml`. Every divergence recorded above
now has a disposition, and three validator checks fail if either side's shape
reappears alone.

## Divergence 1 — desired-state document

| Concern | Repo 1 §12.2 | Repo 3 §49 | Published | Source of the ruling |
| --- | --- | --- | --- | --- |
| Schema versioning | absent | `schema_version: 1` | `schema_version`, required | Repo 3 — Repo 1 raised no objection |
| Resource identity | `mailbox_id` | `resource_id` | `resource_id` + `resource_type` | Repo 3 — uniform across kinds |
| Generation | `generation` | `desired_generation` | `desired_generation` | Repo 3 — reads correctly beside `observed_generation`, which is Repo 1 §29.1's own wording |
| Target state | absent | `desired_status` | `desired_status`, required | Repo 3 |
| Typed fields | flat | nested under `spec` | `spec` | Repo 3 |
| Dependencies | absent | `dependencies[]` | `dependencies[]` | Repo 3 |
| Correlation | `correlation` | absent | `correlation`, required | **Repo 1** — Master §30 requires it to survive this hop |

Six of seven went to Repo 3; the seventh to Repo 1 on a Master Contract
requirement. That asymmetry is not a preference — it is what happens when the
side with the operational referent wins on shape and the Master Contract wins
on correlation.

## Divergence 2 — readiness vocabulary

Repo 1 stored four, Repo 3 reported six, three overlapped. Published: **seven**.

| Value | Repo 1 A.32 | Repo 3 §50 | Published |
| --- | --- | --- | --- |
| `READY` | ✓ | ✓ | ✓ |
| `DEGRADED` | ✓ | ✓ | ✓ |
| `FAILED` | ✓ | ✓ | ✓ |
| `ABSENT` | ✓ | — | ✓ — Repo 3 gains it |
| `PENDING` | — | ✓ | ✓ — Repo 1 gains it |
| `RESTRICTED` | — | ✓ | ✓ — Repo 1 gains it |
| `DELETING` | — | ✓ | ✓ — Repo 1 gains it |

Repo 1 Appendix A.32's `status` column is renamed `readiness` and widened to
all seven. The rename matters: leaving a column called `status` holding a value
called `readiness` reproduces in the database exactly the ambiguity this ADR
removed from the wire.

## Divergence 3 — observation fields

| Repo 3 §50 requires | Carried by | Status |
| --- | --- | --- |
| controller instance | `source_service` | resolved, no schema change |
| component statuses | `details` / `details_json` | resolved, but see below |
| `checksum(s)` | new `checksum` field and A.32 column | **resolved — this was the real gap** |

Checksum was the only one with nowhere to go. Repo 3 §50 names checksum
difference as one of its two drift triggers, so before this change a drift
detected by checksum could be observed but not reported as such.

Component statuses are carried inside free-form `details`, which is what the
ADR judged sufficient. Repo 3 Appendix P.1 is more specific — typed
`components[]` of `{name, state, generation, checksum, details}` plus
`warnings[]` — and that gap is recorded in Amendment 1 as noted-not-applied,
because decision 8 is what was accepted.

## Surfaced during implementation

Two divergences this reconciliation missed, both in Repo 3 Appendix O/P which
§49/§50 delegate to. Recorded as open items in ADR-KEM-008 Amendment 1:

1. **`resource_type` vocabularies had never been compared.** Repo 1 A.31 spells
   six; Repo 3 O.1 spells eight; two are the same concept under two spellings
   (`DKIM`/`dkim_key`, `FILTER`/`filter_set`); `organisation` and `placement`
   are Repo 1-only with **no Repo 3 materialization row** — the same class of
   gap as divergence 2, unresolved.
2. **`desired_status` has no enumerated vocabulary** in either specification.
   Published as a grammar-constrained string rather than an invented enum.

## Checks that hold this

`tools/validate/validate.mjs`:

- `the provisioning exchange carries the ADR-KEM-008 union, not either side alone`
  — every envelope field present and required; every retired spelling absent
  from the envelope **and** present in `spec`, so a field cannot be dropped
  under cover of being moved.
- `readiness is the seven-value union and the observation can record drift`
  — exact enum, no extras; `generation` and `status` must be gone; `checksum`
  must exist.
- `a dependency cannot name a resource kind the envelope cannot carry`
  — `ResourceDependency.resource_type` must `$ref` the shared vocabulary, and
  both source vocabularies must survive.
