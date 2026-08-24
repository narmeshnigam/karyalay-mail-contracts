# Phase-gate audit — the ADR-OPS-024 defect class across all five repositories

**Created:** 2026-08-24 · **Owner:** Narmesh Nigam · **Status:** findings only,
no remediation applied · **Companion to:**
[BUILD-ORDER.md](BUILD-ORDER.md) ·
[ADR-OPS-024](../../karyalay-mail-ops/docs/adr/ADR-OPS-024-phase-0-ae-criterion-scope.md)

> **Custody, not authority.** This document lives in `karyalay-mail-contracts`
> because that is the one repository every other already consumes. It sits
> below all five levels of Master Contract §0.3 precedence, the same as
> BUILD-ORDER. **It is a report, not a decision.** Every finding names a
> criterion in somebody else's repository, and nothing here changes one.
> The remedy for each is an ADR in the owning repository, and that is the
> owner's call.

---

## 0. Why this exists

[ADR-OPS-024](../../karyalay-mail-ops/docs/adr/ADR-OPS-024-phase-0-ae-criterion-scope.md)
(ACCEPTED 2026-08-24) found that `karyalay-mail-ops` Phase 0's exit criterion —
*"Appendix AE scenarios #1–#40 (AUTH/SAFETY, EVENT/JOB) pass"* — **cannot be
satisfied by Phase 0's scope.** Four of the forty need capabilities §96's own
phase table assigns to Phases 1, 2 and 3. Its closing observation was left
undischarged, deliberately:

> "No other phase's AE block has been audited by asking which scenarios its
> deliverables can actually produce, and it would be surprising if this were
> the only one."

Nobody had audited another. This is that audit: **every phase-gate exit
criterion in all five repositories**, read against the phase table that assigns
capabilities to phases.

It would not have been surprising. **Neither repository the ADR did not cover
is clean, and the worst instance is not in the repository that found it.**

## 0.1 Method, and its limits

Two independent read-only passes, one over Repos 1 and 2, one over Repos 3 and
4, each reading:

1. every `tasks/README.md` and every `tasks/phase-*/README.md`;
2. the exit criteria **and** — for Repos 3 and 4, where the roll-up rule reads
   it — the `## Phase-gate evidence checklist`, which is the gate that actually
   binds;
3. each repository's own spec phase table (Repo 1 §51, Repo 2 §59, Repo 3 §81,
   Repo 4 §96) as the authority on which phase owns which capability;
4. for every range-shaped criterion, the enumerated members grepped
   individually against that repository's test and evidence trees.

**What "verified absent" means here.** It means the identifier appears nowhere
in the repository's test tree. It does **not** mean no assertion of the
behaviour exists under another name — several are asserted and unmapped, and
that distinction is preserved in every finding below. Where a repository's own
acceptance appendix makes the identifier the contract (Repo 4 spec §I.1-equivalent
requires CI to map acceptance IDs to test names), unmapped is the operative
failure regardless.

**Sibling task trees were moving while they were read**, and this must be
carried with every number in this document. Four other agents were working in
those repositories on 2026-08-24. `karyalay-webmail` had uncommitted work in
progress (`T01.09`, the threaded inbox on delta D-01) which will change Phase
1's coverage; `karyalay-mail-infra` and `karyalay-mail-ops` both had task
READMEs written within the reading window; `START-HERE.md` changed mid-read.
Figures are as of the working tree on 2026-08-24 and should be re-derived
before any of them is acted on.

**Nothing in a sibling repository was edited.** No task file, no phase README,
no `contracts/PIN.json`. The report is the artifact.

---

## 1. The two defect shapes

**Shape A — scope-impossible.** A phase's exit criterion demands a capability
that the same spec's phase table assigns to a later phase, to another
repository, or to infrastructure that does not exist and no task builds. A gate
that can never be met is a gate that eventually gets ticked anyway, which is the
argument ADR-OPS-024 makes and the argument
[T00.05's false ☑](../../karyalay-mail-ops/tasks/phase-00-contracts-foundation/T00.05-jobs-events-engine.md)
proved.

**Shape B — range-shaped.** A criterion written as a range — `A001–A007 pass`,
`AE #1–#40`, `W-170–W-187`, `H1–H9` — which reads as covered when some members
have no test at all. This shape has already hidden two untested scenarios in
Repo 2, which is what put it in this audit's brief. It hides far more elsewhere.

The two compound: a range is also the most reliable way to import a later
phase's work without noticing, because nobody reads a range member by member.

---

## 2. Summary

| # | Repo | Phase | Shape | One line |
| --- | --- | --- | --- | --- |
| **PGA-01** | 1 `karyalay-mail` | 1 | A | "Transaction/outbox tests green" needs a NATS broker no repository has built |
| **PGA-02** | 1 | 2 | A | AUTH-004 needs C.5, which Phase 4 delivers — already realised and worked around |
| **PGA-03** | 1 | 3 | A | DKIM-001/002 need an Infra key service that exists in no repository |
| **PGA-04** | 1 | 4 | A (weak) | C.33 usage needs the Phase 5 mailbox port — but §51.1 pre-authorises the fake |
| **PGA-05** | 1 | 7 | B | "AUD/OBS acceptance scenarios" — AUD-002 and OBS-002 have no test |
| **PGA-06** | 1 | 8 | A+B | "All 62 Appendix I scenarios" — 18 unmapped; DoD requires a staging environment |
| **PGA-07** | 2 `karyalay-webmail` | 1 | A+B | `A008–A044` imports six scenarios §59 gives Phases 3 and 5; A021/A022/A035 untested |
| **PGA-08** | 2 | 5 | A+B | `A093–A096, A098–A102` includes two blocked deltas and two Phase 6 manual-AT rows |
| **PGA-09** | 2 | 3 | A | Reconciliation half needs a lookup by `Idempotency-Key` that C.91 does not offer |
| **PGA-10** | 2 | 6 | A+B | `A001–A120` — 27 unmapped; staging E2E has no deployed API to run against |
| **PGA-11** | 3 `karyalay-mail-infra` | 3 | **A — the worst** | Gate requires a **staging host the programme owner decided not to build** |
| **PGA-12** | 3 | 5,7,9,10,11 | A | Five more phases carry acceptance criteria depending on that same absent host |
| **PGA-13** | 3 | 10 | A | Gate demands two Appendix AL rows §81 and Phase 11's own task index put in Phase 11 |
| **PGA-14** | 3 | 10 | A | Same gate pulls in AL rows owned by Repos 1 and 4, and an "at least two MX" row no phase delivers |
| **PGA-15** | 3 | 4 | A | OpenBao quorum + snapshot restore, on hosts that exist in no inventory |
| **PGA-16** | 3 | 6 | A | "Role minimums met per spec §7" makes one phase responsible for fourteen roles' sizing, incl. a Phase 7 capability |
| **PGA-17** | 3 | deliverability workstream | A | Its gate requires AK-13 evidenced; Phase 5's gate says AK-13 only *becomes testable* in Phase 5 |
| **PGA-18** | 3 | 4,5,6,9,11 | **B — the worst** | **170 of Appendix W's 242 scenarios are named nowhere in the repository** |
| **PGA-19** | 3 | 7 | B | `H1–H9` hides **H4, H6, H7** — the three invariants ADR-KEM-003 exists to enforce |
| **PGA-20** | 3 | workstream | B | The AK gate accounts for 24 of Appendix AK's 28 rows |
| **PGA-21** | 4 `karyalay-mail-ops` | 3 | A | `AE #41–#90` includes #85 and #68, which need Repo 1 contract surfaces that do not exist |
| **PGA-22** | 4 | 4 | A | `AE #131–#155` includes #148 and #149, produced by Phase 5; DR-005 needs a MariaDB host |
| **PGA-23** | 4 | 5 | A | `AE #156–#180` reaches into Phase 2, Repo 3 Phase 7, and a second MX |
| **PGA-24** | 4 | 7 | A | Appendix AF's launch gate requires validation **on staging** — see PGA-11 |
| **PGA-25** | 4 | 1 | A (inverted) | Criterion claims AE #15, which Phase 0 already delivers |
| **PGA-26** | 4 | 3 | B | 17 AE scenarios named in no task at all — including all four ATO/containment rows |
| **PGA-27** | 4 | — | B | **#203–#241 are claimed by no phase** before Phase 7's blanket "all 241" |
| **PGA-28** | 4 | 1 | B | ADR-OPS-024 moved #13/#14 into the criterion and **not into the gate checklist** |
| **PGA-29** | 3 | 10 | B | "AL.1 steps 1–8" against an AL.1 that has nine steps — recorded, not asserted |
| **PGA-30** | 4 | 3 | A? | §25 anomaly scenarios #58/#59/#64 may belong to Phase 6 — **not determined**, see §10 |

**Clean:** Repo 1 Phases 0, 5, 6 · Repo 2 Phases 0, 2, 4 · Repo 3 Phases 0, 1,
2, 8, 9, 11 · Repo 4 Phases 2, 6. Detail in §7 — the clean ones matter, because
two of them are the patterns worth copying.

---

## 3. The finding that changes the most: PGA-11

**`karyalay-mail-infra` Phase 3's gate requires a host the programme owner
decided not to build.**

> ☐ Control-plane, **staging** and IdP hosts converge from Ansible with a clean
> second run (spec §53; ADR-INF-033)

`T03.07-control-plane-staging-hosts.md` records the decision verbatim: *"The
programme owner elected to provision cp1 and idp1 in production and defer
staging… **This task therefore closes PARTIALLY, and is not to be ticked ☑.**"*
`inventory/environments/staging.yml` carries RFC 5737 placeholder addresses and
its own header says neither staging host has been provisioned. START-HERE §6
item 9 records the deferral as standing.

**Under the roll-up rule that phase can therefore never be ☑.** Not "is not yet"
— *cannot be*, by a decision that is not going to be reversed. The repository
knows both halves and has never put them together: Phase 0's README says
"T03.07/T03.08 remain ◐ **by design** … and must not be ticked ☑" without
drawing the conclusion that the gate above them is now unmeetable as written.

This is ADR-OPS-024's defect in its purest form, and it is **worse** than the
one that ADR was written for. Phase 0's four scenarios were produced by later
phases; they arrive eventually. Staging arrives never.

**And it propagates.** Five more phases carry acceptance criteria naming
staging (PGA-12): Phase 5's expired-cert chaos, Phase 7's quarterly live
failover drill, Phase 9's interop certification and recurring chaos, Phase 10's
staging→production artifact promotion, Phase 11's independent-synthetics test.
`T03.07` anticipated exactly two of these — it records that "§6 promotion is
unrehearsed" and that "the cross-origin and TLS rehearsals have nothing to run
against" — but the cost was written into T03.07 and never propagated into the
criteria that depend on it. And it crosses repositories: **Repo 4's Phase 7
launch gate (PGA-24)** requires Appendix AF's Diagnostics row, *"Message
trace/DNS/mailbox/queue workflows validated **on staging**"*. No Repo 4 phase
can produce a staging environment; Repo 3 owns machines under ADR-INF-033 and
has decided not to build this one.

**What the owner has to decide, and it is one decision.** Either staging is
provisioned, or every criterion that names it is rewritten to say what is
required *without* it — and where the answer is "nothing adequate", that is the
recorded cost of the deferral rather than a checkbox that stays open forever.
Seven phases across two repositories wait on the same sentence.

---

## 4. The finding that hides the most: PGA-18 and PGA-19

**170 of Appendix W's 242 scenarios are named nowhere in `karyalay-mail-infra`
— not in a task, not in a test.**

Repo 3's gates cite Appendix W as ranges, three of them softened further with
the word *"area"*: `W-055 area`, `W-106–W-120 area`, `W-170–W-187 area`, plus
Phase 9's *"Appendix W first full pass recorded, no waivers"* and Phase 11's
*"Final Appendix W run green"*.

Enumerating W-001…W-242 and grepping each: **72 are named individually, 170 are
not.** The endpoint pattern is the tell — tasks name W-105, W-106, W-120,
W-121, W-138, W-139, W-170, W-187, W-188, W-202: the *boundaries* of the
ranges, and nothing between them. Concretely, `W-106–W-120 area` never names
W-107 through W-119 — thirteen scenarios covering DANE valid TLSA, DANE
mismatch, DNSSEC-bogus, MTA-STS enforce/mismatch/cert-mismatch/cached/expired,
TLS-RPT, cert renewal and the expired-cert synthetic. `W-170–W-187 area` never
names W-171 through W-186 — sixteen covering Galera writer loss, minority
partition, total quorum loss, SST/IST, PITR, Redis primary loss, NATS poison
message, OpenBao sealed state and internal cert auto-renew.

**PGA-19 is the sharp one.** Phase 7's gate reads *"Appendix AG invariants
**H1–H9** conformance tests pass"*. Of the nine, **H4, H6 and H7 have zero
occurrences anywhere in the repository outside the specification**:

| | |
| --- | --- |
| **H4** | "Promotion requires quorum **and positive fencing evidence** for the previous writer when previous writer state is uncertain" |
| **H6** | "A DRBD split-brain signal disables automatic merge/promotion" |
| **H7** | "A new standby is not counted in RPO-0 availability until fully UpToDate and health-checked" |

H4 and H6 are the two invariants **[ADR-KEM-003](adr/ADR-KEM-003-mailbox-storage-ha-ceiling.md)**
exists to enforce — *no HA claim without proven fencing* — and H7 is what stops
a half-synced standby being counted as redundancy. All three are invisible
behind the string `H1–H9`, in a gate that will read as satisfied the moment six
of nine are green.

This is the exact failure START-HERE §6.4 describes, one layer up: the gate
inspects a range and never asks whether each thing the range describes actually
happens.

---

## 5. Findings by repository

Each entry: the verbatim criterion, the capability it needs, where the spec
assigns that capability, and who actually owns it.

### 5.1 `karyalay-mail` (Repo 1)

**PGA-01 — Phase 1 (shape A).** *"'Tenant isolation and transaction/outbox
tests green': TEN-001/TEN-002 and the atomic state+audit+outbox transaction
tests (EVT-001/EVT-002) pass in CI."* Appendix I's EVT-001 requires *"Outbox
remains pending; API state durable; later publication"* and EVT-002 *"Publisher
crashes after NATS ack…"* — both need a broker to ack. §2 puts NATS outside this
repository, and its own `UnavailableBroker` is annotated *"Replaced by a
JetStream adapter in Wave 3, when karyalay-mail-infra has a NATS cluster (its
Phase 6)"*. It is the only `EventPublisher` implementation in the repository and
it throws on every publish. **Owner: `karyalay-mail-infra` Phase 6.**

**And the aggravating half, which is a separate defect worth its own line.**
The tests offered as evidence do not test the scenarios. `AtomicMutationTest`'s
methods are `evt_001_state_audit_and_outbox_all_commit_together` and
`evt_002_a_failure_after_the_outbox_write_rolls_back_all_three` — transactional
atomicity. Appendix I's EVT-001/EVT-002 are broker-outage and
publisher-crash-after-ack. **The identifiers match and the scenarios do not.**
The phase README ticks `[x] EVT-001, EVT-002 green` and three lines later admits
"no scheduler runs the relay, and the NATS adapter behind `EventPublisher` is
unwritten". A mapping check that verifies *the named test exists* cannot catch
this; only reading the scenario text can. **This is a third defect shape and it
is discussed in §6.**

**PGA-02 — Phase 2 (shape A, already realised).** AUTH-004 is *"attempt to
remove last org_owner"*, which needs C.5 `PUT …/members/{subject}/roles` — §27
Customer Administration, delivered by Phase 4's T04.01. The repository states it
outright in three places, including `AcceptanceMappingTest`, which records that
the mapping check had to be written in a *weaker* form for months "because
AUTH-004 could not be demonstrated until Phase 4 delivered C.5, and a check
demanding seven would have failed every build until then and been switched off
in week one." **ADR-OPS-024's defect, encountered, worked around, and never
named as a spec defect.** The remedy is the ADR's: reassign AUTH-004 to Phase 4
and let the check demand all seven.

**PGA-03 — Phase 3 (shape A).** Gate item: DKIM-001/DKIM-002. DKIM-002 is *"rotate
active key → new key published/observed before old retires"*; §11.1 **step 2**
is *"Infra generates/stores private key and returns key reference + public
key"*. No Infra key service exists in any repository. `grep -rl "DKIM-001\|DKIM-002" tests/`
returns **zero files**. §51's Phase 3 exit tolerates a *mocked* Infra contract;
the task README's gate checklist added these two items without a mock and
without a mockable service. **Owner: `karyalay-mail-infra`.**

**PGA-04 — Phase 4 (shape A, weak — reported for completeness).** C.33 mailbox
usage needs a real backend quota probe, and `MailboxBackend` is Phase 5's and
was left empty. **But §51.1 explicitly licenses this** ("mailbox gateway and
admin APIs can progress with fake adapters") and the repository used the
licensed escape properly — a `DeterministicQuotaProbe`, with the production
binding throwing rather than silently defaulting to the fake. Two knock-ons are
*not* covered by §51.1: T04.08's handler is registered with no `JobRunner` and
no scheduled task creates it, and the phase's own entry criteria admit it was
"**Entered without that gate**" — Phase 3's exit criterion is unmet.

**PGA-05 — Phase 7 (shape B).** *"internal Ops endpoints pass contract tests;
AUD/OBS acceptance scenarios green."* Written as a **prefix class**, not even a
bounded range. Members: AUD-001 ✓ (4 files), **AUD-002 — 0 files**, OBS-001 ✓
(2 files), **OBS-002 — 0 files**. The phase README already flags it as "not
mapped". Note OBS-002 is redaction, which is also delta **AI-13** — OPEN in the
delta register with no contract on either side. Secondary: OBS-001 traces a send
request through the SMTP adapter, which is Phase 6; Phase 7's *entry* criteria
say it may start "where no gateway/send surface is required" and its *exit*
criteria require exactly that surface. The two contradict each other.

**PGA-06 — Phase 8 (shape A + B).** *"All 62 Appendix I scenarios green or
runbook-scripted with evidence."* **18 of 62 have no occurrence in the test
tree**: DOM-002, DKIM-001, DKIM-002, MBX-002, JOB-001, AUD-002, OBS-002, DB-001,
DB-002, FAIL-001, FAIL-002, FAIL-003, FAIL-005, FAIL-006, SEC-002, PERF-001,
REL-001, REL-002. Phase 8 is `todo`, so this is forecast work rather than a
false claim — the shape-B risk is that "all 62" reads as one item. Shape A on
the same phase: §52.1's Definition of Done requires *"rolling
deploy/migration/failure recovery tested in staging"*, and T08.09 is `blocked`
on *"no production host carries mariadb/redis/nats/openbao"*. The environment
the DoD requires does not exist and is Repo 3's to build.

### 5.2 `karyalay-webmail` (Repo 2)

**PGA-07 — Phase 1 (shape A + B).** *"A008–A044 automated where technically
possible."* The closest structural analogue to `AE #1–#40`. Six of the 37
members need capabilities §59 assigns elsewhere: **A013, A014, A015** (folder
create/rename/delete → Phase 3), **A021** (mark-read policy → Phase 3's flag
mutation), **A022** (quick archive → Phase 3), **A035** (remote-image proxy →
Phase 5, and blocked on delta **D-07**, which is DEFERRED with no owner). The
phase README names the same conclusion for each. A013–A015 were in fact
delivered by Phase 3. Shape-B half: **A021, A022 and A035 have no test of any
kind.** A042 has tests but only of the decision logic — `AttachmentDescriptor`
carries no scan-state field, so the blocked path is unreachable from the wire.

**PGA-08 — Phase 5 (shape A + B).** *"A093–A096, A098–A102 automated/manual
where applicable."* **A093** needs delta D-02 and **A094** needs D-13 — both
DEFERRED with no decision owner (see [the deferral
register](registers/deferral-register-v1.yaml)), so Phase 5 cannot satisfy them
by working harder. **A100** (400% zoom / 320px reflow) and **A101** (NVDA /
VoiceOver) are §60's manual AT matrix, which §59 gives **Phase 6**. **A095**
(offline while reading) is service-worker territory, §54, Phase 6. Of the nine:
A093, A094, A095, A098, A099, A101, A102 have zero files; **A100's single hit is
a CSS comment, not a test**; A096 has a test written in *Phase 3*, whose gate
also claims it — one member double-counted across two ranges.

**PGA-09 — Phase 3 (shape A).** *"Duplicate-send protection proven end to end…
no path reaches success without canonical server ACCEPTED/reconciliation."*
A068/A069 require reconciling an attempt whose response never arrived — a lookup
by `Idempotency-Key`. C.91 is keyed by submission id and there is no such
operation. The phase README says so: *"**The reconciliation half cannot be done
as written.**"* The client's fallback is honest — the status control is absent
and the copy says so — but the criterion demands something the cross-repo
contract does not offer. **This is delta AI-03, PARTIAL in the delta register
with exactly this gap recorded.** Owner: `karyalay-mail` + this repository.

**PGA-10 — Phase 6 (shape A + B).** *"Appendix M A001–A120 traceability matrix
complete."* **27 of 120 have no test.** Three of them — **A097, A103, A104** —
appear in **no phase-specific gate range at all**; Phase 5's range deliberately
skips A097 (`A093–A096, A098–A102`), so the blanket Phase 6 item is the only
place they are ever claimed. Shape A: *"Staging critical E2E on the production
artifact"* requires a deployed API. `api.karyalay.site` has answered 502 since
2026-08-22 and Repo 2's own Phase 0 README says *"there is no deployed API to
point a browser at"*.

### 5.3 `karyalay-mail-infra` (Repo 3)

Repo 3's `## Exit criteria (spec §81)` sections are one-line restatements of
§81's own exit column, so they cannot themselves be scope-impossible. **The gate
that binds is the `## Phase-gate evidence checklist`**, per the roll-up rule in
`tasks/README.md`. All findings below are against those checklists.

**PGA-11, PGA-12** — §3 above.

**PGA-13 — Phase 10 (shape A).** *"Appendix AL rows evidenced (incl.
'Deliverability' — AK fully evidenced)."* AL's **Capacity** row ("N+1 tested
headroom… no critical tier starts >65% tested limit") and **Runbooks** row ("all
P1 runbooks present; high-risk ones exercised") are §81 **Phase 11**
deliverables, owned by `T11.01` and `T11.02`. Phase 10's task index contains no
capacity task and no runbook task, and Phase 11's gate repeats the runbook item.
Phase 10 cannot close without evidence that §81 *and Phase 11's own task index*
both place in Phase 11. *(Checked and not claimed: AL's external-synthetics row
**is** Phase 10's, via `T10.05`.)*

**PGA-14 — Phase 10 (shape A, cross-repo).** The same criterion. Appendix AK's
preamble says *"ongoing reputation operations belong with **Repo 4**"*, and the
"AK fully evidenced" clause therefore pulls in **AK-17** (complaint/reputation
ingestion → Repo 4 Phase 3) and **AK-20** (abuse restriction path, calling Repo
1's C.101 → Repo 4 Phase 3). Appendix AL also carries an **Inbound SMTP** row
requiring *"at least two MX nodes"*, which no §81 phase delivers.

**PGA-15 — Phase 4 (shape A).** *"OpenBao quorum failover and snapshot restore
fixture pass."* §7 requires the `vault` role at 3 nodes. `inventory/environments/production.yml`
holds four hosts — `mx1`, `mx-out1`, `cp1`, `idp1` — and **none carries
`vault`**. Weaker than PGA-11 by a degree: nothing forbids buying three
machines, and §81 does put OpenBao in Phase 4. But the gate cannot be evidenced
today and no task provisions the hosts.

> **Adjacent, and not a gate defect — worth its own line because it is
> load-bearing.** The comment above `deploy_authorized_keys` in that same
> inventory file says *"OpenBao is not built yet (§42, **Repo 3 Phase 5**)"* and
> *"moving custody is a **Phase 5** task"*. OpenBao is **Phase 4** per §81 and
> per the task tree. That comment is the recorded containment story for an
> unrestricted-root SSH key living on one laptop, and it names the wrong phase.

**PGA-16 — Phase 6 (shape A).** *"Role minimums met per spec §7."* §81 gives
Phase 6 "Galera, Redis HA, NATS HA, redundant DNS/edges"; §7 sets minimums for
**fourteen** roles. `mailbox-active` (1 active per shard) and `mailbox-standby`
(≥1 eligible standby) are **Phase 7** — Phase 6 cannot produce a fenced standby.
`mx` (≥2 public nodes in independent failure domains) and `submit` (≥2, separate
IP/reputation pools) are Phase 1/2 roles that **no phase gates on**; today `mx1`
carries `mx`, `submit`, `mailbox` *and* `dns-rec` on one box. `controller` (≥2)
is Phase 3; `monitor`'s independent synthetic node is Phase 11. One unqualified
gate line makes one phase responsible for the whole fleet's sizing.

**PGA-17 — deliverability workstream (shape A, a direct contradiction).** The
workstream's gate requires *"AK-01…AK-13, AK-23, AK-26 rows ☑ with evidence"*;
Phase 5's gate says *"deliverability enforcement rows **AK-13**…AK-15 become
testable"* in Phase 5. The same row is required-evidenced by one gate and
not-yet-testable by another. The workstream's entry criteria are *"None"*, and
`docs/runbooks/deliverability-readiness.md` asserts *"identity items AK-01…AK-13
and AK-23, AK-26 need only the server, the test domain and DNS control"* — which
is false for at least **AK-09** (MTA-STS/DANE policy fixtures), **AK-10**
(TLS-RPT) and **AK-13** (IP pool isolation), all three of which §81 assigns to
Phase 5 and all three of which are ☐ in that runbook's own table. **This is the
programme's longest-lead-time workstream** (START-HERE §4 item 5: sender
reputation accrues with calendar time), so a gate it cannot meet matters more
here than anywhere else.

**PGA-18, PGA-19** — §4 above.

**PGA-20 — workstream (shape B, low severity, and with a mitigation worth
copying).** The AK gate accounts for 24 of Appendix AK's 28 rows (15 claimed,
9 explicitly deferred to Phases 2–5). **AK-24, AK-25, AK-27 and AK-28 are
unaccounted**, despite the workstream's own Objective reading "every AK row
(AK-01…AK-28)". AK-09, AK-10, AK-17, AK-19 and AK-25 are named in no task file
at all — they exist only as unnamed members of a range.

> **The mitigation, and it is the model.** `docs/runbooks/deliverability-readiness.md`
> carries a **complete 28-row table** with a per-row status glyph and a per-row
> evidence path. Repo 3 already has the machine-checkable artifact that
> ADR-OPS-024's Compliance section says Appendix AE lacks. The defect is only
> that the *gate* cites ranges instead of that table. Fixing PGA-20 is
> a one-line change; the same fix is not available for Appendix W, which has no
> such table.

**PGA-29 — Repo 3 Phase 10 (shape B, off-by-one, no action urged).** *"AL.1 first-mailbox
smoke steps 1–8"* against an AL.1 that has nine steps; step 9 is *"only then
mark tenant migration/commercial activation complete"*, arguably a conclusion
rather than a test. Recorded so somebody decides which, not asserted as a hole.
*(For contrast: Phase 1's "host enrollment gate steps 1–8" is exact against §9's
eight, and Phase 8's `AJ-03…AJ-08` is exact. Both clean.)*

### 5.4 `karyalay-mail-ops` (Repo 4)

Phase 0 is ADR-OPS-024's and was not re-audited. Its reassignment of #13/#14 →
Phase 1, #30 → Phase 2, #16 → Phase 3 **did land** in all three phase READMEs —
except for PGA-28 below.

**PGA-21 — Phase 3 (shape A).** *"AE #41–#90 pass."* Two members need Repo 1
surfaces that do not exist in the pinned contract, verified by reading the
vendored `contracts/upstream/openapi/operations-api-v1.yaml` directly, which
defines exactly four operations.

- **AE #85** — *"outbound lock reversed → **Repo 1 observed state verified**"*.
  There is no Ops-callable read of effective restrictions.
  `getResourceDiagnostics` is the only read and its `ResourceDiagnostics` schema
  has no restrictions field. Corroborated against the *running* service by
  T00.07b. **This is delta AI-01, PARTIAL, and the missing read is one of the
  two defects [ADR-KEM-014](adr/ADR-KEM-014-restriction-precondition-token.md)
  proposes fixing.**
- **AE #68** — *"new app password + spam spike → **credential revoke**/outbound
  lock"*. `restriction_code` is a closed enum of five values and none revokes a
  credential or a session. **AI-01's third open defect: Ops can block future
  authentication and cannot end a session an attacker already holds. No ADR is
  raised on it.**

*(Also in range, lower confidence: **AE #84** "action HTTP timeout uncertain →
reconcile before retry" is currently answered by idempotent replay rather than
by asking. Whether that satisfies the scenario's intent is a spec-owner reading,
not a file question.)*

**PGA-22 — Phase 4 (shape A).** *"AE #131–#155 pass."* **#149** ("derived infra
projections after PITR → rebuilt from authority") is §77 projection rebuild →
**Phase 5**, `T05.09`; its near-duplicate **#196** is *already* a Phase 5 exit
criterion. **#148** ("DB PITR while workers running → workers paused") is
§79–§80 maintenance drain → **Phase 5**, `T05.06`. Phase 4's five tasks build a
ledger, sampled restores, restore orchestration, cross-plane restore and DR
drills; none is a projection rebuilder or a drain orchestrator. Additionally the
gate requires a passing **DR-005 MariaDB PITR** drill, and MariaDB is on no
production host — Phase 4's entry criteria do not state that dependency.

**PGA-23 — Phase 5 (shape A).** *"AE #156–#180 and #192–#197 pass."* Entry
criteria require Phase 0 and Phase 1 only, **not Phase 2** — but **#172**
(maintenance drains *migration workers* with checkpoints) needs the Phase 2
migration runtime, which is the same subject ADR-OPS-024 used to move **#30**
out of Phase 0. **#174** (mailbox shard maintenance) needs Repo 3 Phase 7's
fenced shards. **#173** (MX drain → alternate capacity) needs more than one MX
(see PGA-16). **#163** (recovery synthetics) is Repo 3's `T10.05`/`T11.04`.
*Credit where due:* Phase 5's README already self-discloses its §76–§78 mapping
gap in the open. The cross-phase and cross-repo dependencies are not disclosed
the same way.

**PGA-24 — Phase 7 (shape A, cross-repo).** See §3.

**PGA-25 — Phase 1 (shape A, inverted; low severity).** *"AE #181–#191,
**#13–#15** + #198, #202 pass."* AE **#15** is *"evidence access ticket reused
after expiry → denied"* — an evidence ticket, not a support bundle. §96 puts
audit/evidence in **Phase 0**, and Phase 0's README records #15 as already
delivered and green. Satisfiable, so it blocks nothing; it inflates Phase 1's
apparent AE count by one and the grouping "#13–#15 (support bundles)" mislabels
#15's subject. **The mirror image of ADR-OPS-024's defect** — a criterion
pointing at an *earlier* phase — and worth naming because it shows the ranges
are assembled by proximity rather than by subject.

**PGA-26 — Phase 3 and others (shape B).** **17 AE scenarios are named in no
task file at all**, existing only as unnamed members of a range: #46, #57, #60,
#62, **#67, #68, #69, #70**, #138, #185, #186, #206, #207, #208, #213, #214,
#215.

**#67, #68, #69 and #70 are the four ATO and containment scenarios** — the core
of Phase 3's abuse story — and not one is named by a Phase 3 task. #206, #207
and #208 are API-hygiene scenarios (unknown-field rejection, `request_id` in
problem responses, optimistic version conflict without lost update) that §96's
own "authz/audit/idempotency are Phase 0" line would put at the foundation.

**Qualification, stated so it can be weighed:** every Repo 4 phase-1-onward task
is ☐, so "no test exists" is true of essentially all 201 scenarios in Phases
1–7. The finding is narrower and survives that: **these 17 have no *task***, so
when the phases are built there is no line item that will produce them.

**PGA-27 — no phase (shape B, by set arithmetic).** The union of every ops
phase's AE claim is exactly **#1–#202**. **#203 through #241 — thirty-nine
scenarios covering evidence audit and PLATFORM — are claimed by no phase**
before Phase 7's blanket *"all 241 pass"*. Several are named in Phase 0 *task*
criteria, but none is a *phase* exit criterion, so no gate before Phase 7 fails
if one regresses. Among the fully unclaimed: **#205** (retention hold prevents
evidence deletion), **#219–#222** (rule shadow mode; promotion to enforce;
global kill switch; kill switch off does not replay destructive actions),
**#237** (operator session revoked mid-action), **#241** (backup verify job
starved by migrations).

**#221 and #222 are the ones to look at first**, and for an interesting reason:
Phase 3's *gate checklist* names them (*"☐ kill switches proven (AE #16, #221,
#222)"*) while Phase 3's *exit criteria* do not. That is a gate item **stronger**
than the criterion it serves — the opposite failure to ADR-OPS-024's, and
equally worth fixing.

**PGA-28 — Phase 1 (shape B; a live regression from ADR-OPS-024's own
remediation).** Phase 1's **exit criteria** demand #181–#191, **#13–#15**, #198
and #202. Phase 1's **gate checklist** says only *"☐ AE #181–#191, #198 green"*.
**#13, #14, #15 and #202 are in the criterion and have no box in the
checklist** — and #13/#14 are precisely the two ADR-OPS-024 moved *into* this
phase on 2026-08-24. That ADR's acceptance note says the phase READMEs are
updated in the same commit "because an ADR that reassigns a criterion and does
not move it has quietly dropped it." The criterion moved. **The gate item did
not**, and the gate checklist is what the roll-up rule reads. Small, live,
and fixable in one line.

---

## 6. What generates this, in four patterns

**1. A range copied from the appendix by subject area rather than by phase
scope.** `AE #1–#40`, `A008–A044`, `W-106–W-120`, `AUTH-001…004`, `H1–H9`. The
acceptance matrix is organised by subject; the phases are organised by
capability; the two do not align, and copying a contiguous block out of one into
the other imports whatever else happens to sit in that block. **Every shape-A
finding in this report except PGA-01 and PGA-11 arrived this way.**

**2. A scenario whose *other half* is owned by somebody else.** EVT-001/002
(NATS → Repo 3), DKIM-001/002 (Infra key service → Repo 3), A093/A094
(unapproved deltas → contracts), AE #85/#68 (missing Repo 1 operations),
A068/A069 (C.91 keyed wrong). The criterion names a scenario and **nobody checks
whether the scenario's dependencies are inside the phase.**

**3. An identifier matched by name rather than by scenario.** PGA-01 is the
sharpest instance in the programme: two tests named `evt_001_…` and `evt_002_…`
are green, mapped, and CI-enforced, and they assert a *different property* than
Appendix I's EVT-001/EVT-002 describe. **A mapping check that verifies "a test
with this name exists" cannot catch this.** It is START-HERE §6.4's lesson
applied to acceptance mapping: the check inspected a name and never asked
whether the thing the name describes actually happens. Any future
scenario-to-test check must compare *behaviour*, or at minimum require the
scenario text to be quoted in the test, or it will certify this defect.

**4. An environment decision that is never propagated into the criteria that
depend on it.** Staging (PGA-11, PGA-12, PGA-24, PGA-06, PGA-10) and the absent
data tier (PGA-15, PGA-22). The decision is recorded once, in the task that
took it, and every criterion downstream keeps asking for the thing.

---

## 7. What is clean, and the two patterns worth copying

**Clean:** Repo 1 Phases 0, 5, 6 · Repo 2 Phases 0, 2, 4 · Repo 3 Phases 0, 1,
2, 8, 9, 11 · Repo 4 Phases 2, 6.

Two deserve to be read by whoever fixes the rest.

**`karyalay-mail-ops` Phase 2 — how to carry a cross-phase dependency without
poisoning your own gate.** Its fourth exit criterion states the problem in the
open rather than burying it: *"**Production launch note (§96)**: migrations
cannot launch to production without restore/backup and target-capacity checks,
**even though those are Phase 4/6 features** — the launch gate (Appendix AF
'Migration' row) also requires cutover/rollback drills."* It scopes the
dependency to the **launch gate** rather than to the **phase gate**, so Phase 2
stays closable on its own deliverables and nothing is dropped. `AE #91–#130` is
also fully covered — every member named individually in a task. **This is the
pattern the other findings should be remediated into.**

**`karyalay-mail-infra` Phase 2 — how to write a gate that cannot silently
pass.** A two-column table separating *"the configuration cannot express the
failure"* from *"the running system was observed not to fail"*, with honest ☐
NOT EVIDENCED rows naming the exact missing capability, plus a section headed
*"the one gap with no gate at all"* for ClamAV. Its rig **refuses** to report a
pass it cannot support and CI fails if it exits zero. That is START-HERE §6.4
built into a gate rather than written above one.

Also worth noting: **Repo 2 Phase 0 is now clean.** The `A001–A007` range that
ADR-OPS-024 cites was closed — A002 and A003 were given tests in commit
`d7243d0`, whose subject reads *"A002 and A003 had no test, and the gate said so
in a range."* The fix works. It has been applied to one range out of the dozens
in this report.

And **Repo 2 Phase 4 is the counter-example that proves the defect is
avoidable**: its contacts/directory criterion is written *with an explicit
escape hatch* for the unapproved delta — "either implemented or remaining
disabled mocks" — which is the correct way to write a criterion whose capability
lives in another repository.

---

## 8. What this repository did about it, and what it deliberately did not

**Did.** ADR-OPS-024's Compliance section names the enforcement it could not
write:

> "A test would be the better enforcement — 'every AE scenario claimed by this
> phase has a test naming it' — and is not written here because the AE table
> lives in prose in the spec rather than in a machine-readable form. That is a
> gap worth closing, and closing it belongs with whoever makes Appendix AE
> machine-readable."

That is the same sentence ADR-KEM-012 wrote about the delta register, and both
were answered on 2026-08-24 for the register:
[`docs/registers/delta-register-v1.yaml`](registers/delta-register-v1.yaml) and
[`docs/registers/deferral-register-v1.yaml`](registers/deferral-register-v1.yaml),
with eleven checks in `npm run validate`. Three of this report's findings —
PGA-07's A035, PGA-08's A093/A094, PGA-09, PGA-21 — resolve to deltas that
register now carries with an evidenced disposition, so the cross-repo half of
those criteria is at least *checkable* from here.

**Deliberately did not.** No acceptance-scenario register was built. Appendix
AE (241 rows), Appendix W (242), Appendix M (120) and Appendix I (62) are the
property of the repositories that own them, four agents were working in those
repositories, and a scenario register authored here would be exactly the
speculative projection ADR-KEM-009 refused to publish for AI-04..AI-09.
**The delta register is the pattern; the scenario registers are their owners'
to build**, and each is a smaller job than this report, because the enumeration
already exists in the specs.

**Also deliberately did not:** no sibling task file, phase README or
`contracts/PIN.json` was touched.

---

## 9. Suggested order, if the owner wants one

Not a plan and not authority. An ordering by how much each unblocks.

1. **Decide staging** (PGA-11, PGA-12, PGA-24, and half of PGA-06 and PGA-10).
   One decision, seven phases across three repositories. Either provision it, or
   rewrite every criterion that names it and record what the deferral costs.
2. **PGA-28** — one line, and it is a live regression from an ADR accepted
   today. Phase 1's gate checklist is missing the boxes its own criterion needs.
3. **PGA-19** — H4, H6 and H7 are ADR-KEM-003's fencing invariants and they are
   invisible. This is a safety property, not a bookkeeping one.
4. **PGA-01's second half** — the EVT-001/EVT-002 tests assert a different
   property than the scenarios describe, and they are green and mapped. Anything
   that can be green while being wrong should be corrected before more mapping
   is built on it.
5. **PGA-17** — the deliverability workstream is the longest-lead-time item in
   the programme and its gate contradicts Phase 5's.
6. **The range criteria generally** — remediate into the ADR-OPS-024 shape:
   name the excluded members, assign each to the phase that owns it, and keep
   the numbers. Repo 3's `deliverability-readiness.md` shows what the target
   looks like; Repo 4 Phase 2 shows how to write the criterion.

## 10. Recorded as not determined

- Whether **AE #84**'s idempotent-replay reconcile satisfies that scenario's
  intent. A spec reading, not a file question.
- Whether Repo 2's **cross-origin credential isolation test** exists and passes,
  as Repo 3 Phase 1's sixth gate item requires. Candidate files were found;
  the specific assertion was not verified. One grep for whoever owns that phase.
- Whether **PGA-— (Repo 4 Phase 3 §25 anomaly scenarios #58/#59/#64)** belong to
  Phase 3 or Phase 6. §96 reads as basic-in-3 / sophisticated-in-6 and Phase 3's
  frontmatter range textually includes §25. The overlap is real and is hidden
  inside two ranges; which side it falls is the spec owner's.
- Whether Repo 3 **could procure** the ~20 machines §7's role minimums imply.
  PGA-15 and PGA-16 claim only that those gates cannot be evidenced *today* —
  a weaker claim than PGA-11's "cannot be met by decision".
- **Every count in this document**, if enough time passes. Four repositories
  were being written to while they were read.
