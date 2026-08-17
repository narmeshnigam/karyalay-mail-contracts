# ADR-KEM-002 — Mailbox gateway transport: pooled IMAP rather than Doveadm HTTP

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** |
| Date | 2026-08-16 (proposed) · 2026-08-17 (accepted) |
| Amends | Repo 1 §19.1, §19.2; Repo 3 §29; Repo 2 Appendix N delta D-02 |
| Approvers | Architecture owner (Narmesh Nigam), 2026-08-17 |

## Decision record

Accepted by the architecture owner on 2026-08-17. Per-mailbox data operations
use pooled IMAP with master-user impersonation; Doveadm HTTP is retained for
administrative operations only. Consequences activated: Repo 1 Phase 5
(mailbox gateway) is unblocked on this decision; Repo 2 delta D-02 becomes
implementable via IMAP IDLE once its canonical endpoint ships in this
repository.

## Context and problem

Repo 1 §19.2 and Repo 3 §29 specify the mailbox gateway as a typed adapter over
the **Doveadm HTTP API**. Every `MailboxBackend` operation — `listMessages`,
`fetchMessageMetadata`, `streamMessagePart`, `search`, `setFlags`,
`moveMessages`, `saveMessage`, `expunge` — maps to a `doveadm` subcommand, so
the design is implementable as written.

The concern is that Doveadm is an **administrative** interface being used as a
per-user interactive data path at webmail request rates. Four consequences:

**No persistent per-user session.** IMAP holds a selected mailbox across a
connection. Doveadm does not: every call re-resolves the user and mailbox, so
list-then-open-then-flag pays full setup three times.

**No IDLE equivalent.** This is the most damaging consequence and it is already
visible in the specifications. Repo 2 Appendix N records delta **D-02 (mailbox
change feed)** as unresolved, with polling as the production fallback. That gap
is not independent of this choice — it is caused by it. Doveadm exposes no
change notification, so there is nothing underneath a change feed to build on.

**Admin-scope authorization.** Doveadm authenticates as an administrative
principal and selects the target with `-u <user>`. The per-mailbox boundary is
therefore enforced entirely by adapter correctness. One bug in target
construction is a cross-mailbox exposure — precisely the failure class Master
§26.7 requires the platform to prove impossible.

**Divergence from proven practice.** Roundcube, SOGo and Nextcloud Mail all use
pooled IMAP with a master user. No significant webmail drives mailbox reads
through Doveadm HTTP.

## Decision (proposed)

Split the gateway by operation class:

**Pooled IMAP with master-user impersonation** for all per-mailbox data
operations — folder listing and status, message list, metadata fetch, body and
part streaming, search, flags, move, copy, append, expunge.

**Doveadm HTTP, retained as specified,** for administrative operations that have
no IMAP equivalent — mailbox namespace creation at provision time, quota get and
set, `force-resync`, index rebuild, and mailbox deletion during deprovisioning.

Connection pooling is per mailbox with a bounded idle lifetime, a per-mailbox
concurrency cap, and the circuit breaker and per-operation deadline already
required by Repo 1 §19.2.

All other §19.2 safety requirements survive unchanged: no raw command strings
from HTTP input, opaque `storage_key` addressing rather than client-supplied
addresses, bounded streaming, and no protocol credentials reaching the browser.

## Alternatives considered

**Retain Doveadm HTTP throughout.** Rejected in this proposal. It leaves D-02
permanently unbackable, keeps the admin-scope blast radius, and diverges from
every comparable implementation.

**JMAP.** Rejected for v1. Master §40.2 requires an ADR to expose a new client
protocol, Dovecot CE has no production JMAP support, and it would enlarge rather
than settle the v1 surface.

**Direct browser-to-IMAP.** Prohibited by Master §2.4 and not reconsidered here.

## Impact

**Security.** Net positive. IMAP authentication is per-mailbox even under a
master user, so the mailbox boundary is enforced by the protocol rather than by
adapter string handling. Master-user credentials become a high-value secret
governed by Master §11 and must be scoped to the gateway service identity alone.

**Deliverability.** None. This path is read-side only; submission is unchanged.

**Cross-repository.**
- Repo 1 — `MailboxBackend` port is unchanged; the Dovecot adapter behind it is
  reimplemented. §19.2 gains connection-pool requirements.
- Repo 3 — §29 splits into an IMAP access contract and a reduced administrative
  Doveadm contract. Appendix F gains master-user configuration.
- Repo 2 — delta D-02 becomes implementable via IMAP IDLE, so the change feed
  moves off the deferred list.
- Repo 4 — unaffected.

**Performance.** Removes per-call setup on the hottest path. Does not remove the
PHP-FPM process-per-request ceiling on streaming; that is a separate concern and
is not addressed here.

**Migration / rollback.** No production data exists. The `MailboxBackend` port
boundary means either transport can be swapped without touching callers, so
rollback is an adapter substitution.

**Operational.** A new failure mode — pool exhaustion — requiring its own metric
and alert. Repo 1 Appendix H should gain a pool-saturation gauge.

## References

- Repo 1 §19.1, §19.2, Appendix H · Repo 2 Appendix N (D-02) · Repo 3 §25, §29, Appendix F
- Master Contract §2.4, §11, §19.1, §26.7, §40.2
