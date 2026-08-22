# Build Order — Karyalay Email

**Created:** 2026-08-18 · **Revised:** 2026-08-18 (audit against the task
trees — see §11) · **Owner:** Narmesh Nigam · **Companion to:**
[INFRASTRUCTURE-PLAN.md](INFRASTRUCTURE-PLAN.md)

This document answers one question: **in what order do the five repositories get
built, and what blocks what.**

It is derived from the task trees, not invented. Every claim traces to a
`tasks/README.md`, a phase README's entry/exit criteria, or an accepted ADR. If
this document and a repository's task tree disagree, **the task tree wins** and
this document is stale — fix it.

> **Custody, not authority.** This document lives in `karyalay-mail-contracts`
> because that is the only repository every other one already consumes, so it is
> the natural home for programme-wide records. Living here does **not** raise it
> in the precedence order of Master Contract §0.3: Master Contract → contracts
> repo schemas → repository spec → approved ADRs → implementation, and this
> document sits below all of them. It is not a contract, no consumer validates
> against it, and it is not a release artifact — editing it is never a contract
> change and never requires a version bump.

Scope note: this covers *repository build sequencing*. Server/DNS/provider
sequencing lives in [INFRASTRUCTURE-PLAN.md](INFRASTRUCTURE-PLAN.md). The two
meet at Wave 1 and again at Wave 3.

---

## 1. The short answer

| # | Repository | Start when | Rationale |
| --- | --- | --- | --- |
| **1** | `karyalay-mail-contracts` | **Now, first** | Root of the dependency graph. Three of four repos cannot start a single task until it tags `v0.1.0`. |
| **2** | `karyalay-mail-infra` | **Now, concurrent** | The only repo with unblocked work today — Phase 0 *and* Phase 1's first three tasks — and it owns the longest lead-time item in the programme. |
| **3** | `karyalay-mail` | Day the tag lands | Largest build (9 phases, 107 endpoints, 45 tables). Everything downstream consumes it, and its Phase 7 gates Repo 4. |
| **4** | `karyalay-mail-ops` | Day the tag lands | Unblocks last at Gate 0 — needs the tag *and* the AI-04..AI-09 freeze. |
| **5** | `karyalay-webmail` | Tag for Phase 0; Repo 1 live to *close* phases | Consumes Repo 1's API, but Phases 1–3 build against mocks — see §7.3. |

**If you can only run one workstream at a time**, the serial order is:
contracts → infra → mail → ops → webmail. Do not reorder 1 and 2 with anything
else; they are the only two with open doors.

---

## 2. Status legend

Matching the repositories' own legend, so this table reads the same as theirs.

| Glyph | Meaning |
| --- | --- |
| ☐ | Ready to start; no unresolved hard blocker |
| ◐ | In progress |
| ⛔ | Hard blocker outstanding (external artifact, undecided ADR, unlanded tag) |
| ◎ | Complete, awaiting review/evidence |
| ☑ | Complete with recorded evidence |

Per every repo's convention: **ordinary phase sequencing is ☐, not ⛔.** A task
that merely waits its turn is not blocked. ⛔ is reserved for things no amount
of local effort can clear.

---

## 3. The dependency graph

```
                        ┌────────────────────────────────────┐
                        │  karyalay-mail-contracts           │
                        │  Gate 0  →  tag v0.1.0             │
                        │  (12 tasks, 2 ☑, 5 ☐ now)          │
                        └─────────────────┬──────────────────┘
                                          │  HARD BLOCK — no escape hatch
          ┌───────────────┬───────────────┼───────────────┬───────────────┐
          ▼               ▼               ▼               ▼               │
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
   │  Repo 3     │ │  Repo 1     │ │  Repo 2     │ │  Repo 4     │        │
   │  infra      │ │  mail       │ │  webmail    │ │  ops        │        │
   │             │ │             │ │             │ │             │        │
   │ PARTLY FREE │ │  fully ⛔   │ │  fully ⛔   │ │  fully ⛔   │        │
   │ 8 tasks ☐   │ │  (8 of 9)   │ │  (8 of 10)  │ │  (9 of 11)  │        │
   │ + TWD.01–05 │ │             │ │             │ │ + AI-04..09 │◄───────┘
   └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   freeze
                                                                  (contracts T00.06)
```

That asymmetry is the entire answer to "where do I start." **Repo 3 is the only
repository with a door open today**, and contracts is the only thing that opens
the other three.

Repo 3's open door is wider than it first appears: Phase 0's
T00.03/T00.04/T00.05/T00.08 *and* Phase 1's T01.01/T01.02/T01.03/T01.07 all
carry `blocked-by: —`. Phase 1 needs a skeleton and a CI gate, not a contract.
Phase 1's remaining three tasks are unblocked too, so the real constraint is
attention, not dependencies. See §4 Wave 0 Track B.

---

## 4. Wave model

Waves are dependency-defined, not calendar-defined. A wave opens when its
entry condition is met, not on a date.

### Wave 0 — Today → `v0.1.0` tag

Two tracks with **zero dependency on each other**. Run both.

#### Track A — `karyalay-mail-contracts`, Gate 0 *(critical path)*

Five tasks are unblocked right now and are mutually independent — they can all
run in parallel:

| Task | Deliverable | Source |
| --- | --- | --- |
| T00.01 | Error catalog (80 codes) → `errors/` | Repo 1 App. E, §39 |
| T00.02 | Event envelope + 45-event catalog → `events/` | Master envelope; Repo 1 §31, App. D |
| T00.03 | Auth contracts → `auth/` | Repo 1 §17–§18, App. B |
| T00.07 | Observability contract → `observability/` | Master; Repo 1 App. H; Repo 2 App. K |
| T00.08 | DNS record contract → `dns/` | Repo 1 §10–§11; Repo 3 DNS §§ |

Then the serial tail — each genuinely needs its predecessor:

```
T00.01 + T00.03  ──►  T00.04  (OpenAPI C.1–C.96, public + mailbox)
                 ──►  T00.05  (OpenAPI C.97–C.107, internal + ops)
                            └─►  T00.06  (freeze AI-04..AI-09)   ← unblocks Repo 4
T00.01…T00.08    ──►  T00.09  (validation harness + pinning guide)
T00.01…T00.09    ──►  T00.12  (tag v0.1.0 + Gate 0 closure evidence)
```

☑ Already done: T00.10 (ADR-KEM-002 accepted), T00.11 (ADR-KEM-003 accepted),
both 2026-08-17.

**This work is pure derivation from specifications that already exist.** No
server, no runtime, no external dependency. It is the single highest-leverage
thing in the programme because it is the only thing standing between you and
four parallel build tracks.

> **Gate 0 does not close at the tag.** Per ADR-KEM-001, closure additionally
> requires all four consumers' CI to validate against the tagged release
> (evidence recorded per consumer). The tag *unblocks* Wave 1; the gate *closes*
> during Wave 1.

#### Track B — `karyalay-mail-infra`, unblocked half

| Task | Deliverable | Note |
| --- | --- | --- |
| T00.03 ☐ | Repository skeleton per Appendix A (42 paths) | Prerequisite for writing any playbook |
| T00.04 ☐ | CI pipeline bootstrap, stages 1–4 (§74) | Secret scan must be blocking |
| T00.05 ☐ | Ephemeral test CA and mTLS harness | Needed from Phase 4 onward |
| **T01.01 ☐** | **Inventory schema and environment model** | No contract dependency |
| **T01.02 ☐** | **Debian 13 baseline, identities, time — `bootstrap.yml`** | Mounts the 25 GB volume as the Dovecot mail root, XFS |
| **T01.03 ☐** | **nftables firewall-as-code — HARD GATE** | See below |
| **T00.08 ☐** | **Determine the OIDC identity provider disposition** | A question to a person, not engineering work — see below |
| **T01.07 ☐** | **Public zone records and the two application origins** | ADR-INF-034 — webmail Phase 0 builds against these; see below |
| T00.01 ⛔ | Pin contracts release, vendor schemas | Waits on tag |
| T00.02 ⛔ | Synthetic Repo 1 fixtures + API simulator | Waits on tag + T00.01 |

☑ Already done: T00.06 (ADR-INF-031), T00.07 (ADR-INF-032).

> **Phase 1 starts here, not in Wave 2.** All six Phase 1 tasks carry
> `blocked-by: —`; none reads a contract artifact. Phase 1's entry criterion is
> T00.03 + T00.04 (a home for playbooks and a lint gate) — not the whole Phase 0
> gate, which includes the tag-blocked T00.01/T00.02. The phase README was
> corrected on 2026-08-18 to say so.
>
> This is not a scheduling nicety. `mx-sin-1` is **live on a public IPv4 right
> now** with sshd listening, and INFRASTRUCTURE-PLAN §4 step 7a calls the
> firewall baseline a hard gate "deferrable only while sshd alone is listening."
> Holding T01.03 behind an unrelated contracts tag leaves a production host
> exposed for weeks with no dependency justifying it. Sequence
> T00.03 → T00.04 → T01.01 → T01.02 → **T01.03**, all inside Wave 0.
>
> Phase 1's remaining tasks (T01.04 DNS, T01.05 observability, T01.06 runbooks)
> can follow immediately or wait for Wave 2 — nothing forces either. **Phase 2
> is genuinely tag-gated**: T02.06's mailbox gateway consumes the contract
> schemas.

**T00.08 is in Wave 0 on purpose.** It asks whether the parent Karyalay system
already runs an OIDC provider mail can federate against. The answer decides
whether Wave 3 contains a full Keycloak build — host, TLS, backups, restore
drill, availability alerting — or a monitoring hookup. It costs nothing to ask
and it is the difference between estimating Wave 3 and guessing at it.
ADR-INF-033's `idp` role stays conditional until it reports.

**T01.07 provisions the application origins**, and until 2026-08-18 nothing did.
`mail.karyalay.site` and `content.karyalay.site` were Wave 0 work in
[INFRASTRUCTURE-PLAN §4 step 8a](INFRASTRUCTURE-PLAN.md) and in no task tree —
planned in prose, owned by nobody, which is the defect class ADR-INF-033 was
raised on. ADR-INF-034 now assigns them to Repo 3 on the same boundary: Repo 3
provisions the origin, Repo 2 deploys onto it.

The split is listed in INFRASTRUCTURE-PLAN §7 as retrofit-impossible and webmail
Phase 0 (T00.06, T00.08) builds against it from the first commit, so the origins
must exist before that phase opens — not at Phase 6 where the only reference
used to live. Two constraints carry into the task: **two separate Pages
projects** (one project with two custom domains serves both names with identical
headers from a single deployment and makes the split cosmetic), and **no Pages
Functions** without an ADR, which is what keeps leaving Cloudflare a CNAME change
rather than a rewrite.

**Plus the standing deliverability workstream**, whose README states
*"UNBLOCKED. Start today"* and calls it **the longest-lead-time item in the
programme** — sender reputation accrues only with calendar time, and no
engineering effort compresses it.

| Task | Status as of 2026-08-18 |
| --- | --- |
| TWD.01 Provision sending identity (AK-01…04, 12) | ◐ — server, IP, PTR, FCrDNS ☑; **AK-01 (port 25 egress) ⛔ until Hetzner limit request clears** |
| TWD.02 Publish authentication records (AK-05…07) | ◐ — SPF ☑; DMARC policy ☑ (single record verified) but **alignment ⛔ on AK-01**; DKIM key generation open |
| TWD.03 Baseline hygiene and contacts (AK-08, 11, 26) | ☐ |
| TWD.04 Evidence capture and checklist upkeep | ☐ — must conform to the T00.07 evidence convention |
| TWD.05 Warm-up plan and reputation watch (AK-23, 24) | ☐ — needs TWD.02 + TWD.03 |

These statuses were landed in the task tree and the AK runbook on 2026-08-18.
They had been recorded only in INFRASTRUCTURE-PLAN, leaving the tree — which
this document defers to — reading ☐ for work that was done.

**DKIM key generation is the one open item with no blocker.** Do it in Wave 0.

---

### Wave 1 — Tag lands: all four repos unblock

Entry condition: `karyalay-mail-contracts` **`v0.2.1`** published and pinnable.

> **Revised 2026-08-18.** The entry condition named `v0.1.0`. Two ADRs were
> accepted after it was written and both changed what "the tag" means:
>
> - **ADR-KEM-008** (union of the desired-state and observation shapes) ships
>   as **`v0.2.0`**, a shared-breaking release. `v0.1.0` remains published and
>   immutable — a published tag is never moved — but its provisioning shape is
>   superseded, so **consumers pin `v0.2.0`**. This is not optional for Repo 3:
>   its T00.02 golden case tests `schema_version`, which `v0.1.0` has no field
>   for.
> - **ADR-KEM-009** freezes AI-04..AI-09 as *deferred to `v0.2.x`*, which is
>   what contracts T00.06 asked for — a recorded disposition with a target tag,
>   not silence. Repo 4's eight gating Phase 0 tasks no longer carry that
>   blocker.
>
> **Superseded 2026-08-18 by `v0.2.1`.** Wiring the first consumer pin
> surfaced that `v0.2.0` declared two different versions of itself — the two
> hand-authored artifacts (`observability/`, `dns/`) still said `0.1.0`,
> because they sit outside the regeneration stage and the version check read
> only OpenAPI `info.version`. `v0.2.1` is shared-compatible, byte-identical
> in every wire shape, and gives the version one source. **Consumers pin
> `v0.2.1`.**
>
> The remaining half of the entry condition is **satisfied differently than
> planned**: no repo has a git remote, so the pin resolves through a local
> `file://` source recorded in each consumer's pin file. The pin names the
> tag, the tag's commit SHA and a SHA-256 per vendored artifact, so the
> switch to an `https://` remote changes one field and the digests prove
> nothing else moved. This is a recorded deviation, not a workaround: the
> immutability the pin rule protects comes from the digests, which hold
> regardless of transport.

| Repo | What opens | Notes |
| --- | --- | --- |
| **Repo 3** | T00.01, T00.02 → Phase 0 gate → **Phase 2** | Phase 1 already ran in Wave 0. T00.02 pins `v0.2.1`; against `v0.1.0` its `schema_version` golden case is unwritable |
| **Repo 1** | Phase 0, all 8 remaining tasks | T00.01 boot → T00.02/T00.03/T00.05/T00.08 → T00.04, T00.06. Does not consume the provisioning document, so unaffected by KEM-008 |
| **Repo 2** | Phase 0, all 8 remaining tasks | T00.01 toolchain → T00.03 generated client → T00.05 auth → T00.06 shell. Also unaffected by KEM-008 |
| **Repo 4** | Phase 0, all 9 remaining gating tasks | AI-04..AI-09 cleared by ADR-KEM-009; the *execution* phases (1, 2, 4, 5) stay blocked on the executors themselves. Repo 4 still joins at Wave 4 under ADR-OPS-022 |

**Repo 4's extra catch, corrected.** Its typed-clients task listed `Repo 1 APIs`
as a third blocker. Two things were wrong with how that was scheduled:

1. **The blocker is Repo 1 Phase 7, not Phase 3.** The AI-01 restriction/action
   requests it needs are served by Repo 1 **T07.01** (C.96, C.101–C.102).
   Earlier revisions of this document said Phase 3; that understated the lag by
   four phases.
2. **It was gating far more than itself.** Repo 4's Phase 0 exit required all
   §96 deliverables, and Phase 1's entry is "Phase 00 ☑" — so diagnostics could
   not start until Repo 1 Phase 7 shipped, even though *no Phase 1 task consumes
   a Repo 1 client*. T01.02/T01.04 block on the AI freeze alone (AI-05, AI-07,
   both Repo 3 executors); everything needing Repo 1 correctly sits in Phase 3.

**ADR-OPS-022** (ACCEPTED 2026-08-18) splits the task into **T00.07a** (Repo 3
client + the shared action envelope) and **T00.07b** (Repo 1 client), so the
tree shows which half is ready. It deliberately **does not relax the gate** —
both halves must complete for Phase 0 to close. A roll-up rule with one
exception is a roll-up rule nobody trusts.

The consequence is blunt and worth stating plainly: **Repo 4 does not build in
Wave 2.** Its Phase 0 cannot close without T00.07b, and Phase 1's entry is
"Phase 00 ☑", so the whole repository waits on Repo 1 T07.01. Wave 2 is a
three-way parallel wave, not four-way. The only lever is *when* Repo 1 runs
T07.01 — see Wave 2.

**Close Gate 0 here.** Each repo's first green CI run against the pinned tag is
the evidence ADR-KEM-001 requires. Record all four.

> **Built 2026-08-18.** All four repos' Phase 0 is delivered against `v0.2.1`;
> evidence in [docs/evidence/gate-0/CLOSURE.md](evidence/gate-0/CLOSURE.md).
>
> | Repo | Phase 0 | Verification |
> | --- | --- | --- |
> | **Repo 3** | T00.01, T00.02 ☑ (T00.08 waits on a person) | 48 checks |
> | **Repo 1** | all 8 ☑ | 53 tests, PHPStan `max`, Pint |
> | **Repo 2** | all 8 ☑ | 42 tests, typecheck, boundary lint |
> | **Repo 4** | 8 of 9 ☑ | 42 Go tests + 5 console |
>
> **Gate 0 is closed on validation, not on distribution.** Every pin resolves
> through a sibling clone; no consumer off this machine can fetch the tag.
>
> **Repo 4's Phase 0 does not close.** T00.07b blocks on Repo 1 **T07.01**,
> which is Wave 2 — the table row above saying "all 9 remaining gating tasks"
> was the loose statement; §4's own prose two paragraphs later has it right.

---

### Wave 2 — Divergent build (maximum parallelism)

Four tracks, no cross-blocking, all running on simulators or mocks.

| Repo | Sequence | Decoupling mechanism |
| --- | --- | --- |
| **Repo 3** | Phase 1 tail (T01.04–T01.06) → Phase 2 (mail vertical slice) | Phase 1 head ran in Wave 0 |
| **Repo 1** | Phase 1 (persistence) → Phase 2 (identity/authz) → **Phase 7 (T07.01 first)** → Phase 3 (provisioning) → Phase 4 (admin) | **Phase 3 exits against a mocked Infra contract** |
| **Repo 2** | Phase 1 (read mailbox) → **Phase 2 (compose/drafts) → Phase 3 (send/actions)** | Contract-generated mocks |
| ~~Repo 4~~ | **Does not build in this wave** — see below | — |

**Repo 1 T07.01 is the highest-leverage task in the programme after the tag.**
Not the whole of Phase 7 — the single task. §51.1 permits Phase 7 to start once
Phases 1–2 exit and the contracts are frozen, and T07.01 blocks only on T02.06
and T02.02. Since ADR-OPS-022 kept Repo 4's Phase 0 gate intact, T07.01 is what
lets Repo 4 exist at all.

**Schedule it immediately after Repo 1's Phase 2 exit gate is recorded** — the
earliest legal point. The rest of Phase 7 stays in its normal slot; pulling only
T07.01 forward keeps Repo 1's flow intact while cutting Repo 4's idle time to
the minimum the dependency allows.

**Repo 4 is out of this wave entirely.** Its Phase 0 gates on T00.07b, which
gates on T07.01, and Phase 1's entry is "Phase 00 ☑". It joins at Wave 4. This
is the accepted cost of keeping the roll-up rule absolute — the parallelism was
available, and it was traded for a gate that always means what it says.

**Repo 2 builds Phases 2 and 3 here too.** Their entry criteria are "Phase 1 ☑"
and "Phase 2 ☑" — purely internal to webmail. Every task chains off a Phase 1
task, none needs a live backend. Earlier revisions left them unplaced until
Wave 4, which hid real parallelism: Wave 4 makes them *provable*, it is not what
makes them buildable. Repo 2's §59 gate still applies — a phase is never
complete "solely because screens render" — so expect to close them in Wave 4.

**Repo 3 Phase 1 is the pacing item for the whole wave.** Its seven tasks:

| Task | Deliverable |
| --- | --- |
| T01.01 | Inventory schema and environment model (§6, §53) |
| T01.02 | Debian 13 baseline, identities, time — `bootstrap.yml` (§9–§11) — **this is where the 25 GB volume gets mounted as the Dovecot mail root, XFS** |
| T01.03 | **nftables firewall-as-code (§8, §12, App. C) — HARD GATE** |
| T01.04 | NSD authoritative + Unbound recursive — `dns.yml` (§43–§44, §75) — mail-plane split DNS, *not* the public Cloudflare zone |
| T01.05 | Observability plumbing (§66–§68) |
| T01.06 | Early runbook drafts RB-029/030/039/042 (§80, App. Y) |
| T01.07 | Public zone records and the two application origins (ADR-INF-034) — starts in Wave 0 |

**T01.03 must land before any datastore binds a port.** Redis, MariaDB and
OpenBao all listen by default; a Debian box on a public IPv4 with an unfiltered
data plane is compromised in hours, not days. Sequence it as T01.01 → T01.02 →
**T01.03** → everything else.

**Everything from here goes through Ansible.** No `apt install` over SSH. Phase
1's own evidence checklist requires *"second Ansible run after convergence shows
no changes"* — provable only if there was never a manual step. §53 mandates it,
and you will need to rebuild or clone this host.

---

### Wave 3 — First convergence: real mail plane

Entry condition: **Repo 3 Phase 2 complete** (Postfix in/submission, Rspamd,
ClamAV, Dovecot LMTP/IMAP, mailbox gateway on the lab domain).

This is where mocks run out.

| Repo 1 phase | Needs | Why it cannot be mocked |
| --- | --- | --- |
| **Phase 5 — Mailbox gateway** | Repo 3 Phase 2 Dovecot | Exit criterion is literally *"real Dovecot integration + malicious input/large mailbox tests"* |
| **Phase 6 — Compose/send** | Repo 3 Phase 2 Postfix submission | Duplicate/ambiguous-send failure tests need a real MTA and a real Sent folder |

Repo 3's own Phase 3 (projection/controller) converges from the other side: it
consumes Repo 1's desired-state, decoupled during Wave 2 by the T00.02 synthetic
fixtures and API simulator. Wave 3 is where the simulator gets replaced by the
real Repo 1.

**Also in Wave 3 — provision the three non-mail hosts.** Repo 3 T03.07
(control-plane `vps_server_1` + staging `vps_server_3`) and T03.08 (OIDC
identity provider), established by **ADR-INF-033** (ACCEPTED 2026-08-18). None
of these had an owner before that ADR: Repo 3's role catalogue was mail-data-plane
only, and Repo 1's T08.06 covers application config rather than the machine.
They depend only on the Phase 1 baseline, and **Wave 4 cannot open without
them** — Repo 1 has nowhere to serve from and no IdP to validate against.

**T03.08 is a full build. T00.08 reported on 2026-08-21** — the programme owner
confirmed the parent Karyalay platform operates no OIDC provider, *and* that mail
is to remain independent of it. ADR-INF-033's `idp` role is activated and this
wave grows accordingly: host, TLS, its own database with backup and PITR, a
tested restore drill, availability alerting with a named pager owner, realm and
audience configuration as code, and an upgrade policy.

The independence clause is the durable half. Federation is now a change to
ADR-INF-033 rather than a deferred default, so Wave 4 does not need to keep a
branch open for it — but the IdP is a single point of failure for all browser and
API access to mail, and Wave 4 cannot open without it running.

They sit in Phase 3 rather than Phase 1 for a reason worth keeping: Phase 1's
gate then closes on mail-baseline evidence alone, so Phase 2 is never held up by
hosts the mail plane does not use.

> **Schedule this deliberately.** If Repo 1 races ahead of Repo 3, it stalls at
> ~80% complete with its two hardest phases unable to exit. Target Repo 3 Phase 2
> landing *before* Repo 1 Phase 4 finishes.

---

> **Wave 3 status, 2026-08-22 (evening).** Both Repo 1 exit gates are ☑ and the
> mail plane is proven end-to-end on mx1 from the public Internet — not asserted.
> **T03.07 and T03.08 have converged**: `cp1` and `idp1` are provisioned,
> `maintenance_state: active`, with a clean second run on both. Nine defects
> surfaced that only running found.
>
> Both tasks stay ◐ **by design, not by staleness** — the programme owner elected
> to provision production only and defer staging, and both task files say in
> terms that they close partially and are not to be ticked ☑.
>
> **Wave 4's remaining blocker is a deployment, not a machine.** `cp1` serves
> `api.karyalay.site` on a trusted certificate and answers 502 until Repo 1's
> application is deployed onto it. Full account in
> [wave-3-closure.md](wave-3-closure.md) §0.
>
> An earlier revision of this note read *"T03.07 and T03.08 remain ⛔ … Wave 4 is
> blocked on exactly two hosts."* That was written hours before both hosts came
> up; it is superseded.

---

### Wave 4 — Second convergence: live API

Entry condition: **Repo 1 serving a real API against a real mail plane.**

> **Both halves are now substantially met (2026-08-22 evening).** The mail plane
> is proven end-to-end on mx1. `cp1` and `idp1` are converged and `active`, so
> there is a host to serve from and an IdP to validate against — what remains is
> deploying Repo 1's application onto cp1, which is Repo 1's half of the
> ADR-INF-033 boundary.
>
> An earlier revision read *"the serving half is not: `cp1` and `idp1` carry RFC
> 5737 placeholder addresses and `maintenance_state: provisioning`"*. Superseded;
> the inventory now carries real addresses.

| Repo | What opens |
| --- | --- |
| **Repo 2** | Phases 1–3 close against real integration; Phase 4 (account controls) becomes meaningful |
| **Repo 4** | **T00.07b** typed Repo 1 client completes; Phase 3 restriction actions via `OPS-BND-001`; Phase 2 migrations against real IMAP |

`OPS-BND-001` is a boundary rule, not a convenience: Repo 4 never mutates Repo 1
or Repo 3 state directly. Every restriction goes through Repo 1's action APIs.
Repo 4's Phase 0 exit criteria test for exactly this.

---

### Wave 5 — Secure the plane

Entry condition: Wave 4. **The §6 external clock binds here** — Repo 3 Phase 5
testing needs Hetzner TCP/25 egress.

| Repo | Sequence |
| --- | --- |
| **Repo 3** | Phase 4 (identity/secrets — OpenBao, DKIM key custody) → Phase 5 (outbound security — MTA-STS, DANE, TLS-RPT) |
| **Repo 1** | Phase 8 (hardening) |
| **Repo 2** | Phase 5 (live/safety/power) |

Phase 4 precedes Phase 5 for a concrete reason: OpenBao holds the DKIM private
keys that outbound signing depends on.

---

### Wave 6 — Durability

Entry condition: Wave 5.

| Repo | Sequence |
| --- | --- |
| **Repo 3** | Phase 6 (HA data foundations) → Phase 7 (mailbox shard HA) → Phase 8 (backup/DR) |
| **Repo 4** | Phase 4 (backup/recovery) — **needs Repo 3 Phase 8** |

**Repo 3 Phase 7 may not complete, by design.** ADR-KEM-003 holds T07.04/T07.08
behind proven fencing capability; without it, run single-node and publish
measured RPO/RTO. Do not let Phase 7 block Phase 8 — backups are independent
recovery (ADR-INF-030) and Repo 4 Phase 4 depends on them.

---

### Wave 7 — Certify and pilot

Entry condition: Wave 6.

| Repo | Sequence |
| --- | --- |
| **Repo 3** | Phase 9 (scale/security certification) → 10 (production pilot) → 11 (commercial readiness) |
| **Repo 4** | Phase 5 (incidents) → 6 (capacity) → 7 (hardening) |
| **Repo 2** | Phase 6 (production hardening) |

**Repo 4 Phase 6 needs history, not just code** — its entry requires Phases 0–3
☑ so capacity intelligence has real data to reason over. It cannot be pulled
forward.

Waves 5–7 were a single "Wave 5 — HA, scale, pilot" until 2026-08-18. Fifteen
phases with live internal dependencies in one row gave no sequencing to roughly
half the programme's work.

Two standing constraints apply across all three and are non-negotiable:

- **ADR-INF-002 (ACCEPTED, FINAL):** no third-party mail platform, relay or
  hosted gateway in any task, step or evidence. Repo 3 is first-party from Gate 1.
- **ADR-KEM-003 (ACCEPTED 2026-08-17):** no standby promotion and no HA claim
  without proven fencing capability. Without fencing → single-node with
  *published* RPO/RTO. Repo 3 T07.04/T07.08 retain the fencing-proof blocker.

---

## 5. Cross-repo blocking matrix

The complete set. Everything not listed here is independent.

| Blocked | Waits on | Escape hatch |
| --- | --- | --- |
| Repo 1/2/4 **Phase 0**, Repo 3 **Phase 0 exit** | contracts `v0.2.1` tag, resolvable by every consumer | **none — the real gate** |
| Repo 4 **Phase 0** | + AI-04..AI-09 frozen (contracts T00.05 → T00.06) | none |
| Repo 3 **T00.01, T00.02** | contracts tag | none |
| Repo 3 **Phase 1** | T00.03 + T00.04 only | ✅ **not tag-blocked — runs in Wave 0** |
| Repo 3 **Phase 2** | contracts tag (T02.06 gateway schemas) | none |
| Repo 3 **Phase 3** (controller) | Repo 1 desired-state | ✅ T00.02 synthetic fixtures + API simulator |
| Repo 3 **T03.07** (control-plane, staging) | Phase 1 baseline | none — Wave 4 needs them live |
| Repo 3 **T03.08** (IdP host) | T00.08 disposition; Phase 1 baseline | ✅ collapses to monitoring if a parent IdP exists |
| Repo 1 **Phase 3** (provisioning) | Repo 3 internal APIs | ✅ mocked Infra contract — permitted by the exit criteria |
| Repo 1 **Phase 5 exit** | Repo 3 Phase 2 real Dovecot | **none — hard convergence** |
| Repo 1 **Phase 6** (send) | Repo 3 Phase 2 Postfix submission | **none — hard convergence** |
| Repo 1 **Wave 4 deployment** | Repo 3 T03.07 control-plane host; T03.08 IdP | none |
| Repo 2 **Phases 1–5** | live Repo 1 | ✅ contract-generated mocks (build yes, prove no) |
| Repo 2 **Phases 2–3** | Repo 2 Phase 1 ☑ only | ✅ **internal — builds in Wave 2** |
| Repo 4 **T00.07b** Repo 1 client | Repo 1 **T07.01** (Phase 7) | none |
| Repo 4 **Phase 0 exit** | T00.07a **and** T00.07b | none — ADR-OPS-022 kept the gate |
| Repo 4 **Phase 1** (diagnostics) | Phase 0 ☑ → T00.07b → Repo 1 T07.01 | none — mitigate by scheduling T07.01 early |
| Repo 4 restrictions | Repo 1 action APIs (`OPS-BND-001`) | none |
| Repo 4 **Phase 2** migrations | real IMAP → Repo 3 Phase 2 | none |
| Repo 4 **Phase 3** abuse/deliverability | Repo 3 Phase 5 outbound; T00.07b | none |
| Repo 4 **Phase 4** backup/recovery | Repo 3 Phase 8 backups | none |
| Repo 4 **Phase 6** capacity | Phases 0–3 ☑ (needs history) | none |
| Repo 3 **T07.04, T07.08** | proven fencing capability | none — else publish single-node RPO/RTO |
| Repo 3 **Phase 5** *testing* | **Hetzner TCP/25 egress (AK-01)** | none — see §6 |
| Repo 2 delta features (D-11/12/14/15) | contract acceptance of the delta | ✅ ship flagged OFF (§60 permits) |
| Repo 2 **T01.09** (D-01), **T04.05** (D-04), **T04.06** (D-05) | contract acceptance **and** a Repo 1 endpoint | none — see below |
| Repo 2 **T05.02** (D-02), **T05.03** (D-13), **T05.04** (D-03), **T05.05** (D-07) | contract acceptance **and** a Repo 1 endpoint | none — see below |

**Seven Repo 2 tasks are blocked on unapproved deltas, and until 2026-08-22 this
matrix recorded none of them.** The row above them named D-11/12/14/15 — four
deltas that block no task at all — and offered "ship flagged OFF" as the escape
hatch. That hatch is real for those four, because each degrades to a working
fallback inside webmail. **It does not apply to the seven below it.** A feature
flag cannot be turned on against an endpoint that does not exist, and Appendix N's
governance is explicit that the deltas are "not authorization for Agent 2 to
invent production APIs."

Six of the seven are owned by **karyalay-mail** (D-05 by identity/directory plus
the mail gateway), so acceptance is not paperwork: it is an OpenAPI change, a
contracts version bump past `v0.2.1`, re-pinning in four consumers, and then an
endpoint build in Repo 1. Appendix C is exhaustive by invariant, so the route
cannot exist before the catalog does.

The scheduling consequence is concrete. **Wave 4** loses Repo 2's threaded inbox,
personal contacts and organisation directory search. **Wave 5** loses four of
Repo 2's seven Phase 5 tasks — the change feed, browser notifications, spam
feedback and the remote-image privacy proxy — which is most of what makes that
phase "live, safety, power" rather than a polish pass. Deferring the decision
does not defer the cost; it moves it into whichever wave is least able to absorb
it.

The simulators are deliberate architecture, not workarounds. Repo 1 and Repo 3
were each specified to be buildable without the other — Repo 3 against synthetic
Repo 1 fixtures, Repo 1 against a mocked Infra contract. That is what makes
Wave 2 four-way parallel instead of serial.

---

## 6. The external clock

One dependency is not in any repository and cannot be engineered around.

| Date | Event | Gates |
| --- | --- | --- |
| **~1 Sep 2026** | Hetzner first invoice issued → pay same day → immediately file SMTP limit request | Everything outbound |
| **~3 weeks later (~late Sep)** | TCP/25 egress expected to open | Repo 3 Phase 5 testing; TWD.01 closure; all warm-up |
| **~Sep, after Postfix + TLS + DKIM live** | File Barracuda delisting (deliberately deferred — a request filed against a dark IP gets denied and the denial is remembered) | Deliverability evidence |

**Inbound mail is unaffected.** Port 25 *inbound*, internal mail, IMAP,
submission on 465/587 and the entire Repo 3 Phase 2 vertical slice all work
today. Only egress to foreign MXs is blocked.

This costs nothing on the critical path **provided contracts Gate 0 and Repo 3
Phases 0–2 are underway now** — both run longer than the wait. It becomes a
schedule hit the moment the build tracks idle.

Contingency, if the limit request is denied: OVH / Contabo / RackNerd for the
outbound node. **That decision must be made before warm-up begins**, because
reputation accrues per-IP and restarting on a new IP restarts the clock.

---

## 7. Judgement calls

### 7.1 Why contracts first, absolutely

It is 12 tasks of derivation from specifications that already exist, it needs no
runtime, and it is the sole thing preventing four parallel tracks. Every day it
is not done is a day three repositories are idle. There is no version of this
programme where anything else is the right first move.

### 7.2 Why infra concurrent, not after

Two independent reasons:

1. It has unblocked work today — nothing else does.
2. Deliverability is **calendar-bound**. Reputation cannot be bought, parallelised
   or crashed. Its README is blunt: *"Every week of delay here is a week added to
   the end of the schedule."*

### 7.3 Why webmail last — with one exception

Repo 2 consumes Repo 1's API. Building it before Repo 1 exists means building
against generated mocks: real work, but unprovable, and its own §59 gate says a
phase is never complete *"solely because screens render."*

**The exception:** Phase 1's safe message renderer and hostile-corpus testing is
pure frontend security with zero backend dependency. Hostile HTML sanitisation is
where webmail security actually lives, it is the hardest thing in Repo 2, and it
benefits from long soak time. If you have capacity for a third track in Wave 2,
that is the piece worth pulling forward — still gated on the tag for Phase 0's
toolchain, but independent of everything after it.

**Corrected 2026-08-18:** "last" was overstated. Phases 2 and 3 are internally
gated on Phase 1, not on the backend, so the whole Phase 1→2→3 chain builds in
Wave 2. What comes last is *closing* those phases, which needs a live Repo 1.
Build early, prove late — but do not confuse the two, because §59 is explicit
that rendering screens is not completion.

### 7.4 Why ops unblocks last despite a nominal tag-only gate

Repo 4's Phase 0 carries two standing blockers, not one: the tag *and* the
AI-04..AI-09 freeze, which is contracts T00.06 — itself downstream of T00.05.
So Repo 4 is gated on the *deepest* part of Gate 0, not the shallowest. It
unblocks with the tag in practice, but it is the last thing Gate 0 produces.

### 7.5 Why Repo 4 waits, when it did not have to

The audit found Repo 4's Phase 0 gate stricter than its own task dependencies:
the typed-clients task bundled a Repo 1 client that only Phase 3 uses, and the
all-deliverables exit rule then held diagnostics behind Repo 1 Phase 7. A
carve-out excluding T00.07b from the gate would have freed Repo 4 to build in
Wave 2.

**That carve-out was offered and declined.** ADR-OPS-022 splits the task so the
dependency is visible, but leaves the gate absolute. The reasoning: a roll-up
rule with one documented exception becomes a roll-up rule with two, and a phase
marked ☑ stops being a fact you can act on. Repo 4 waiting is a schedule cost;
gates that need footnotes are a correctness cost, and correctness wins on a
programme whose evidence discipline is its main quality mechanism.

What that buys must be paid for in scheduling instead — hence T07.01 pulled to
the earliest legal point in Wave 2. **If Repo 4's start date becomes the binding
constraint, reopen ADR-OPS-022 rather than quietly slipping the gate.**

---

## 8. Traps

| Trap | Consequence | Guard |
| --- | --- | --- |
| Hand-configuring `mx-sin-1` over SSH | Unreproducible host; Phase 1 evidence unobtainable | Ansible from the first command (§53) |
| Repo 1 racing ahead of Repo 3 | Stalls at ~80% with Phases 5 and 6 unable to exit | Target Repo 3 Phase 2 before Repo 1 Phase 4 ends |
| Binding Redis/MariaDB/OpenBao before T01.03 | Public-IP host compromised in hours | Firewall is a hard gate, not a phase item |
| Treating the tag as Gate 0 closure | ADR-KEM-001 closure conditions unmet | Record four consumer CI runs |
| Claiming HA without fencing proof | Availability claim that is false to customers | ADR-KEM-003; publish RPO/RTO instead |
| Editing a phase status directly | Task tree stops meaning anything | Roll-up rule — status derives from tasks only |
| Filing Barracuda delisting early | Denial on a dark IP, and denials are remembered | Wait for Postfix + TLS + DKIM live |
| Starting Repo 3 Phase 1 before Phase 0 skeleton | Playbooks with no home, no CI gate | T00.03 → T00.04 → T01.01 |
| **Sizing Wave 3 as if T03.08 were a hookup** | T00.08 answered NO on 2026-08-21: it is a full Keycloak build, weeks not days | ADR-INF-033; `evidence/phase-00/T00.08/FINDING.md` |
| **Deferring T01.03 to Wave 2 because "Phase 1 needs the tag"** | A live public host stays unfirewalled for weeks on a dependency that does not exist | Phase 1 needs T00.03 + T00.04 only — §4 Wave 0 Track B |
| **Leaving Repo 1 T07.01 to spare capacity** | Repo 4 cannot start *at all* — Phase 0 gates on it and every later phase gates on Phase 0 | T07.01 immediately after Repo 1 Phase 2 exits |
| **Treating `content.karyalay.site` as a deployment detail** | Origin assumptions set in Phase 0 code; retrofit means auditing every content path in a shipped client | Two origins wired from webmail T00.06/T00.08 |
| **Assuming someone owns `vps_server_1` and the IdP** | Hand-configured hosts at the moment Wave 4 needs them; §53 evidence unobtainable after the fact | ADR-INF-033; Repo 3 T03.07/T03.08 |

---

## 9. Keeping this document true

This file is **derived**. It has no authority of its own.

Update it when — and only when — one of these changes:

- a phase's entry or exit criteria change in a repository spec
- an ADR lands that adds or removes a cross-repo dependency
- a wave's entry condition is met (mark it, date it)
- the external clock in §6 moves
- an audit finds this document asserting a dependency the trees do not have,
  or missing one they do (§11 is the record of the first such pass)

Do **not** track individual task status here. That lives in the task trees, and
duplicating it guarantees the two disagree. This document records *structure*;
the task trees record *state*.

**Precedence, unchanged:** Master Contract → contracts repo → repository spec →
approved ADRs → implementation. This document sits below all of them.

---

## 10. Right now

Two tracks, both startable today, neither blocking the other:

1. **`karyalay-mail-contracts`** — T00.01, T00.02, T00.03, T00.07, T00.08 in
   parallel, then the OpenAPI tail (T00.04 is over half the wave's volume on its
   own), then T00.09, then tag.
2. **`karyalay-mail-infra`** — T00.03 skeleton, T00.04 CI, T00.05 test CA, then
   straight into **T01.01 → T01.02 → T01.03**. Plus **T00.08** (ask about the
   IdP), **T01.07** (the two application origins), DKIM key generation (TWD.02's
   open item, no blocker), and starting TWD.03.

**T01.03 is the one with a clock on it that is not the contracts tag.**
`mx-sin-1` is live and unfirewalled beyond sshd; nothing else in Wave 0 is
holding an exposure open.

**T00.08 is the cheapest task in the programme and one of the highest-value.**
One conversation decides whether Wave 3 contains a Keycloak build. Do it this
week.

All three ADRs are now decided — **ADR-OPS-022** ACCEPTED (split the clients,
keep the gate), **ADR-INF-033** ACCEPTED with the `idp` role conditional on
T00.08, and **ADR-INF-034** ACCEPTED (Repo 3 owns the public zone and the
application origins; Pages, static only, no Functions). Nothing in the wave model
is waiting on a decision any more.

**ADR-INF-035** closed the last open question the same day: no Karyalay hostname
terminates TLS at a third party while carrying message content, credentials or
session tokens in readable form. `api.karyalay.site` becomes DNS-only; the static
origins and the encrypted R2 backups are unaffected. The cost is stated rather
than hidden — the control plane has no volumetric DDoS absorption, and the origin
hardening that replaces it lands in T01.03 and T03.07, neither of which had it
before.

Everything else in the programme is waiting on track 1.

---

## 11. Audit record — 2026-08-18

First full reconciliation of this document against all 38 phases and
workstreams in the five task trees. Eight corrections landed.

| # | Finding | Fix |
| --- | --- | --- |
| 1 | Repo 3 Phase 1 was placed in Wave 2 behind the contracts tag; all six tasks carry `blocked-by: —` and the phase needs only T00.03 + T00.04. A live public host was waiting on a dependency that does not exist | Phase 1 entry criterion rewritten; T01.01–T01.03 moved to Wave 0 |
| 2 | Repo 4's typed-clients blocker was recorded as Repo 1 **Phase 3**; it is Repo 1 **Phase 7** (T07.01). Repo 4 Phase 0's all-deliverables exit rule then blocked Phase 1 on it, though no Phase 1 task uses a Repo 1 client | Task split into T00.07a/T00.07b under **ADR-OPS-022** (ACCEPTED). Owner declined the proposed gate carve-out, so Repo 4 leaves Wave 2 and joins at Wave 4; mitigated by pulling Repo 1 **T07.01** to immediately after that repo's Phase 2 exit |
| 3 | Repo 2 Phases 2–3 were unplaced until Wave 4; their entry criteria are internal to Repo 2 | Both moved to Wave 2 |
| 4 | Wave 5 held 15 phases with live internal dependencies | Split into Waves 5 (secure the plane), 6 (durability), 7 (certify and pilot) |
| 5 | Three production dependencies had no owner in any task tree: the Repo 1 control-plane host, the staging host, and the production OIDC IdP. A fourth — the `content.karyalay.site` origin split — was referenced only in Repo 2 Phase 6 despite being retrofit-impossible | **ADR-INF-033** ACCEPTED with the `idp` role conditional; Repo 3 T03.07/T03.08 in Wave 3, and new infra **T00.08** resolves the IdP question in Wave 0. Origin split wired into webmail T00.06/T00.08, its provisioning into Wave 0 |
| 6 | Contracts T00.02 targeted 46 events; Appendix D holds 45 unique rows, so the task's own zero-divergence criterion could not pass | Corrected to 45; a 46th, if a consumer needs one, arrives via the ADR path already in the task |
| 7 | TWD.01/TWD.02 and every AK row read ☐ in the tree while INFRASTRUCTURE-PLAN recorded the work done on 2026-08-18 | Evidence landed in the task frontmatter, the workstream README and the AK runbook |
| 8 | Finding 5 wired the origin split into webmail but left its *provisioning* in prose — no task owned the origins, and ADR-INF-033 covers hosts, which a managed service is not. The public `karyalay.site` zone had no owner either; it is panel-edited, where two defects had already surfaced. Separately, INFRASTRUCTURE-PLAN served `mta-sts` from Pages, which spec §47 cannot support — it needs per-customer-domain policy with a tenant mapping, so the plan described something that breaks at the second customer domain | **ADR-INF-034** ACCEPTED: Repo 3 owns the public zone and the application origins on ADR-INF-033's boundary. New **T01.07** in Wave 0 — two separate Pages projects, static only, **no Pages Functions** without an ADR. `mta-sts` corrected to T05.03's service. The `api.karyalay.site` TLS-termination question was deliberately left open rather than folded in |

Not changed, and worth stating: **every one of the 38 phases appears in a wave.**
Nothing in the task trees is orphaned. The gaps found were all at the seams —
between the trees and the infrastructure plan, or in gates that claimed more than
their tasks required.

**Decisions taken on the audit's findings, 2026-08-18.** Findings 1, 3, 4, 6 and
7 were applied as recommended. Finding 2 was applied structurally but its
scheduling recommendation was declined: the owner kept Repo 4's Phase 0 gate
absolute rather than carve out T00.07b, accepting that Repo 4 starts at Wave 4
instead of Wave 2 (§7.5). Finding 5 was accepted with the `idp` role held
conditional pending T00.08, and the host tasks placed in Phase 3 rather than
Phase 1 so Phase 1's gate stays closeable on mail evidence alone. Finding 8 was
raised while answering whether Cloudflare Pages is a durable choice; it is, on
one condition — **no Pages Functions** — which is now the operative clause of
ADR-INF-034 rather than an understanding held in someone's head.
