# ADR-KEM-005 — Reconciling the Master error catalog baseline with Repo 1 Appendix E

| Field | Value |
| --- | --- |
| Status | **PROPOSED** |
| Date | 2026-08-18 |
| Raised by | Gate 0 task T00.01 (machine-readable error catalog) |
| Affects | Master Contract Appendix D; Repo 1 Appendix E, §39; `errors/error-catalog-v1.yaml` |
| Approvers | Architecture owner — pending |

## Context

T00.01 transcribed Repo 1 Appendix E into `errors/error-catalog-v1.yaml`: 80
codes, each with an HTTP status, a retry class from §39, and a user-facing
category from Repo 2 Appendix G where one exists.

Master Contract **Appendix D** also carries an error catalog, labelled a
*baseline*. Of its 26 codes, 21 appear in Repo 1 Appendix E unchanged. Five do
not, and they are not new codes — each is a **different name for a condition
Appendix E already covers**:

| Master Appendix D | Repo 1 Appendix E | Same condition? |
| --- | --- | --- |
| `AUTH_INVALID` | `AUTH_INVALID_TOKEN` | Yes — "Authentication failed" vs "Token invalid/expired/not for this audience" |
| `SENDER_IDENTITY_NOT_AUTHORIZED` | `SUBMISSION_SENDER_NOT_AUTHORIZED` | Yes — Master §23.2 itself uses the `SUBMISSION_` form |
| `TOO_MANY_RECIPIENTS` | `SUBMISSION_RECIPIENT_LIMIT` | Yes |
| `IDEMPOTENCY_CONFLICT` | `IDEMPOTENCY_KEY_REUSED` | Yes |
| `CONCURRENCY_CONFLICT` | `VERSION_CONFLICT` | Yes |

Two further divergences are values, not names. Master Appendix D's column is
headed "HTTP **class**" and several entries are ranges; where Appendix E picks a
value inside the range that is a narrowing, not a conflict. Two Appendix E values
fall **outside** the Master's range:

| Code | Master Appendix D | Repo 1 Appendix E |
| --- | --- | --- |
| `MAILBOX_QUOTA_EXCEEDED` | 409 | **507** |
| `PROVISIONING_FAILED` | 409/500 by caller | **503** |

## Problem

Master §0.2 places the Master Contract above the repository specifications and
forbids resolving a shared-contract conflict by invention. Master §0.5 lists
"canonical entity names and identifiers" among the things the Master
deliberately locks. So the five names cannot simply be discarded — but nor can
both spellings be published, because a client that branches on `code` would
have to handle two strings for one condition, which is exactly the ambiguity a
stable identifier exists to remove.

Master §23.2 is the decisive evidence that the Master's own Appendix D is not
self-consistent: §23.2's "stable examples" table uses
`SUBMISSION_SENDER_NOT_AUTHORIZED`, the Repo 1 spelling, against Appendix D's
`SENDER_IDENTITY_NOT_AUTHORIZED` twelve pages later.

## Options

**A. Publish Appendix E as-is; record the Master names as historical.** The
catalog carries 80 codes. Master Appendix D is annotated as a superseded
baseline in the next master revision. Consumers see one name per condition.

**B. Publish both spellings as aliases.** Every client must map two strings to
one condition forever, and a new client will inevitably branch on the wrong
one. Rejected on the same grounds Master §6.3 rejects tenant-ID synonyms.

**C. Rename Appendix E's codes to the Master's spellings.** Loses the
`SUBMISSION_` prefix grouping that Master §23.1 itself prescribes
(`SUBMISSION_*` is one of its named domains), and contradicts Master §23.2.

## Decision (proposed)

**Option A.** `errors/error-catalog-v1.yaml` publishes the Repo 1 Appendix E
catalog verbatim — 80 codes, no additions, no renames. The five Master
Appendix D names are recorded here as superseded and are not published.

`MAILBOX_QUOTA_EXCEEDED` keeps **507** and `PROVISIONING_FAILED` keeps **503**.
In both cases Appendix E is the more precise statement: 507 Insufficient Storage
names the condition exactly, and 503 paired with the `OPERATOR_ATTENTION` retry
class says *retrying will not help until someone acts* — which 500 does not.
Master Appendix D's HTTP column was never a precise mapping; it is headed "HTTP
class" and carries entries as loose as "401/403 by flow" and "409/202 status".

This decision does **not** amend the Master Contract. It records that the
machine-readable catalog follows Appendix E, and asks the architecture owner to
carry the correction into the next master revision under Master §0.4's
shared-breaking class.

## Consequences

- Gate 0 can tag `v0.1.0` with an unambiguous catalog.
- Master Appendix D and §23.2 disagree with each other today; whichever way this
  ADR is decided, one of them needs a revision. That revision is a
  master-contract change, not a schema edit, and is not a Gate 0 blocker.
- If the owner rejects Option A, `errors/error-catalog-v1.yaml` changes under
  the **shared breaking** class of Master §0.4 and every consumer re-pins.

## Evidence

`docs/reconciliation/error-catalog.md` — the full 26-row comparison.
