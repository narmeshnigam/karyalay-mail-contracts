# ADR-KEM-009 — Disposition of the Repo 4 → Repo 3 typed executor deltas (AI-04..AI-09)

| Field | Value |
| --- | --- |
| Status | **PROPOSED** |
| Date | 2026-08-18 |
| Raised by | Gate 0 task T00.06 (freeze the ops executor interface deltas) |
| Affects | Repo 4 Appendix AI (AI-04..AI-09); Repo 3 Appendix AB; Repo 4 Phase 0 |
| Approvers | Architecture owner — pending |

## Context

Repo 4's specification requires typed, allow-listed Repo 3 executors. Its
Appendix AI records six of them as deltas. T00.06 requires each to be either
defined in `v0.1.0` or explicitly deferred with a target tag — "frozen" meaning
a recorded disposition, not silence.

## The blocking finding

Repo 3's own **Appendix AB** already answers this, and the answer is no:

> "Repo 4 operational action API is the primary known future delta; until its
> contract is approved, Repo 3 exposes only local admin/runbook tooling, **not a
> speculative production API**."

and, on delta handling:

> "A DELTA entry is not permission for Agent 3 to invent an undocumented
> endpoint. It must be proposed as OpenAPI/JSON Schema, reviewed against
> Master/Repo owner, assigned version, then implemented on both sides."

So none of AI-04..AI-09 can be authored into `v0.1.0` by this repository.
Authoring them here would be precisely the speculative production API Repo 3
forbids — and would bind Repo 3 to an interface its owner has not reviewed.

This is a finding, not an impasse: the deltas are frozen as **deferred with a
target tag**, which is what T00.06 asks for.

## Per-delta disposition

| ID | Required contract | Repo 3 surface today | Classification | Disposition |
| --- | --- | --- | --- | --- |
| **AI-04** | Allow-listed migration executor using Dovecot migration primitives, without generic Doveadm | Repo 3 §29 exposes a typed allow-listed **mailbox gateway** (listFolders … expunge, quota) for Repo 1. No migration primitives in that allow-list. | Needs Repo 3 spec addition | **Defer to v0.2.0.** Requires a Repo 3 ADR extending the gateway allow-list with migration operations. |
| **AI-05** | Queue diagnostic/action service: summary, item metadata, scoped hold/release/retry | Repo 3 §34 owns retry/bounce/queue-lifetime policy; no external action interface. Appendix AB names "controlled queue retry" as the DELTA. | Needs Repo 3 spec addition | **Defer to v0.2.0.** |
| **AI-06** | Mailbox restore executor: stage recovery point, verify, import recovery folder, approved replacement mode | Repo 3 §58 and Appendix AJ define backup and recovery-drill *procedures*, operator-run. No typed executor. | Needs Repo 3 spec addition | **Defer to v0.2.0.** |
| **AI-07** | Read-only shard/DRBD/fencing/Galera/NATS/OpenBao health endpoint for Ops diagnostics | Repo 3 §67 requires all of these as **metrics**, and Appendix AB records "Delivery/reputation metrics/log query surfaces" as `OWNER: Repo3 telemetry`. Metrics exist; a typed health *endpoint* does not. | Partially confirmable | **Defer the endpoint to v0.2.0.** Ops consumes the §67 metrics in the interim — sufficient for dashboards and alerting, insufficient for a synchronous diagnostic call. |
| **AI-08** | Backup catalog / recovery point and restore-verification events and queries | The **event** half exists: Repo 4 Appendix E consumes `infra.v1.backup.*` and Repo 3 §58 produces backup state. The **query** half does not. | Split | **Event half: confirm at v0.2.0** when Repo 3 publishes `infra.v1.*` schemas here. **Query half: defer to v0.2.0.** |
| **AI-09** | Maintenance typed actions: drain/restart/validate with `action_id`/preconditions | Appendix AB names "IP drain, migration maintenance state" as part of the same DELTA. | Needs Repo 3 spec addition | **Defer to v0.2.0.** |

## The shared prerequisite

Four of the six (AI-04, AI-05, AI-06, AI-09) are *actions*, and Repo 4 Appendix
AI **AI-12** already asks for the thing they all need first:

> "Canonical action envelope: `action_id`, `idempotency_key`, actor/service,
> `reason_code`, evidence refs, precondition version, result/observed state.
> Freeze machine-readable schema."

Defining four action executors before their shared envelope would produce four
incompatible action shapes. **AI-12 is therefore sequenced first**, as the
`v0.2.0` opening item, and AI-04/05/06/09 are authored on top of it.

## Decision (proposed)

1. All six deltas are **deferred to `v0.2.0`**, with AI-08's event half
   confirmable at the same tag once Repo 3 publishes its stream schemas.
2. **AI-12 (canonical action envelope) is sequenced ahead of AI-04/05/06/09.**
3. Repo 3 raises one ADR extending its typed allow-list to cover migration,
   queue, restore and maintenance operations. Until it is accepted, Repo 3
   exposes local runbook tooling only, per its Appendix AB.
4. Repo 4's Phase 0 blocker line cites **this ADR** rather than "pending", so
   the blocker names a decision with a target tag instead of an open question.

## Repo 4 phases that stay blocked

| Repo 4 area | Blocked on | Until |
| --- | --- | --- |
| Migration execution (its Phase 2) | AI-04 | v0.2.0 |
| Queue diagnostics and controlled retry (Phase 1/Phase 5) | AI-05 | v0.2.0 |
| Restore orchestration (Phase 4) | AI-06 | v0.2.0 |
| Synchronous infra health diagnostics (Phase 1) | AI-07 | v0.2.0 — metrics-based diagnosis available now |
| Backup recoverability queries (Phase 4) | AI-08 query half | v0.2.0 |
| Change/maintenance orchestration (Phase 5) | AI-09 | v0.2.0 |

This is consistent with the schedule already recorded in
[BUILD-ORDER §11](../BUILD-ORDER.md) finding 2: Repo 4 leaves Wave 2 and joins
at Wave 4 under ADR-OPS-022.

## Consequences

- `v0.1.0` ships with all six deltas dispositioned; none is left implicit, which
  is what T00.06 required.
- No speculative Repo 3 interface is published, so Repo 3 is not bound to an
  API its owner has not reviewed.
- Repo 4's Phase 0 exit no longer waits on an unanswerable question.
