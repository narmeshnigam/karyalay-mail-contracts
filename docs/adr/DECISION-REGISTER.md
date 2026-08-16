# Cross-Repository Decision Register

Status of architecture-level decisions raised against the v1.0 specification
baseline. Governed by Master Contract §40. One line of truth per decision —
details live in the linked ADRs.

| ID | Decision | Status | Notes |
| --- | --- | --- | --- |
| ADR-KEM-001 | Shared contracts package ownership → this repository | **ACCEPTED** | Closes the Master §42.3 P0 gap. Directories exist; population is the first Gate 0 deliverable. |
| ADR-KEM-002 | Mailbox gateway transport: pooled IMAP + master user for data operations; Doveadm HTTP retained for admin operations | **PROPOSED** | Awaiting architecture-owner decision. Unblocks Webmail delta D-02 (change feed) if accepted. |
| ADR-KEM-003 | DRBD/CE storage HA recorded as a stage with explicit exit triggers; fencing capability must be published before any HA claim | **PROPOSED** | Awaiting architecture + SRE owner decision. No code impact until an exit trigger fires. |
| ADR-KEM-004 | Amend ADR-INF-002 to permit Mailcow as a Gate 1–3 Repo 3 implementation | **REJECTED by owner, 2026-08-16** | ADR-INF-002 stands as written. Repo 3 is first-party from Gate 1. Not to be re-proposed without new evidence. |
| OPEN-001 | Calendar/groupware position vs. Workspace/Zoho competition | **OPEN — product decision** | Master §1.3 excludes it from v1. The exclusion is deliberate; the *competitive* consequence is undecided. Needs a product answer before GA pricing, not before Gate 1. |
| OPEN-002 | PHP-FPM as the streaming path for the mailbox gateway | **OPEN — deferred** | Concern recorded (process-per-request under large attachment streaming). Revisit with load evidence at Gate 2; premature to redesign now. |

## Editorial corrections applied to working copies (2026-08-16)

Baseline documents in `~/Downloads/` are untouched. Working copies under
`docs/spec/` in each repository carry three factual corrections:

1. **Repo 3, Appendix AA** — SMTP enhanced-status references corrected to cite
   RFC 2034 (capability), RFC 3463 (semantics), RFC 5248 (registry), and both
   RFC 3461/3464 for DSN. Previously cited RFC 2034 and 3461 alone.
2. **Master §34.3** — backup-only site-disaster RPO row no longer quotes a flat
   ≤24 h; it now requires each deployment to publish its measured RPO, with a
   ≤1 h target where the Repo 3 §58 hourly snapshot tier replicates off-site.
3. **Repo 4, Appendix AH** — the two Dovecot documentation links now cite one
   documentation version, pinned to the Repo 3 release manifest.
