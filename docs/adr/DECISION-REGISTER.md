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
| ADR-KEM-009 | All six Repo 4 → Repo 3 executor deltas (AI-04..AI-09) deferred to `v0.2.0`, with AI-12's canonical action envelope sequenced first | **PROPOSED 2026-08-18** | Raised by Gate 0 T00.06. Repo 3 Appendix AB forbids publishing a speculative production API, so none could be authored in `v0.1.0`. Consistent with ADR-OPS-022 and BUILD-ORDER §11 finding 2. |
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
