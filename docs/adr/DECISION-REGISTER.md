# Cross-Repository Decision Register

Status of architecture-level decisions raised against the v1.0 specification
baseline. Governed by Master Contract §40. One line of truth per decision —
details live in the linked ADRs.

| ID | Decision | Status | Notes |
| --- | --- | --- | --- |
| ADR-KEM-001 | Shared contracts package ownership → this repository | **ACCEPTED** | Closes the Master §42.3 P0 gap. Directories exist; population is the first Gate 0 deliverable. |
| ADR-KEM-002 | Mailbox gateway transport: pooled IMAP + master user for data operations; Doveadm HTTP retained for admin operations | **ACCEPTED by owner, 2026-08-17** | Repo 1 Phase 5 unblocked. Webmail delta D-02 implementable via IMAP IDLE once its canonical endpoint ships here. |
| ADR-KEM-003 | DRBD/CE storage HA recorded as a stage with explicit exit triggers; fencing capability must be published before any HA claim | **ACCEPTED by owner, 2026-08-17** | Honesty rule binding: no fencing proof → single-node with published RPO/RTO. First deployment's fencing capability still to be established (Repo 3 T07.04/T07.08). |
| ADR-KEM-004 | Amend ADR-INF-002 to permit Mailcow as a Gate 1–3 Repo 3 implementation | **REJECTED by owner, 2026-08-16** | ADR-INF-002 stands as written. Repo 3 is first-party from Gate 1. Not to be re-proposed without new evidence. |
| ADR-KEM-005 | Error catalog: publish Repo 1 Appendix E verbatim; five Master baseline names recorded as superseded; `MAILBOX_QUOTA_EXCEEDED` 507 and `PROVISIONING_FAILED` 503 stand | **PROPOSED 2026-08-18** | Raised by Gate 0 T00.01. Blocks nothing — `v0.1.0` ships Appendix E. Master Appendix D and §23.2 already disagree with each other; one needs a master revision either way. |
| ADR-KEM-006 | Event envelope follows Master §22.3 (`resource`, `request_id`), not Repo 1 §31.1 (`aggregate`); catalog scope is Repo 1 Appendix D's 45 events; three genuine gaps and three undefined consumer subject families referred to their owners | **PROPOSED 2026-08-18** | Raised by Gate 0 T00.02. Repo 4 must not build consumers against `mail.v1.auth.*`, `mail.v1.delivery.*` or `mail.v1.abuse.*` — nothing publishes them. |
| ADR-KEM-007 | Permission vocabulary follows Repo 1 Appendix B; role catalog follows Master §10.2/§10.3; `platform_security`, `deliverability_analyst` and `platform_billing` carry no permissions and must not be assigned until Appendix B covers them | **PROPOSED 2026-08-18** | Raised by Gate 0 T00.03. `deliverability_analyst` has an immediate consequence: the deliverability workstream is live now with no permission behind it. |
| ADR-KEM-008 | Desired-state and observation shapes: adopt the Repo 1 ⊎ Repo 3 union in `v0.2.0` (`schema_version`, `resource_id`, `desired_generation`, `desired_status`, `dependencies`, `spec` nesting, six-value readiness + `ABSENT`, `checksum`, and Repo 1's `correlation`) | **PROPOSED 2026-08-18** | Raised by Gate 0 T00.05. **The one to read before writing code.** `v0.1.0` publishes only the Repo 1 side. Items 2, 3, 5 and 7 are shared-breaking; better broken now than at integration. |
| ADR-KEM-009 | All six Repo 4 → Repo 3 executor deltas (AI-04..AI-09) deferred to `v0.2.0`, with AI-12's canonical action envelope sequenced first | **ACCEPTED 2026-08-18** | Raised by Gate 0 T00.06. Repo 3 Appendix AB forbids publishing a speculative production API, so none could be authored in `v0.1.0`. Consistent with ADR-OPS-022 and BUILD-ORDER §11 finding 2. **The deferral target has passed and was never met** — see the note below. |
| ADR-KEM-010 | Webmail deltas D-01, D-04 and D-05 accepted into the contract as C.108–C.114; D-02, D-03, D-07 and D-13 remain deferred and undecided | **ACCEPTED 2026-08-22** | Published in `v0.3.0`. karyalay-mail serves all seven operations as of 2026-08-22 (`ServedOperationsTest::OUTSTANDING` is empty). The four still-deferred deltas block four Repo 2 Phase 5 tasks, so Wave 5 cannot open its webmail half without deciding them. |
| ADR-KEM-011 | Session bootstrap endpoint C.115, the Appendix N delta that was never registered | **ACCEPTED 2026-08-22** | Published in `v0.4.0`. Repo 1 Appendix C grows 114 → 115. |
| ADR-KEM-012 | Publish AI-12 (canonical action envelope) and AI-04..AI-09 (the six typed Repo 3 executors) in `v0.5.0`, over karyalay-mail-infra ADR-INF-038 | **ACCEPTED 2026-08-24** | Closes the gap ADR-KEM-009 opened: its deferral to `v0.2.0` named a prerequisite Repo 3 ADR that nobody raised, and the target passed three tags. Unblocks ten Repo 4 tasks. Also fixes AI-05's per-request mutability, which Repo 4's client had wrong, and publishes the `idempotency_key` pattern T00.07b found unpublished. |
| OPEN-001 | Calendar/groupware position vs. Workspace/Zoho competition | **OPEN — product decision** | Master §1.3 excludes it from v1. The exclusion is deliberate; the *competitive* consequence is undecided. Needs a product answer before GA pricing, not before Gate 1. |
| OPEN-002 | PHP-FPM as the streaming path for the mailbox gateway | **OPEN — deferred** | Concern recorded (process-per-request under large attachment streaming). Revisit with load evidence at Gate 2; premature to redesign now. |

## Gate 0 — contract population (2026-08-18)

`karyalay-mail-contracts` `v0.1.0` is tagged. All six machine-readable contract
directories are populated: 80 error codes, an envelope plus 45 event payload
schemas, claims/14 roles/32 permissions, 107 OpenAPI operations across the four
documents Master §0.3 names, the telemetry contract, and 11 DNS record kinds. A
21-check harness and a Redocly ruleset run in CI, alongside a job that
regenerates every artifact from the four repository specifications and fails on
any diff.

**Gate 0 is not closed.** ADR-KEM-001 requires all four consumers' CI to
validate against the tagged release, and none has done so yet — those
repositories were blocked on this tag. The tag unblocks Wave 1; the gate closes
during it. `CONSUMING.md` is the procedure each consumer follows.

Populating the contracts was also the first exercise that forced the four
specifications to agree on one artifact, and it surfaced the five findings
recorded as ADR-KEM-005 through ADR-KEM-009 above. Each is proposed, none is
resolved, and none was fixed by invention (Master §0.2).

## Editorial corrections applied to working copies

Baseline documents in `~/Downloads/` are untouched. Working copies under
`docs/spec/` in each repository carry four factual corrections:

1. **Repo 3, Appendix AA** (2026-08-16) — SMTP enhanced-status references
   corrected to cite RFC 2034 (capability), RFC 3463 (semantics), RFC 5248
   (registry), and both RFC 3461/3464 for DSN. Previously cited RFC 2034 and
   3461 alone.
2. **Master §34.3** (2026-08-16) — backup-only site-disaster RPO row no longer
   quotes a flat ≤24 h; it now requires each deployment to publish its measured
   RPO, with a ≤1 h target where the Repo 3 §58 hourly snapshot tier replicates
   off-site.
3. **Repo 4, Appendix AH** (2026-08-16) — the two Dovecot documentation links
   now cite one documentation version, pinned to the Repo 3 release manifest.
4. **Repo 2, Appendix P** (2026-08-17) — cross-reference typo "Appendix 49"
   corrected to "§49" (visual-regression baselines reference a section, not an
   appendix).

## Recorded dispositions (2026-08-17)

Ambiguities surfaced during documentation and task scaffolding, each closed by
a recorded disposition rather than a spec edit:

1. **Mixed British/American spelling in all four repository specs** —
   tolerated as-is; derived documents follow the spec's usage per term and
   quote normative identifiers verbatim. Editorial-class cleanup may batch
   later; never per-file drive-by edits.
2. **Repo 4 Appendix AE rows 41–241 formatting artifact** — scenario and
   expected-result collapsed into tuple-style strings. Scenario numbering
   remains valid and citable; content is recoverable from the tuples. Reformat
   only as a single editorial-class change if ever needed.
3. **Repo 3 Appendix AK has no item IDs** — document-local row references
   AK-01…AK-28 assigned in the Repo 3 deliverability-readiness runbook, by row
   order, and labelled as doc-local.
4. **Repo 3 acceptance-count mismatch** (§82 "180+ minimum" vs Appendix W
   "minimum 242") — not a contradiction; the Appendix W count governs
   (recorded in Repo 3 T09.06).
5. **Phase-plan placement gaps** — deliverables named in a spec but absent
   from its phase plan were scheduled with mapping notes recorded in the task
   files themselves: Repo 1 C.1–C.5 → T04.01, C.6–C.23 → T03.07, §36 sending
   policy → T06.08; Repo 3 ACME/DNSSEC → T05.05, Keycloak → T04.04; Repo 4
   data repair → T05.09, IP warm-up → T06.04. These placements are approved.
6. **Commit convention** — Conventional Commits 1.0.0 pinned across all five
   repositories via each repo's CONTRIBUTING (Repo 4 additionally by
   ADR-OPS-021). The specs are silent; this is a local process decision.
7. **Security disclosure contact** — `security@karyalay.in` is the permanent
   address, to be provisioned before the first supported release; interim
   contact is the owner's personal address, recorded in each SECURITY.md.
8. **Repo-local gap ADRs accepted 2026-08-17** — Repo 1 ADR-019 (static
   analysis + collation pins), ADR-020 (documentation tree baseline); Repo 2
   WEB-ADR-016 (documentation tree), WEB-ADR-017 (flag governance completion:
   D-11/12/14/15 flag names; unphased deltas get phases at approval time);
   Repo 3 ADR-INF-031 (runbook governance), ADR-INF-032 (evidence convention);
   Repo 4 ADR-OPS-019 (stop-the-world independence scenario), ADR-OPS-020
   (runbook governance), ADR-OPS-021 (repository conventions).

## Register correction — 2026-08-24

Three rows were wrong and are fixed above.

- **ADR-KEM-009 read `PROPOSED`**; its ADR file has said `ACCEPTED` since
  2026-08-18. Repo 4 has been treating it as accepted throughout — its
  `contracts/PIN.json` cites "ADR-KEM-009 (ACCEPTED 2026-08-18)" as the reason
  AI-04..AI-09 may be absent from the pinned tag.
- **ADR-KEM-010 and ADR-KEM-011 were missing entirely**, despite both being
  ACCEPTED on 2026-08-22 and both having shipped contract changes
  (`v0.3.0` and `v0.4.0`). A register that omits the two most recent accepted
  decisions is worse than no register, because it is consulted as complete.

### The ADR-KEM-009 deferral was never honoured, and nothing owns it

ADR-KEM-009 deferred AI-04..AI-09 to **`v0.2.0`**. The contracts repository is
now at **`v0.4.0`** — three tags past the target — and the six executor deltas
exist nowhere in it. `grep -rl "AI-04"` returns only this register, the ADR
itself, `BUILD-ORDER.md` and Gate 0's `T00.06`.

`T00.06` is ☑, and correctly so: its acceptance criterion was to record a
*disposition*, not to publish the contracts. So the deferral closed a task
without creating one, and **no task in any repository owns writing them.**

The cost is not theoretical. Ten Repo 4 tasks are ⛔ on this string across
Phases 1, 2, 4 and 5:

| Phase | Blocked tasks |
| --- | --- |
| 01 diagnostics | T01.02, T01.04 |
| 02 migrations | T02.06, T02.07, T02.08 |
| 04 backup/recovery | T04.01, T04.02, T04.03 |
| 05 incidents/changes | T05.03, T05.06 |

Deciding whether `v0.5.0` publishes them — and creating the task that does — is
the single largest unblocking action available to the programme outside the
`cp1` deployment.

## Gate 0 closed — 2026-08-24

ADR-KEM-001's condition — **all four consumers' CI validates against the tagged
release** — is met. All four verified in FULL mode on 2026-08-24, meaning the
tag was fetched and compared rather than the committed copies merely digested:

| Consumer | Tag | Result |
| --- | --- | --- |
| `karyalay-mail` | `v0.4.0` | 14 files byte-identical to `ea4ce36` |
| `karyalay-webmail` | `v0.4.0` | 6 files byte-identical, generated client current |
| `karyalay-mail-ops` | `v0.4.0` | CI run 32664033271, FULL mode |
| `karyalay-mail-infra` | `v0.2.1` | 12 files byte-identical to `a5c1135` |

The Gate 0 section above says "Gate 0 is not closed ... none has done so yet".
That is superseded by this entry.

**Repo 3 sits on `v0.2.1` and the other three on `v0.4.0`.** Gate 0 asks
whether each consumer validates against *a tagged release*, not whether all
four share one, so the condition holds. The drift is nonetheless real,
unexplained by any ADR, and owed a decision: `v0.2.1` → `v0.4.0` crosses
C.108–C.115, so advancing Repo 3's pin is a change with evidence rather than a
chore. Recorded here so it is not mistaken for something Gate 0 settled.
