# Changelog — `errors/`

Change classes follow Master Contract §0.4. Every entry names the class,
because the class decides the approval path and whether the release is a
patch, a minor or a master-contract revision.

| Class | Applies to an error catalog change when | Approval |
| --- | --- | --- |
| Local implementation | Nothing in this directory. A catalog entry is never repo-local. | — |
| Shared compatible | A new code is added; a `meaning`, `ux_class` or `ux_behavior` string is clarified without changing what the code denotes. | Architecture owner + affected repo owners |
| Shared breaking | A code is renamed or removed; `http_status` or `retry_class` changes; the `type_uri_template` changes. Consumers branch on all four. | Master-contract revision and migration plan |

Consumers pin a tag (Master §0.3). A published tag is never moved — a
correction ships as the next patch version.

## Unreleased

Nothing.

## v0.1.0 — 2026-08-18

Initial population of the machine-readable catalog. No behavioural change:
this is the first machine-readable form of a catalog that already existed in
prose.

- Added `error-catalog-v1.yaml` — 80 codes transcribed from `karyalay-mail`
  repository-spec-v1.0 Appendix E, with the six retry classes from its §39
  and the user-facing categories from `karyalay-webmail` Appendix G.
- Added `error-catalog-v1.schema.json`.
- Recorded, but did not resolve, the divergence between Master Contract
  Appendix D (error catalog baseline) and Repo 1 Appendix E — see
  [ADR-KEM-005](../docs/adr/ADR-KEM-005-error-catalog-baseline-reconciliation.md).
  Five Master baseline codes have no Repo 1 counterpart. Per Master §0.2 a
  shared-contract conflict is never resolved by invention, so this release
  transcribes Appendix E as-is and leaves the reconciliation to the ADR.
