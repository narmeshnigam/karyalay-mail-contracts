---
phase: 00
status: in-progress
last-updated: 2026-08-17
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
| [T00.01](T00.01-error-catalog.md) | Error catalog (`errors/`) | ☐ todo | — | Repo 1 App. E, §39 |
| [T00.02](T00.02-event-envelope-and-catalog.md) | Event envelope + catalog (`events/`) | ☐ todo | — | Master envelope; Repo 1 §31, App. D |
| [T00.03](T00.03-auth-contracts.md) | Auth contracts (`auth/`) | ☐ todo | — | Repo 1 §17–§18, App. B |
| [T00.04](T00.04-openapi-public.md) | OpenAPI: public + mailbox APIs (`openapi/`) | ⛔ blocked | T00.01, T00.03 | Repo 1 App. C.1–C.96 |
| [T00.05](T00.05-openapi-internal.md) | OpenAPI: internal provisioning + ops (`openapi/`) | ⛔ blocked | T00.01, T00.03 | Repo 1 §29–§30, App. C.97–C.107 |
| [T00.06](T00.06-ops-executor-deltas.md) | Freeze ops executor deltas AI-04..AI-09 | ⛔ blocked | T00.05 | Repo 4 App. AI |
| [T00.07](T00.07-observability-contract.md) | Observability contract (`observability/`) | ☐ todo | — | Master; Repo 1 App. H; Repo 2 App. K |
| [T00.08](T00.08-dns-contract.md) | DNS record contract (`dns/`) | ☐ todo | — | Repo 1 §10–§11; Repo 3 DNS §§ |
| [T00.09](T00.09-validation-harness.md) | Validation harness + consumer pinning guide | ⛔ blocked | T00.01–T00.08 | Master §0.3; ADR-KEM-001 |
| [T00.10](T00.10-decide-adr-kem-002.md) | Decide ADR-KEM-002 (gateway transport) | ☑ done | — | Repo 1 §19 |
| [T00.11](T00.11-decide-adr-kem-003.md) | Decide ADR-KEM-003 (storage HA ceiling) | ☑ done | — | Repo 3 §56–§57, App. AG |
| [T00.12](T00.12-tag-v0.1.0-gate-0-closure.md) | Tag `v0.1.0` + Gate 0 closure evidence | ⛔ blocked | T00.01–T00.09 | ADR-KEM-001 |

## Phase-gate evidence checklist

- ☐ Validation harness output (all artifacts pass) archived
- ☐ `v0.1.0` tag exists and is annotated with the artifact inventory
- ☐ Four consumer CI validation runs recorded (one per repo)
- ☑ Decision register updated for ADR-KEM-002 and ADR-KEM-003 outcomes
  (both ACCEPTED 2026-08-17)
