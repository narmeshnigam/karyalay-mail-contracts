# ADR-KEM-006 — Reconciling the event envelope and catalog across four specifications

| Field | Value |
| --- | --- |
| Status | **PROPOSED** |
| Date | 2026-08-18 |
| Raised by | Gate 0 task T00.02 (event envelope and payload catalog) |
| Affects | Master Contract §22.3, Appendix C; Repo 1 §31.1, Appendix D; Repo 3; Repo 4 Appendix E |
| Approvers | Architecture owner — pending |

## Context

T00.02 required the envelope from the Master Contract and one payload schema per
event in Repo 1 Appendix D. Doing so surfaced three separate divergences. They
are recorded together because they are one question — *who owns an event name* —
seen from three angles.

## Divergence 1 — the envelope

| Member | Master §22.3 | Repo 1 §31.1 |
| --- | --- | --- |
| aggregate reference | `resource` | `aggregate` |
| its version member | `resource.generation` | `aggregate.version` |
| request correlation | `request_id` present | absent |

`generation` and `version` are not interchangeable. Master §6.2 defines
`generation` as the reconciliation revision of a resource, and Master §22.2
requires consumers to compare it when ordering matters. Repo 1 Appendix A.5 and
A.13 carry **both** a `version` (optimistic concurrency, Master §24.5) and a
`desired_generation` (reconciliation) on the same row — so a consumer reading
`aggregate.version` and a consumer reading `resource.generation` are reading two
different numbers with two different monotonicity guarantees.

Dropping `request_id` breaks the correlation chain that Master §20.7 and §30
require: without it, a customer-reported failure cannot be joined from the API
request through the outbox to the consumer job.

**Proposed:** the envelope follows **Master §22.3** — `resource {type, id,
generation}` plus `request_id`. `events/envelope-v1.schema.json` is already
published this way, under Master §0.2 precedence. Repo 1 §31.1 needs a
repository-spec correction.

## Divergence 2 — Master Appendix C reserved names

Master Appendix C lists 30 "reserved canonical names" and states repo specs may
add events "without changing meanings below". **Eighteen of the thirty do not
appear in Repo 1 Appendix D under that name.** They fall into three groups:

**Ten name facts Repo 1 does not produce at all** — `migration.*`, `restore.*`
and `abuse.*` are Repo 4's, `dkim.selector_activated` is Repo 3's. Their absence
from a *Repo 1* appendix is correct, not a gap.

**Five are renames**, where Appendix D carries the same fact under a different
name:

| Master reserved name | Repo 1 Appendix D | Assessment |
| --- | --- | --- |
| `organisation.suspended` | `organisation.mail_restricted` | Near-equivalent; Repo 1's name scopes it to mail. |
| `domain.created` | `domain.requested` | `requested` is the more accurate past-tense fact. |
| `domain.deleted` | `domain.deletion_requested` + `domain.released` | Split into two facts, which is more precise. |
| `mailbox.provisioning_failed` | `provisioning.failed` | Re-homed to a wider `provisioning.*` family. |
| `mailbox.restriction_lifted` | `mailbox.restriction_cleared` | Rename only. |

**Three are genuine gaps** — no Appendix D event carries the fact:

| Reserved name | Why it matters |
| --- | --- |
| `organisation.created` | `organisation.mail_activated` is a strictly later fact. Nothing announces the organisation's creation. |
| `domain.verification_requested` | The challenge is returned synchronously by C.7/C.11, so no consumer learns a challenge is outstanding. |
| `security.credential_reset` | Master §9.7 requires the security-event stream to record password reset and recovery; no Appendix D event does. |

## Divergence 3 — events no appendix defines

Two consumer expectations have no producer-side definition anywhere:

- **Repo 4 Appendix E** consumes `mail.v1.auth.*`, `mail.v1.delivery.*` and
  `mail.v1.abuse.*`. Repo 1 Appendix D defines **no** `auth.*`, `delivery.*` or
  `abuse.*` event. A consumer subscribing to a subject nothing publishes fails
  silently — the worst failure mode available, because it looks like "no
  activity".
- **Repo 1 Appendix C.2's own Notes** say the endpoint "emits
  `organisation.mail_settings_changed`". That event is not in Appendix D. An
  endpoint card naming an event its own appendix does not define is a
  self-contradiction inside one specification.

## Decision (proposed)

1. **Envelope:** Master §22.3 wins. Already published. Repo 1 §31.1 corrected by
   repository-spec revision.
2. **Catalog scope:** `events/` publishes the 45 `mail.v1.*` events of Repo 1
   Appendix D and nothing else. Repo 3 (`infra.v1.*`) and Repo 4 (`ops.v1.*`)
   own their own streams and will publish schemas into this repository under
   their own directories at a later tag.
3. **Reserved names:** Master Appendix C is annotated as a *baseline of
   reserved namespaces*, not a list of required event names, in the next master
   revision. The five renames are ratified in Repo 1's favour — each is the more
   precise name. The three genuine gaps are referred to the Repo 1 owner as
   candidate additions — **not added here**, per Master §0.2.
4. **Undefined consumer expectations:** Repo 4's three subject families and
   `organisation.mail_settings_changed` are recorded as open. Repo 4 MUST NOT
   build consumers against them until they exist.

## Consequences

- `v0.1.0` ships 45 events. A consumer that needs a 46th gets it through this
  ADR process, never by invention.
- Repo 4's collector work against `mail.v1.auth.*`, `mail.v1.delivery.*` and
  `mail.v1.abuse.*` is blocked until item 4 is resolved. That is a real schedule
  consequence and is better known now than at integration.
- Repo 1's C.2 card and Appendix D disagree; the repository owner resolves it.

## Evidence

`docs/reconciliation/event-catalog.md` — the full 30-row comparison and the
consumer-expectation gap list.
