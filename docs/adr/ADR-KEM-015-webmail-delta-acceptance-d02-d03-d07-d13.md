# ADR-KEM-015 — Accept webmail deltas D-02, D-03, D-07 and D-13 into the contract

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** |
| Date | 2026-08-24 |
| Raised by | Wave 5 opening; the decision ADR-KEM-010 scheduled and did not take |
| Affects | Repo 1 Appendix C (grows 115 → 120); Repo 2 Phase 5; contracts `v0.5.0` → `v0.6.0`; all four consumer pins |
| Approvers | Programme owner — accepted 2026-08-24 |

## Context

[ADR-KEM-010](ADR-KEM-010-webmail-delta-acceptance-d01-d04-d05.md) accepted three
of the seven task-blocking deltas and was explicit about the other four:

> D-02, D-03, D-07 and D-13 remain **deferred**. They are not refused; they are
> undecided, and Wave 5 cannot open its Repo 2 Phase 5 without deciding them —
> four of that phase's seven tasks depend on them. Recording that here so the
> decision is scheduled rather than rediscovered.

This is that scheduled decision, taken at the point it was scheduled for. It is
**not a supersession** of ADR-KEM-010, which decided what it decided correctly;
it is the second half of a two-part decision, and the deferral register records
the four as `HONOURED` rather than `MISSED_THEN_HONOURED` for that reason.

Each of the four blocks exactly one Repo 2 Phase 5 task and each has a working
fallback, which is why deferring them was reasonable. Deferring them further was
not: a fallback is a degraded mode, and Phase 5's own name — *live, safety,
power* — is the phase where the degraded modes were supposed to stop.

## Decision

**D-02, D-03, D-07 and D-13 are accepted as catalog operations C.116–C.120**,
published in `v0.6.0`. Five operations for four deltas: D-13 needs a register and
a revoke, and a registration you cannot revoke is a worse contract than none.

| Delta | Operation | Path |
| --- | --- | --- |
| D-02 | C.116 `getMailboxChanges` | `GET /api/v1/mailboxes/{mailbox}/changes` |
| D-03 | C.117 `reportMessageFeedback` | `POST /api/v1/mailboxes/{mailbox}/messages/{message}/feedback` |
| D-07 | C.118 `getMessageRemoteContent` | `GET /api/v1/mailboxes/{mailbox}/messages/{message}/remote-content` |
| D-13 | C.119 `registerPushSubscription` | `PUT /api/v1/me/push-subscriptions/{subscription}` |
| D-13 | C.120 `revokePushSubscription` | `DELETE /api/v1/me/push-subscriptions/{subscription}` |

## The four design decisions worth arguing

### D-02 is long-poll, not SSE or WebSocket

Appendix N permits any of the three. The catalog's shape decides it: every other
operation in Appendix C is request/response, and an event-stream response would
be the only one no `ServedOperationsTest` could check against a schema. A
contract that its own conformance suite cannot verify is a contract in name.

`wait_seconds` is bounded at 30 and the server returns an **empty page** at the
bound rather than holding on. That is not a detail — an unbounded hold is a
request a proxy times out instead of the server answering, and a client cannot
distinguish a proxy timeout from a stalled feed.

The cursor is opaque and server-minted, because a client-composable cursor is a
client-composable query and this one addresses a tenant's mailbox. And a change
carries **identifiers and a kind, never content**: a feed that returned message
bodies would be an unbounded read path wearing a notification's clothes, exempt
from the §38 controls the mailbox routes carry.

### D-03's classification is a closed set, and PHISHING is not a flag on SPAM

Free-text feedback is a content channel into the filter and into the abuse
queue. `SPAM | NOT_SPAM | PHISHING` is the whole vocabulary.

Phishing is separate rather than a boolean on spam because the two have
different urgencies and different downstream owners, and collapsing them loses
the distinction at the only point it is cheap to record. The response says the
report was recorded and **nothing about what it will do**: returning a filter
score or a reputation value turns the endpoint into an oracle a spammer tunes
against.

### D-07's safety property is that the URL must appear in the message

This is the whole reason C.118 is a proxy rather than an open SSRF relay. The
server resolves the requested `url` against the message it already stored, so a
caller with a valid session cannot aim it at an internal address — the set of
fetchable URLs is exactly the set some sender already put in that reader's
mailbox.

The rest is defence behind that: https only, DNS checked against private and
link-local ranges **after** resolution rather than before (checking the literal
before resolving is the classic bypass), redirects bounded and re-checked at
every hop, size and content-type capped, and no caller headers forwarded. A
blocked fetch returns a stable Appendix E code and never the origin's error
text, which would otherwise disclose whether an internal host exists.

The response is `Content-Disposition: inline`. The generator's binary branch
emitted `attachment`, which is right for C.73/C.74's downloads and would have
made every remote image in every message download instead of display — the
opposite of the feature. The branch now takes an `inline` flag.

### D-13 stores a transport handle and nothing about what will be sent

A push payload traverses a third-party push service. The contract is therefore
that **a notification says a mailbox has new mail and the client fetches the
rest over an authenticated channel** — no subject, no sender, no preview.

`p256dh` and `auth` are write-only: `PushSubscriptionRecord` withholds them, so
a read of this route cannot reconstruct the ability to push to the device. The
subscription id is client-chosen so re-registration on every app start is a
`PUT` to a known path rather than create-then-reconcile, and revoke is
idempotent because a client that lost its response must be able to retry.

## Three generator defects this found

Adding five operations to a 115-operation catalog exercised the tooling harder
than adding one, and it failed three times — each a hard-coded count that had
become a second place to remember the same number:

- `gen_openapi.py` refused the spec with *"Appendix C parsed to 120 cards; the
  appendix preamble states 115"*. The preamble was the source of truth and the
  literal `115` was a copy of it. It now reads the preamble.
- The same file asserted `total != 115` after emission, and wrote
  `declared_operation_count: 115` into the reconciliation document. Both now
  derive.
- `openapi/infra-executor-api-v1.yaml` is hand-authored and **was in no
  stamper**, so its version sat at whatever release it was last hand-edited in.
  It read `0.5.0` while every other artifact moved. `stamp_handauthored.py` now
  covers OpenAPI documents as well as contract YAMLs.

The pattern is the one the 2026-08-24 phase-gate audit was drawing: a fact
written in two places is a fact that will disagree, and the disagreement is
found by whatever change first makes the two differ.

## Consequences

- Repo 1 implements five operations. Phase 5's four blocked Repo 2 tasks
  (T05.02–T05.05) unblock once it does; the contract landing is necessary and
  not sufficient.
- The deferral register's `unassigned_owner_baseline` drops **5 → 1**. All four
  of these carried `decision_owner: UNASSIGNED`, and the ratchet's own failure
  message asked for the lowering in as many words — a baseline left above the
  real count silently re-permits what was just fixed.
- Repo 2's Appendix N has **no task-blocking delta left deferred**. Thirteen
  entries remain `OPEN` and none of them blocks a task.
