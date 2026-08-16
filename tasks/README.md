# Task system — karyalay-mail-contracts

This directory is the executable work plan for the shared contract authority.
It uses the same task system as the four implementation repositories.

This repository has a single phase: **Gate 0 — contract population**. Per
[ADR-KEM-001](../docs/adr/ADR-KEM-001-shared-contracts-ownership.md), Gate 0
does not close until every machine-readable contract directory is populated
and all four consumers' CI validates against a tagged release. Every sibling
repository's Phase 0 is blocked on the tag produced here, which makes this
folder the first work item of the entire programme.

## Status legend

| Symbol | Status | Meaning |
| --- | --- | --- |
| ☐ | `todo` | Ready to start; no unresolved blocker |
| ◐ | `in-progress` | Actively being worked |
| ⛔ | `blocked` | Cannot start; see `blocked-by` |
| ◎ | `review` | Work complete, awaiting review/decision |
| ☑ | `done` | Complete with recorded evidence |

## Conventions

- Task IDs: `T00.NN` (this repo has only phase 00 / Gate 0).
- Every task file carries YAML frontmatter:
  `id`, `phase`, `status`, `blocked-by`, `spec`, `docs`, `last-updated`.
- Status changes are made by editing the task's frontmatter **and** the phase
  README index row, and bumping `last-updated`.
- Roll-up rule: the phase is ☑ only when all tasks are ☑ **and** the exit
  criteria have recorded evidence. Phase status is never edited independently.

## Phase overview

| Folder | Title | Objective | Exit criteria | Status |
| --- | --- | --- | --- | --- |
| [phase-00-gate-0-contract-population/](phase-00-gate-0-contract-population/README.md) | Gate 0 — contract population | Populate all six contract directories, stand up validation, tag `v0.1.0` | ADR-KEM-001 closure conditions; Master Contract §0.3 | ☐ todo |

## Sources of truth

Contract content is **derived**, never invented: the Master Contract defines
the envelope and precedence; each repository specification's appendices define
the catalogs (endpoints, events, errors, permissions). On any conflict between
sources, stop and raise an ADR (Master §0.2) — never resolve by invention.
