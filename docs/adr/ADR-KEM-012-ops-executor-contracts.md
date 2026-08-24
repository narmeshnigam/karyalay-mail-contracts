# ADR-KEM-012 — Publish AI-12 and AI-04..AI-09 in `v0.5.0`

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** |
| Date | 2026-08-24 |
| Raised by | The AI-04..AI-09 gap: ten Repo 4 tasks blocked, no task owning the fix |
| Affects | New `actions/` directory; `openapi/infra-executor-api-v1.yaml`; Repo 3 Appendix AB; Repo 4 Phases 1, 2, 4, 5; `v0.4.0` → `v0.5.0` |
| Approvers | Programme owner — accepted 2026-08-24 |

## Context

[ADR-KEM-009](ADR-KEM-009-ops-executor-delta-disposition.md) (ACCEPTED
2026-08-18) deferred Repo 4's six executor deltas to **`v0.2.0`** and named the
prerequisite in its own decision:

> Repo 3 raises one ADR extending its typed allow-list to cover migration,
> queue, restore and maintenance operations.

**That ADR was never raised, and the deferral was never honoured.** This
repository reached `v0.4.0` — three tags past the target — with the six deltas
present in no tag and ten Repo 4 tasks ⛔ on them across its Phases 1, 2, 4
and 5.

The reason is worth recording, because it is a process defect rather than an
oversight: `T00.06` is ☑ and correctly so. Its acceptance criterion was to
record a *disposition*, not to publish contracts. **The deferral closed a task
without creating one**, so no task in any repository owned the work, and a
deferral with a target tag and no owner is indistinguishable from a decision
not to do it.

## Decision

**`v0.5.0` publishes AI-12 and AI-04..AI-09.**

1. **`actions/action-envelope-v1.schema.json`** — AI-12, the canonical action
   envelope. Published **first**, per ADR-KEM-009: *"Defining four action
   executors before their shared envelope would produce four incompatible
   action shapes."* A new top-level directory, because an action envelope is
   neither an event nor an error nor an auth artifact.

2. **`openapi/infra-executor-api-v1.yaml`** — the six executors, over that
   envelope, authorised by
   [ADR-INF-038](../../../karyalay-mail-infra/docs/adr/ADR-INF-038-ops-executor-allow-list.md)
   (ACCEPTED 2026-08-24), which is the missing prerequisite, raised.

3. **`openapi/executor-reconciliation-v1.yaml`** — the Appendix AI counterpart
   to the generated Appendix C reconciliation, so both documents have an
   exhaustive map.

### Where the shapes came from

Not invented here. Repo 4's `internal/infraclient` already carried the complete
typed client for all six (T00.07a, 2026-08-22), derived from its own Appendix
AI and reviewed. This publishes what that client already binds to, reconciled
field for field. Authoring fresh shapes would have produced a contract the one
existing implementation did not match.

The one place the contract deliberately **diverges** from that client is
recorded below.

## What the contract fixes that the implementation had wrong

**AI-05's mutability is per request, not per operation.** Repo 4's client keyed
mutability on the *method* (`Method.Mutating()`), so `queue.diagnostics` was
classified as a read — and `HOLD`, `RELEASE` and `RETRY` therefore bypassed
envelope validation entirely. A queue hold could be requested with no
`action_id`, no `reason_code`, no evidence and no precondition.

Nothing was going to catch that. The client's own tests asserted the mutating
set matched the method table, and the method table was the thing that was
wrong. The contract states the rule with `if`/`then` so neither side can drift
back to it, and Repo 4's client is corrected in the same change.

**Two other rules moved from prose into schema** on the same reasoning:

- **`REPLACE` requires a human actor.** It is the only restore mode that can
  destroy mail the customer received after the recovery point. A runbook saying
  so is consulted by people who already know to be careful.
- **A hold must name one item.** `HOLD`/`RELEASE`/`RETRY` require
  `scope: ITEM` and an `item_id`, so a queue-wide hold is not expressible. A
  hold that names no item is an outage requested by an operator who meant to
  pause one message.

**And one contract defect is fixed at its source.** `idempotency_key` now
carries `^[A-Za-z0-9._~-]{1,128}$`. T00.07b found that karyalay-mail enforces
RFC 3986 unreserved characters while the published schema had `maxLength` and
no pattern — and rejects a malformed key by reporting a *missing* one
(`IDEMPOTENCY_KEY_REQUIRED`). Appendix AP.1's own worked example
(`case:...:mailbox-lock:v1`) contains colons and fails. Publishing the pattern
is what stops a client that follows the specification from failing every
request permanently for a reason the response misdescribes.

## Consequences

- **Ten Repo 4 tasks unblock**: `T01.02`, `T01.04`, `T02.06`, `T02.07`,
  `T02.08`, `T04.01`, `T04.02`, `T04.03`, `T05.03`, `T05.06`.
- **Repo 3's Appendix AB DELTA row closes.** Repo 3 may now expose these six as
  a production API, which Appendix AB forbade until the contract was approved.
- **Repo 3 owes an implementation, and Repo 4 owes callers.** The contract
  existing is what lets both build against it; neither serves nor calls it yet.
  Publishing ahead of implementation is the whole point of the sequencing.
- **Three new harness checks** guard the properties that would otherwise be
  prose: the executor document reconciles 1:1 with Appendix AI, no operation
  carries a command-shaped field, and the envelope inlined into the OpenAPI
  matches the schema file field for field.
- **Repo 3 is still pinned to `v0.2.1`.** It must advance to consume this, and
  that advance now crosses C.108–C.115 as well. Still owed a decision, and now
  with a reason to make it.

## The process lesson, since it cost six days and three tags

A deferral needs an owner, not just a target tag. ADR-KEM-009 named a
prerequisite ADR and no task was created to raise it; the target tag passed
three times and nothing failed, because no check compares a deferral's target
against the current version.

**A check for that is worth writing** and is not written here — it belongs with
whoever makes the delta register machine-readable, which is the same gap
ADR-OPS-024 hit from the other side.

## References

- [ADR-KEM-009](ADR-KEM-009-ops-executor-delta-disposition.md) — the deferral
  and its unmet prerequisite.
- [ADR-INF-038](../../../karyalay-mail-infra/docs/adr/ADR-INF-038-ops-executor-allow-list.md)
  — the allow-list extension this publishes against.
- Repo 4 Appendix AI (AI-04..AI-09, AI-12) and Appendix AP.1; Repo 3
  Appendix AB.
