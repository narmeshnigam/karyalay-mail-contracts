# ADR-KEM-011 — The session bootstrap endpoint Appendix N never registered

| Field | Value |
| --- | --- |
| Status | **PROPOSED** |
| Date | 2026-08-22 |
| Raised by | Repo 2 Wave 4 build (T00.05, T04.01, T04.02) |
| Affects | Repo 1 Appendix C; Repo 2 §7, Appendix F, Appendix G; contracts `v0.3.0` → `v0.4.0` |
| Approvers | — awaiting programme owner |

## The finding

Repo 2's specification requires a session bootstrap and names it in four places:

- **§4:** *"**Consumes:** authentication/session bootstrap; mailbox/folder/message/thread/search/draft/send APIs…"*
- **Appendix F:** the `AppBootstrap` machine — `START → SESSION_LOADING → CONTEXT_LOADING → READY | SIGNED_OUT | FATAL_CONFIG | DEGRADED`, keyed on *"401/re-auth, malformed config, **no mailboxes**"*.
- **§18 mailbox switcher:** *"Shows only mailboxes returned by **authorized session/bootstrap**."*
- **§56 build order:** *"Generated contracts → **auth/bootstrap** → mailbox context → folders/list…"*

**No operation in the catalog returns it.** C.61 `listMyMailSessions` and C.62 `revokeMyMailSession` are the user's *IMAP and SMTP client* sessions — the ones a phone mail app holds, which a user lists and revokes. They are not the browser session, they do not answer "who am I", and they cannot answer "which mailboxes may I open".

**Appendix N did not register this as a delta.** Fifteen are registered, D-01 through D-15; none is a session or identity bootstrap. This is a sixteenth, and it is more foundational than any of them — Appendix F's state machine cannot reach `READY` without it.

## What the client needs

Repo 2 has already had to define the shape locally, in `src/domain/identity/session.ts`, to build its state machine against:

```
Session
  subject           string          OIDC subject
  organisation_id   uuid
  mailboxes         [{ ref, address, delegated }]   every mailbox this session may act on
  permissions       string[]
  locale            string
  server_time       timestamp       §7: the client's clock is wrong often enough to matter
  capabilities      map<string, bool>
```

`mailboxes` is the load-bearing member. Delegation means a session may act on more than one, and §18 makes the switcher's contents *exactly* this list — so a client that cannot read it either shows nothing or guesses.

`server_time` is in the spec for a stated reason: an expiry computed against a skewed local clock either signs a user out early or trusts a dead session.

## What its absence costs today

Three consequences, all of them observed in the Wave 4 build rather than predicted:

1. **A001–A005 cannot be automated at all.** There is no endpoint to drive, so five of Repo 2's Phase 0 acceptance criteria have no test. T00.05 is ◎ rather than ☑ on exactly this.

2. **The capability ledger infers permissions from `AUTHZ_FORBIDDEN`.** T04.01 has no permission list to read, so it records denials as it discovers them. Repo 2's own Appendix G calls the failure mode out — *"no repeated retry"* — because without a record a settings section that 403s is offered again on every visit and 403s again every time. The ledger is a correct mitigation of a gap that should not exist: **a permission check turned into a polling loop.**

3. **Forwarding's loop check has no addresses to compare against.** `loopRisk(address, ownAddresses)` is passed `[]`, so the one check that stops a customer forwarding a mailbox to itself is inert.

## Proposed shape

One operation. `GET /api/v1/me/session` → `Session`, permission `authenticated`, no request body, ETag optional.

It belongs in the **public-control** document, beside C.61/C.62 under a `Sessions` tag, and it is a read of state Repo 1 already holds: the OIDC subject from the token, the organisation from `TenantContext`, the mailboxes from the access-grant tables C.34–C.36 already serve, and the permissions from the §18 policy engine that already computes them per request.

**It invents no data.** That is the argument for it being cheap: every member above is something Repo 1 can already answer, assembled into one response so the client stops deriving it from failures.

## Alternatives considered

**Decode the OIDC token client-side.** Gets `subject` and `locale` and nothing else. Mailboxes and permissions are not in the token and must not be — §18's five-factor decision is computed per request against live state, and a token minted before a grant was revoked would authorise a mailbox the server would refuse.

**Leave the capability ledger as the mechanism.** It works, and it is well built. But it can only learn what a user is *denied*, one 403 at a time, and it cannot populate the mailbox switcher at all. It is a mitigation, not a design.

**Defer to Wave 5 with D-02/D-03/D-07/D-13.** Those four block features. This one blocks a state machine the whole client is built on, and every phase built without it accumulates more code shaped around its absence.

## Consequences if accepted

`v0.4.0`, additive. One Appendix C card (C.115), one schema, one endpoint in Repo 1 reading tables it already owns. Repo 2's T00.05 becomes automatable, T04.01's ledger becomes a cache rather than the source, and forwarding's loop check gets its comparison set.

If **not** accepted, record why against A001–A005 so the next reader does not rediscover this — Repo 2 cannot close those criteria and should stop carrying them as outstanding.

## Related

- [ADR-KEM-010](ADR-KEM-010-webmail-delta-acceptance-d01-d04-d05.md) — the seven registered deltas accepted in `v0.3.0`, and the four still deferred.
- Repo 2 `docs/spec/repository-spec-v1.0.md` §4, §18, §56, Appendix F, Appendix G.
- Repo 2 `src/domain/identity/session.ts` — the shape, already written against the gap.
