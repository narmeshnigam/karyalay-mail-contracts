# Watched failures — the deferral maturity check

**Date:** 2026-08-24 · **Check:** `tools/validate/deferrals.mjs`, five checks in
`npm run validate` · **Repository version at the time:** `v0.5.0`

A check nobody has watched fail is a check nobody knows works. START-HERE §6.4
records three production failures that every structural gate passed, because
each gate inspected a setting and none asked whether the thing the setting
describes actually happens. That argument applies to a new check on its first
day as much as to a converged host.

So before this check was committed it was made to fail four ways, and each
failure was read to confirm it named the right thing.

## 1. The situation the check exists for — ADR-KEM-009 replayed

Two ways. First as a fixture, permanently: `auditMaturity()` is asserted
against `tools/validate/fixtures/deferral-register-at-v0.4.0.yaml` — the
register as it would have read the day `v0.4.0` was tagged — and must report
exactly seven violations there and at `v0.2.0`, none of the seven at `v0.1.0`,
and none against a row that was delivered on time. That assertion is itself one
of the checks, so the negative case runs on every `npm run check` rather than
having been run once.

Second, live: `AI-04` was set back to `OPEN` in the real register and the
harness run.

```
FAIL no deferral's target tag has passed with the deferred thing absent
     AI-04 was deferred to v0.2.0 by ADR-KEM-009 on 2026-08-18, this repository
     is at v0.5.0, and it is still OPEN. The target has been reached or passed
     and the deferred thing does not exist. Owner: karyalay-mail-infra;
     owning task: none.
FAIL every open deferral has an owner, and the ownerless count only falls
     AI-04 names karyalay-mail-infra as its owner and no task that raises it;
     that is the shape ADR-KEM-009 closed a task without creating
```

This is the message that would have appeared on 2026-08-18, and again on
`v0.3.0` and `v0.4.0`. Ten Repo 4 tasks were blocked for six days instead.

## 2. Status is not capability — a row claiming delivery of an absent operation

`AI-09`'s `satisfied_by` operation id was changed to one the document does not
define.

```
FAIL every honoured deferral resolves to a real operation or schema
     AI-09 claims executeMaintenanceActionX in openapi/infra-executor-api-v1.yaml;
     the document defines no such operation
```

The check resolves the `operationId` inside the OpenAPI document and the `$id`
inside the schema file. A register row saying `HONOURED` proves nothing by
itself, which is the whole lesson of §6.4.

## 3. The ownership ratchet — a new ownerless deferral added quietly

A fabricated `D-99` with `decision_owner: UNASSIGNED` was appended.

```
FAIL every open deferral has an owner, and the ownerless count only falls
     6 deferrals have no decision owner (D-02, D-03, D-07, D-13, OPEN-002, D-99)
     against a baseline of 5. The baseline is a ratchet: assign an owner, or
     lower it -- do not raise it.
```

Five ownerless deferrals exist today and the check cannot make them owned. What
it can do is stop a sixth appearing without somebody deliberately raising the
number, and print the five on every run so they are not forgotten again. The
baseline also fails when it is *too high*, so removing a deferral without
lowering it is caught as well.

## 4. A deferral with no target at all

```
FAIL the deferral register is well-formed
     deferral D-98 names no target at all -- a deferral with no target can never
     mature and can never be caught, which is the ADR-KEM-009 failure with the
     tag removed
```

## What this check still cannot do

Only `target.tag` is comparable against a version. Six of the thirteen
deferrals on the register target a **wave** or a **gate**, and neither is a
value this repository holds, so no comparison can mature them. They are printed
on every run:

```
7 tag-targeted deferrals checked against v0.5.0; 6 NOT maturable by version
(D-02->wave 5, D-03->wave 5, D-07->wave 5, D-13->wave 5, OPEN-002->gate 2,
 KEM-003-FENCING->gate 2)
```

That is a real hole and it is stated rather than hidden. Four of those six —
D-02, D-03, D-07, D-13 — are the ADR-KEM-009 shape exactly: a target with no
owner, blocking four Repo 2 Phase 5 tasks, with a consumer waiting on each and
no task anywhere that raises the decision. Converting a wave target to a tag
target is a decision, not a tooling change, and it is the programme owner's.
