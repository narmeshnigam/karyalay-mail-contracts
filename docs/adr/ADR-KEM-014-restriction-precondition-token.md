# ADR-KEM-014 — Give OPS-BND-002's precondition somewhere to live on C.101/C.102

| Field | Value |
| --- | --- |
| Status | **PROPOSED 2026-08-24** |
| Date | 2026-08-24 |
| Raised by | karyalay-mail-ops `T00.07b`, confirmed against a running karyalay-mail |
| Affects | `openapi/operations-api-v1.yaml` (C.101, C.102) and a new internal read; karyalay-mail Appendix C cards for C.101/C.102 and §36; karyalay-mail-ops `internal/repo1client`; Appendix AI delta AI-01; Repo 4 AE #84, #85 |
| Approvers | Programme owner — **not yet reviewed** |

## Context

karyalay-mail-ops spec **OPS-BND-002** is a MUST:

> Every cross-repository mutation MUST carry `action_id`, `idempotency_key`,
> actor/service identity, `reason_code`, evidence references **and expected
> precondition/version**.

C.101 `POST /internal/v1/ops/restrictions` and C.102
`DELETE /internal/v1/ops/restrictions/{restriction}` are cross-repository
mutations — Ops requests, karyalay-mail decides and applies. **Neither defines
`ETag` nor `If-Match`, and neither the `Restriction` nor the
`RestrictionRequest` schema carries a version field.** There is nowhere for the
expected precondition to go.

**This was verified against the running service, not inferred.** `T00.07b`
records `VersionReturned` as false: karyalay-mail returns no version token on
C.101 at all, so a client could not send one back even if the header existed.

### What that costs, concretely

**A restriction requested against a stale view is applied, not refused.** Two
operators working from different views of the world both succeed. Operator A
reads a mailbox as unrestricted and requests `SEND_BLOCKED`. Operator B, in the
same minute, clears the restriction they can see. Whichever request lands second
wins, and neither is told anything happened. Ops has no way to say "apply this
only if the restriction state is still what I saw."

Idempotency does not cover this and should not be mistaken for covering it. An
idempotency key makes *the same request* safe to retry. A precondition makes *a
different actor's intervening change* visible. C.101 has the first and not the
second.

### The second half, which makes the first unfixable on its own

**There is no Ops-callable read of effective restrictions.** The internal
operations document defines exactly four operations: `requestRestriction`
(C.101), `clearRestriction` (C.102), `getResourceDiagnostics` (C.103) and
`submitSecurityEvent` (C.104). `getResourceDiagnostics` is the only read, and
its `ResourceDiagnostics` schema carries `state`, `desired_generation`,
`observed_generation`, `observation_status`, `open_operations`,
`recent_error_codes` and `correlation` — **no restrictions field.**

C.96 `listMailboxRestrictions` does exist and is not the answer: it is
`GET /api/v1/mailboxes/{mailbox}/restrictions` on the **public** control API,
under permission `mailbox.view`, a customer-principal route scoped to a single
mailbox. C.101 can restrict an `ORGANISATION`, a `DOMAIN` or a `MAILBOX`. Two
of those three cannot be read back by anybody.

**Adding `If-Match` without a read would produce a header no caller can
populate.** That is why this ADR proposes three changes and not one.

### And it is already failing an acceptance criterion

Repo 4 **AE #85** — *"outbound lock reversed → Repo 1 observed state verified"*
— is inside Phase 3's `AE #41–#90` exit criterion, and Phase 3 cannot satisfy
it because it cannot ask. **AE #84** — *"action HTTP timeout uncertain →
reconcile before retry"* — is answered today by idempotent replay rather than by
reading state, which is a different thing wearing the same result.

## Decision (proposed)

**Three changes, and all three are needed for any of them to be useful.**

### 1. A read of effective restrictions on the internal surface

New operation on `operations-api-v1.yaml`:

```
GET /internal/v1/ops/restrictions?resource_type={t}&resource_id={id}
  operationId: listEffectiveRestrictions
  permission:  platform.restrict
  200 -> { restrictions: [Restriction], … }
  ETag: the resource's restriction-state version
```

Scoped to a resource, covering all three `resource_type` values, returning the
same `Restriction` schema C.96 returns so the two do not drift. **The `ETag` on
this response is the token everything else depends on.**

This needs an Appendix C catalog id from karyalay-mail — C.116 at time of
writing — and **that is karyalay-mail's to assign, not this repository's.** The
harness reconciles every operation 1:1 against Appendix C, so a route published
here without a card fails the build, correctly.

### 2. A version token on the write path

- `Restriction` gains a **`version`** string, and C.101's `202` and C.102's
  success response gain the **`ETag`** header. The generator already defines
  that header component and uses it elsewhere.
- C.101 and C.102 gain **`If-Match`**, `required: false` — *honoured when
  supplied*, per Master §20.6's existing language for the optional form. A stale
  value returns **`412 VERSION_CONFLICT`**, which the error catalog already
  defines (`family: VERSION`, `retry_class: NON_RETRYABLE`). **No new error
  code is needed and none is proposed.**

**Optional, not required, and the reasoning matters.** Making `If-Match`
mandatory is the shape OPS-BND-002's "MUST" suggests, and it would break the one
existing caller on its first request: `karyalay-mail-ops`'
`internal/repo1client` sends no `If-Match` today and has no token to send until
§1 ships. The honest sequence is optional-and-honoured first, both sides build
against it, and *then* an ADR flips it to required once a caller exists that can
satisfy it. **A required header nobody can populate is not a stronger contract;
it is an outage.**

### 3. The generator, because these documents are generated

`operations-api-v1.yaml` is emitted by `tools/derive/gen_openapi.py`, which
attaches `If-Match` when the Appendix C card's Notes match
`If-Match required | Requires If-Match | ETag/precondition`, or when the method
is `PUT`/`PATCH`. C.101 is a `POST` and C.102 a `DELETE`, and neither card's
Notes say any of those things.

**So the fix is upstream of this repository, and that is the finding worth
recording.** `tools/derive/specmd.py` forbids the generator reinterpreting a
card, and rightly — teaching it a C.101 special case would be exactly that.
**The Appendix C cards for C.101 and C.102 must state the precondition**, in
karyalay-mail's specification, and then this repository regenerates and the
`412` appears automatically (the generator already adds `412` to the applicable
set whenever an `If-Match` parameter is present).

This makes the change **cross-repository by construction**: karyalay-mail's
Appendix C changes, this repository regenerates, karyalay-mail-ops re-pins.
That is the correct order and it is why this is an ADR rather than a patch.

## Consequences

**Wire compatibility: additive.** One new operation; two optional response
headers; one optional request header; one optional schema field. No existing
request becomes invalid and no existing response shape changes. **Version class:
a minor release.**

**Appendix C grows 115 → 116**, which is karyalay-mail's decision to take. The
harness's 1:1 reconciliation is what forces it to be taken rather than assumed.

**Two Repo 4 acceptance scenarios become satisfiable.** AE #85 gets the read it
needs; AE #84 gets a reconcile that asks rather than replays. Both sit inside
Phase 3's `AE #41–#90` range, which
[the phase-gate audit](../phase-gate-audit.md) records as PGA-21 — a criterion
that phase cannot meet with the contract as it stands.

**Delta AI-01 loses its second open defect.** The register will still show
AI-01 as PARTIAL afterwards, because the third remains: AI-01 asks for
"session/app-password revoke" and `restriction_code` is a closed enum of five
values, none of which ends a session. **Ops can block future authentication and
cannot end a session an attacker already holds.** That defect has been recorded
in two repositories' evidence files since 2026-08-23 and **no ADR is raised on
it** — it is named here so that closing this one is not mistaken for closing
AI-01.

**`karyalay-mail-infra` is unaffected**, which is worth saying because it is the
consumer furthest behind. Nothing here touches the executor surface.

## What was rejected

**Reuse `getResourceDiagnostics` by adding a restrictions field to
`ResourceDiagnostics`.** Cheaper, and it conflates two things that should not
share a cache lifetime or an ETag: a diagnostic snapshot is advisory and may be
stale by design, while a precondition token must be exact. A single ETag over
both would make an unrelated diagnostic change invalidate a valid precondition,
and operators would learn to retry through `412`s — which trains away the exact
signal this ADR exists to add.

**Make `If-Match` required immediately.** See §2. Correct in principle, an
outage in practice, and reachable in one further step once a caller exists.

**Route Ops through C.96.** It is a public-API customer-principal route under
`mailbox.view`, and it is mailbox-scoped. Using it would put Ops on the customer
surface and still leave organisation- and domain-level restrictions unreadable.

**Add a new error code for a stale precondition.** `VERSION_CONFLICT` (412,
`NON_RETRYABLE`) already exists and means exactly this. ADR-KEM-005 exists
because the catalog grows by invention otherwise.

## References

- karyalay-mail-ops spec §2, **OPS-BND-002**.
- karyalay-mail-ops `docs/evidence/phase-00/T00.07b-repo1-client.md` — the live
  run; `VersionReturned` false against the real service.
- karyalay-mail §36 (restrictions), Appendix C cards C.101, C.102, C.96.
- [ADR-KEM-013](ADR-KEM-013-idempotency-key-header-pattern.md) — the other
  open defect on the same two operations.
- [ADR-KEM-012](ADR-KEM-012-ops-executor-contracts.md) — the precedent for
  moving a rule from prose into schema so neither side can drift back.
- [`docs/phase-gate-audit.md`](../phase-gate-audit.md) — PGA-21, the Phase 3
  exit criterion this blocks.
- [`docs/registers/delta-register-v1.yaml`](../registers/delta-register-v1.yaml)
  — delta AI-01 and its three open defects.
