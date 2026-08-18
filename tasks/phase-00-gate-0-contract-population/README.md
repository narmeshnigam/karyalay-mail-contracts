---
phase: 00
status: in-progress
last-updated: 2026-08-18
---

# Phase 00 — Gate 0: contract population

## Objective

Populate the six machine-readable contract directories (`errors/`, `events/`,
`auth/`, `openapi/`, `observability/`, `dns/`), stand up a validation harness,
resolve the two pending cross-repo ADRs, and cut the first immutable tag
(`v0.1.0`) that every consumer repository pins.

## Entry criteria

None. This phase is unblocked and is the first work item of the programme.

## Exit criteria

Per [ADR-KEM-001](../../docs/adr/ADR-KEM-001-shared-contracts-ownership.md)
and Master Contract §0.3:

1. All six contract directories populated from their normative sources.
2. Validation harness passes on every artifact.
3. `v0.1.0` tagged; tag is immutable.
4. All four consumer repositories' CI validates against the tag (evidence
   recorded per consumer).

## Task index

| ID | Task | Status | Blocked by | Spec refs |
| --- | --- | --- | --- | --- |
| [T00.01](T00.01-error-catalog.md) | Error catalog (`errors/`) | ☑ done | — | Repo 1 App. E, §39 |
| [T00.02](T00.02-event-envelope-and-catalog.md) | Event envelope + catalog (`events/`) | ☑ done | — | Master envelope; Repo 1 §31, App. D |
| [T00.03](T00.03-auth-contracts.md) | Auth contracts (`auth/`) | ☑ done | — | Repo 1 §17–§18, App. B |
| [T00.04](T00.04-openapi-public.md) | OpenAPI: public + mailbox APIs (`openapi/`) | ☑ done | — | Repo 1 App. C.1–C.96 |
| [T00.05](T00.05-openapi-internal.md) | OpenAPI: internal provisioning + ops (`openapi/`) | ☑ done | — | Repo 1 §29–§30, App. C.97–C.107 |
| [T00.06](T00.06-ops-executor-deltas.md) | Freeze ops executor deltas AI-04..AI-09 | ☑ done | — | Repo 4 App. AI |
| [T00.07](T00.07-observability-contract.md) | Observability contract (`observability/`) | ☑ done | — | Master; Repo 1 App. H; Repo 2 App. K |
| [T00.08](T00.08-dns-contract.md) | DNS record contract (`dns/`) | ☑ done | — | Repo 1 §10–§11; Repo 3 DNS §§ |
| [T00.09](T00.09-validation-harness.md) | Validation harness + consumer pinning guide | ☑ done | — | Master §0.3; ADR-KEM-001 |
| [T00.10](T00.10-decide-adr-kem-002.md) | Decide ADR-KEM-002 (gateway transport) | ☑ done | — | Repo 1 §19 |
| [T00.11](T00.11-decide-adr-kem-003.md) | Decide ADR-KEM-003 (storage HA ceiling) | ☑ done | — | Repo 3 §56–§57, App. AG |
| [T00.12](T00.12-tag-v0.1.0-gate-0-closure.md) | Tag `v0.1.0` + Gate 0 closure evidence | ◐ in-progress | — | ADR-KEM-001 |

## Phase-gate evidence checklist

- ☑ Validation harness output (all artifacts pass) archived — `npm run validate`,
  21 checks, 0 failures; `npm run lint`, 0 errors. Reproducible on any checkout
  of the tag.
- ☑ `v0.1.0` tag exists and is annotated with the artifact inventory
- ☐ Four consumer CI validation runs recorded (one per repo) — **the remaining
  gate.** Per ADR-KEM-001 the tag unblocks Wave 1; Gate 0 closes during it.
- ☑ Decision register updated for ADR-KEM-002 and ADR-KEM-003 outcomes
  (both ACCEPTED 2026-08-17)

## Findings raised, not resolved

Transcription surfaced six cross-specification divergences. Master §0.2 forbids
resolving a shared-contract conflict by invention, so each is recorded as a
proposed ADR with the evidence behind it, and none was silently fixed:

| ADR | Finding | Blocks |
| --- | --- | --- |
| [KEM-005](../../docs/adr/ADR-KEM-005-error-catalog-baseline-reconciliation.md) | Five Master baseline error codes duplicate Appendix E conditions under different names; two HTTP mappings fall outside the Master's stated range | Nothing — `v0.1.0` publishes Appendix E |
| [KEM-006](../../docs/adr/ADR-KEM-006-event-catalog-and-envelope-reconciliation.md) | Envelope disagreement (`resource` vs `aggregate`, missing `request_id`); three genuine catalog gaps; three `mail.v1.*` families Repo 4 consumes that nobody publishes | Repo 4 collector work on `auth.*`, `delivery.*`, `abuse.*` |
| [KEM-007](../../docs/adr/ADR-KEM-007-permission-and-role-naming-reconciliation.md) | Permission vocabulary differs from Master Appendix B.1; three platform roles carry no permissions at all | Any work needing `platform_security`, `deliverability_analyst` or `platform_billing` authority |
| [KEM-008](../../docs/adr/ADR-KEM-008-desired-state-and-observation-shape.md) | Repo 1 §12.2 and Repo 3 §49 describe the desired-state document differently; 3 of Repo 3's 6 readiness values have nowhere to be stored | Repo 1 Phase 6 and Repo 3 Phase 3 implementation |
| [KEM-009](../../docs/adr/ADR-KEM-009-ops-executor-delta-disposition.md) | All six Repo 4 → Repo 3 executor deltas deferred to `v0.2.0`; AI-12's action envelope sequenced first | Repo 4 Phases 1, 2, 4, 5 — already reflected in BUILD-ORDER §11 |

KEM-008 is the one to read before writing code: it names the interface both
sides describe differently, and `v0.1.0` publishes only one of the two
descriptions.

