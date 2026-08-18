# Correlation walkthrough

**T00.07 acceptance criterion:** *a single correlation ID demonstrably survives
the documented path — API request → outbox event → consumer job.*

This traces one mailbox creation end to end. Every hop cites the rule that
carries the identifier across it. Nothing below is aspirational: if a hop
cannot be implemented as written, that is a contract defect and belongs in an
ADR, not in a workaround.

## The path

```
browser            karyalay-mail            NATS JetStream        karyalay-mail-infra
   │                     │                        │                        │
   │ POST /api/v1/…      │                        │                        │
   ├────────────────────►│ ① request boundary     │                        │
   │  traceparent        │                        │                        │
   │  X-Request-ID       │                        │                        │
   │  Idempotency-Key    │                        │                        │
   │                     │ ② one transaction:     │                        │
   │                     │   state + audit +      │                        │
   │                     │   outbox row           │                        │
   │  201 + X-Request-ID │                        │                        │
   │◄────────────────────┤ ③                      │                        │
   │                     │ ④ mail-outbox publishes│                        │
   │                     ├───────────────────────►│ ⑤ envelope             │
   │                     │  Nats-Msg-Id: event_id │                        │
   │                     │                        ├───────────────────────►│ ⑥ consumer job
   │                     │                        │                        │
   │                     │                        │                        │ ⑦ SMTP/IMAP boundary
```

## ① Request boundary

`POST /api/v1/organisations/{org}/mailboxes` arrives with `traceparent` and,
optionally, `X-Request-ID`.

- The server span is named by **route template**, never the raw URL — Repo 1
  §40.2. `/api/v1/organisations/{org}/mailboxes`, not the interpolated path.
- `request_id` is accepted or generated — Repo 1 §26, Master §20.7. A supplied
  value is validated before propagation; an untrusted arbitrary value must not
  permit log injection (Master §20.7).
- `trace_id` comes from the W3C trace context.
- `Idempotency-Key` is required for this operation (Master §20.5) and is
  **not** a correlation identifier — Master §6.2 forbids overloading it.

Every log record from here on carries `request_id` and `trace_id`
(`log-record-v1.schema.json`).

## ② One transaction

Repo 1 §31.2 step 1: the canonical state write, the audit event and the outbox
row commit in **the same MariaDB transaction**. The outbox row carries the
envelope, and the envelope carries `trace_id` and `request_id`
(Master §22.3).

This is the hop that would otherwise break the chain. If the outbox row were
written outside the transaction, a crash would leave state without an event —
and no correlation identifier can survive an event that was never recorded.

## ③ Response

The response echoes the safe `request_id` (Repo 1 §26). A failure returns a
problem document whose `request_id` and `trace_id` members are the same values
(Repo 1 §26.1, Master §20.3) — so a user-reported failure is searchable from
the one string the UI can safely show them.

## ④ Publication

`mail-outbox` claims unpublished rows in bounded batches and publishes to
`KARYALAY_MAIL_EVENTS_V1` on `mail.v1.mailbox.requested`, setting
`Nats-Msg-Id` to `event_id` (Repo 1 §31.2 step 2).

After broker acknowledgement the publisher marks `published_at`. **A crash
between the acknowledgement and the mark republishes the same `event_id`**
(§31.2 step 3) — which is exactly why `event_id` is the dedupe key and not a
per-attempt value.

## ⑤ Envelope in flight

```json
{
  "event": "mailbox.requested",
  "version": 1,
  "event_id": "018f…",
  "occurred_at": "2026-08-18T04:11:07.219043Z",
  "producer": "karyalay-mail",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "request_id": "req_01J…",
  "organisation_id": "…",
  "resource": { "type": "mailbox", "id": "…", "generation": 1 },
  "data": { "organisation_id": "…", "domain_id": "…", "mailbox_id": "…", "generation": 1 }
}
```

`trace_id` and `request_id` are envelope members, not payload members. They
survive because the envelope is shared (Master §22.3) — a consumer never has to
know a producer's payload shape to correlate.

## ⑥ Consumer job

The consumer starts its job span as a **child of the envelope `trace_id`** and
copies `request_id` into its log context (§2 of the telemetry contract).

Two rules bound what it may conclude:

- **At-least-once.** The same `event_id` may arrive twice; handlers are
  idempotent on it (Master §22.2, Repo 1 Appendix D.1).
- **No ordering guarantee.** The event may arrive *after* a newer state.
  The consumer compares `resource.generation` before acting (Master §22.2). A
  resource is ready only when `observed_generation == desired_generation` with
  fresh READY sub-observations — HTTP 200 from Infra is not readiness
  (Repo 1 §29.1).

## ⑦ Where the trace stops, and what replaces it

Trace context does not cross into Postfix or Dovecot. Master §30.5 and Repo 3
§68 are explicit that Internet mail protocols are not modified to carry it.

The bridge is a **recorded pair**: at submission acceptance, `submission_id`
and `smtp_queue_id` are written to the same structured event (Master §30.3,
Repo 1 §23.1). An inbound Internet message has no trusted external trace
context at all — Karyalay creates its own correlation boundary (Repo 3 §68).

So the end-to-end join is:

```
request_id ──► trace_id ──► event_id ──► submission_id ──► smtp_queue_id
   (HTTP)       (trace)      (event)       (send record)     (transport)
```

Master §6.2 keeps these five distinct on purpose. Overloading any two of them
collapses the chain at the point where it is most needed: the ambiguous send
(`SUBMISSION_STATUS_UNKNOWN`, Repo 1 §39.1), where the only way to tell a lost
message from a delivered one is that the pair was recorded before the outcome
became uncertain.

## What a reviewer should check

| Hop | Check |
| --- | --- |
| ① | Span named by route template; `request_id` echoed in the response and in problem documents |
| ② | Outbox row and state change in one transaction |
| ④ | `Nats-Msg-Id` equals `event_id` |
| ⑤ | `trace_id` and `request_id` present on the envelope, not buried in `data` |
| ⑥ | Handler idempotent on `event_id`; acts on `resource.generation`, not arrival order |
| ⑦ | `submission_id` and `smtp_queue_id` recorded together at acceptance |
