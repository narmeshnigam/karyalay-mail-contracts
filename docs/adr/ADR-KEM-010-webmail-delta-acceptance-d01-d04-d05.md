# ADR-KEM-010 — Accept webmail deltas D-01, D-04 and D-05 into the contract

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** |
| Date | 2026-08-22 |
| Raised by | Wave 4 start; correction of the BUILD-ORDER blocking matrix (commit `ca4fa34`) |
| Affects | Repo 1 Appendix C (grows 107 → 114); Repo 2 Appendix N, Appendix S flags; contracts `v0.2.1` → `v0.3.0`; all four consumer pins |
| Approvers | Programme owner — accepted 2026-08-22 |

## Context

Repo 2's Appendix N registers fifteen cross-repository contract deltas. Seven of
them block a task: **D-01, D-02, D-03, D-04, D-05, D-07, D-13**. Until
2026-08-22 the BUILD-ORDER blocking matrix recorded none of the seven. It named
D-11/12/14/15 — four deltas that block no task — and offered "ship flagged OFF
(§60 permits)" as the escape hatch.

That hatch is sound for those four, because each degrades to a working fallback
inside webmail alone. It does not reach the seven. A feature flag cannot be
turned on against an endpoint that does not exist, and Appendix N's own
governance is explicit:

> "They are not authorization for Agent 2 to invent production APIs."

Three of the seven block **Wave 4**: D-01 (threaded inbox, T01.09), D-04
(personal contacts, T04.05) and D-05 (organisation directory search, T04.06).
The remaining four block Wave 5.

## Decision

**D-01, D-04 and D-05 are accepted into the contract as catalog operations
C.108–C.114**, published in `v0.3.0`.

D-02, D-03, D-07 and D-13 remain **deferred**. They are not refused; they are
undecided, and Wave 5 cannot open its Repo 2 Phase 5 without deciding them —
four of that phase's seven tasks depend on them. Recording that here so the
decision is scheduled rather than rediscovered.

## Ownership resolved

Two of the three had ambiguous owners in Appendix N. Both resolve to Repo 1, and
the reasoning matters because it changes the cost.

**D-04 — "karyalay-mail or dedicated Karyalay contacts service."** No contacts
service exists in this programme and none is planned. Contacts are therefore
Repo 1's, stored in its canonical persistence and scoped per mailbox principal.

**D-05 — "Karyalay identity/directory + mail gateway."** The identity provider
is the Keycloak instance T03.08 builds, and it exposes no directory API this
contract may depend on. But Repo 1 already holds the data: `C.4
listOrganisationMembers` returns the `Member` set for an organisation. **D-05 is
therefore a search projection over data Repo 1 already owns, not a federation
path to the IdP.** That is the cheap reading and it is also the correct one —
routing directory search through the IdP would make every autocomplete keystroke
a dependency on the single point of failure Wave 3 already flagged.

Recording this because the opposite reading would have made D-05 a Wave 5 item
gated on the IdP being live, which is not what the delta needs.

## The operations

Seven operations. Appendix C is exhaustive by invariant, so these are the whole
of what the three deltas may expose.

| ID | Document | Operation | Method / path | Response |
| --- | --- | --- | --- | --- |
| **C.108** | mailbox | `listMailboxThreads` | `GET /mailbox/v1/mailboxes/{mailbox}/threads` | `ThreadSummary`, cursor page |
| **C.109** | mailbox | `listMailboxContacts` | `GET /mailbox/v1/mailboxes/{mailbox}/contacts` | `Contact`, cursor page |
| **C.110** | mailbox | `createMailboxContact` | `POST /mailbox/v1/mailboxes/{mailbox}/contacts` | `Contact`, 201 |
| **C.111** | mailbox | `getMailboxContact` | `GET /mailbox/v1/mailboxes/{mailbox}/contacts/{contact}` | `Contact` |
| **C.112** | mailbox | `updateMailboxContact` | `PATCH /mailbox/v1/mailboxes/{mailbox}/contacts/{contact}` | `Contact` |
| **C.113** | mailbox | `deleteMailboxContact` | `DELETE /mailbox/v1/mailboxes/{mailbox}/contacts/{contact}` | 204 |
| **C.114** | public-control | `searchOrganisationDirectory` | `GET /api/v1/organisation/directory` | `DirectoryEntry`, cursor page |

### D-01 — the capability already exists; the endpoint does not

`C.80 getThread` returns a `Thread` — a thread projection over `MessageSummary`,
with the standing note that "thread identity is an application projection, not
an authoritative mail storage key." Repo 1's T05.07 built the threading and
search translator behind it.

C.108 is the **list** form of that same projection, so the client stops
re-threading message pages in the browser. `ThreadSummary` must be consistent
with `Thread`, not a parallel invention:

```
ThreadSummary
  thread_ref        string                 opaque, same projection as Thread
  subject           string|null
  participants      AddressDisplay[]       bounded; see below
  message_count     integer
  unread_count      integer
  latest            MessageSummary         the newest message in scope
  has_attachments   boolean
```

Query parameters: `folder_ref`, `q`, `cursor`, `limit` — the union of C.70's
folder scope and C.81's search scope, because Appendix N asks for both and a
thread list that cannot be scoped to a search is not the one the Inbox needs.

**`participants` is bounded**, like every array in this contract. An unbounded
participant list on a long thread is a payload amplification an attacker
controls by replying.

### D-04 — contacts are per mailbox principal, not per organisation

```
Contact
  contact_id        uuid
  display_name      string|null
  addresses         AddressDisplay[]       normalized, bounded
  organisation      string|null
  notes             string|null
  version           string                 ETag; If-Match required on C.112
  created_at        timestamp
  updated_at        timestamp
```

`C.109` carries an optional `q` for search rather than adding a second
operation. One operation with a filter is what the rest of this catalog does
(`C.81`), and two would need a rule for which one a client uses when `q` is
empty.

**Tenant and user isolation is the whole security property here.** A contact
list is a social graph; leaking one across mailbox principals inside the same
organisation is a privacy incident, not a bug. The `{mailbox}` path segment is
authoritative and §8.1's visibility step applies before the permission step, so
a contact belonging to another principal answers not-visible rather than
forbidden.

### D-05 — a projection, with a floor on the query

```
DirectoryEntry
  member_id         uuid
  display_name      string
  primary_address   string
  role              string|null
```

Deliberately narrower than `Member`. A directory autocomplete needs a name and
an address; it does not need entitlements, membership dates or role history, and
every field not returned is a field that cannot leak.

Three constraints Appendix N names explicitly, all of them load-bearing:

- **Minimum query length.** A one-character query returns the whole directory,
  which is a CSV export with extra steps.
- **Visibility policy.** Organisation membership is the boundary; a member of
  one organisation may not enumerate another's.
- **Rate limit.** Endpoint-specific, per Master §20. Autocomplete fires on
  keystrokes and is the most trivially abusable read surface in the catalog.

## Implementation order — and the assertion that enforces it

The generators in this repository are **transcription tools**. `specmd.py` says
so:

> "Nothing here may add, drop or reinterpret a row — divergence from the
> appendix is a bug in the generator, never a fix applied to the contract."

They read `karyalay-mail/docs/spec/repository-spec-v1.0.md` Appendix C directly,
and `gen_openapi.py` hard-asserts the count in two places — line 650
(`"Appendix C parsed to %d cards; the appendix preamble states 107"`) and line
688 (`"emitted %d operations; expected 107"`) — plus a two-way diff between the
parsed cards and the `OPS` binding table.

**So this contract cannot be changed from inside this repository.** The order is
forced, and that is the design working:

1. **Repo 1** — Appendix C gains seven cards; the preamble count 107 → 114.
2. **Contracts** — `openapi_ops.py` gains seven bindings, `openapi_schemas.py`
   gains `ThreadSummary`, `Contact` and `DirectoryEntry`, and both `107`
   assertions in `gen_openapi.py` become `114`.
3. **Contracts** — `package.json` version → `0.3.0` (the one source; see
   `tools/derive/version.py`), then `npm run derive && npm run check`, then tag.
4. **Repo 1** — implement C.108–C.114 with contract tests.
5. **Repo 2** — Appendix N status → accepted; flip `webmail_thread_list_v1`,
   `webmail_contacts_v1`, `webmail_org_directory_v1` per Appendix S; build
   T01.09, T04.05, T04.06.

## Also in `v0.3.0` — a dropped idempotency requirement

Found while Repo 4 built its envelope layer against the pinned contract, and
folded in here because it ships in the same version.

`gen_openapi.py` decided whether `Idempotency-Key` was mandatory by regexing the
card's prose **Notes** line for the literal token `Idempotency-Key required`.
The structured **Idempotency** row — the normative one — was never read, because
it is byte-identical boilerplate on all 107 cards: *"Required for POST
create/final-send/provisioning/restriction operations."* It names the classes
without saying which class a card is in, and the Notes line is where a card says
that, in prose.

Two cards state the requirement in a phrasing the regex missed:

| Card | Notes says | Class | Emitted |
| --- | --- | --- | --- |
| **C.100** `reportProvisioningResult` | "Generation and idempotency validation **mandatory**" | provisioning | `required: false` |
| **C.101** `requestRestriction` | "reason, evidence/case ref, **idempotency required**" | restriction | `required: false` |

Both are replay-sensitive mutations arriving from another service — the exact
case Master §20.5 exists for. C.101 is the sharper one: its card says *required*
in as many words, **and** its class is named explicitly in the row above. It
emitted an optional header on both counts.

The regex now matches the requirement however the card phrases it. It
deliberately does **not** match a bare "idempotent", which is a claim about the
operation's semantics rather than about the caller's duty to send a key.
Widening it that far would put a mandatory header on C.75's flag mutation on the
strength of the words "idempotent flag semantics".

**Four cards sit in that ambiguous set and are not resolved here** — C.16
("Idempotent; audit reason required"), C.29 ("Reason mandatory; idempotent"),
C.75 ("idempotent flag semantics"), C.77 ("Same batch/idempotency rules"). Each
says the operation *is* idempotent without saying a key is required, and
deciding that in the generator would be precisely the reinterpretation
`specmd.py` forbids. **This is a question for the Appendix C owner**, not a
defect with an obvious fix.

A confirmation the change is right: the generator emits error responses from
`errors/error-catalog-v1.yaml`, and making the key required pulled
`IDEMPOTENCY_KEY_REQUIRED` into both documents automatically. The code was
already in the catalog; neither document had an operation that could return it.

**This half is breaking, not additive** — a client omitting the header now gets
a 400. It is free today and will not be later: Repo 1 has implemented neither
C.100 nor C.101, and Repo 4's `repo1client` is empty by design. There is no
deployed consumer to break, which is the argument for doing it now rather than
discovering it after one exists.

Repo 1's T07.01 already compensates independently — its progress note records
that "idempotence is at the store, by (resource, code, source), not only at the
HTTP idempotency key", because an Ops retry with a fresh key would otherwise
stack a duplicate. The contract now says what that implementation already does.

## Consequences

**`v0.3.0` is additive and shared-compatible.** Seven new operations, three new
schemas, no existing wire shape altered. `v0.2.1` remains published and
immutable. Consumers may re-pin when convenient rather than immediately — only
Repo 2 needs `v0.3.0` to build the three unblocked tasks, and Repo 1 needs it to
be the thing it implements against.

**Four consumers re-pin eventually.** Each pin names the tag, its commit SHA and
a SHA-256 per vendored artifact, so the upgrade is mechanical and the digests
prove nothing else moved.

**Repo 1 grows a contacts module it did not have.** This is the real cost of
D-04 and it is not small: canonical persistence, per-principal isolation, ETag
concurrency, and the address normalisation the delta requires. D-01 and D-05 are
projections over data Repo 1 already holds; D-04 is a new resource.

**The four deferred deltas are now scheduled, not silent.** D-02 (change feed),
D-03 (spam feedback), D-07 (remote-image proxy) and D-13 (browser
notifications) block four of Repo 2's seven Phase 5 tasks. Wave 5 opens on that
decision. D-02 in particular is already half-answered: ADR-KEM-002 established
that IMAP IDLE is available upstream, so the feed is implementable once a
canonical endpoint ships.

## Related

- [ADR-KEM-002](ADR-KEM-002-mailbox-gateway-transport.md) — pooled IMAP and the
  master user; the upstream capability D-02 will need.
- [BUILD-ORDER §5](../BUILD-ORDER.md) — the blocking matrix this ADR follows
  from, corrected the same day.
- Repo 2 `docs/reference/feature-flags.md` — the delta register and flag
  defaults.
- Repo 2 `WEB-ADR-017` — delta flag governance and naming.
