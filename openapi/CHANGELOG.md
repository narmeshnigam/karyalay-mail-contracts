# Changelog — `openapi/`

Change classes follow Master Contract §0.4. Every entry names the class,
because the class decides the approval path and whether the release is a
patch, a minor or a master-contract revision.

| Class | Applies to an OpenAPI change when | Approval |
| --- | --- | --- |
| Local implementation | Nothing in this directory. An operation or schema here is never repo-local. | — |
| Shared compatible | An operation or optional property is added; a description is clarified without changing what it denotes. | Architecture owner + affected repo owners |
| Shared breaking | A property is renamed, removed or made required; an enum loses a value; an operation changes path, method or status. | Master-contract revision and migration plan |

Consumers pin a tag (Master §0.3). A published tag is never moved — a
correction ships as the next patch version.

## v0.2.1 — 2026-08-18

**Shared compatible.** No shape change. Every schema, operation, enum and
required-field list is byte-identical to `v0.2.0`; only the declared version
strings and the toolchain that writes them changed.

`v0.2.0` shipped declaring two different versions of itself. Six artifacts
said `0.2.0`; `observability/telemetry-contract-v1.yaml` and
`dns/domain-record-contract-v1.yaml` still said `0.1.0`. Both are
hand-authored from prose rather than generated, so the regeneration stage
never inspected them, and the version check read only OpenAPI `info.version`
— so nothing in CI compared an artifact's self-declared version against the
release it was shipping in.

A consumer that vendors the telemetry contract and the provisioning document
out of one tag and reads two different versions has no way to decide which is
authoritative. That is why this is a release and not a follow-up commit:
`v0.2.0` is published and immutable, and a correction ships as the next patch.

| Change | Detail |
| --- | --- |
| Version has one source | `tools/derive/version.py` reads `package.json`. The five generator literals and the two hand-authored files no longer define it independently — there were eight sources of truth for one number. |
| Hand-authored artifacts are stamped | `tools/derive/stamp_handauthored.py` rewrites the `contract_version:` line in the two prose-derived files and runs as part of `derive`, so the regeneration stage now covers them exactly like a generated file. |
| CI catches the drift class | New check `every versioned artifact declares the release it ships in` walks every artifact declaring a version and holds all of them to `package.json`. It fails if fewer than six artifacts are inspected, so it cannot go vacuous the way the error-code check did. |

**Consumer action.** Pin **`v0.2.1`**. Migrating from `v0.2.0` requires no code
change — the wire shapes are identical. Migrating from `v0.1.0` is the
`v0.2.0` migration below, unchanged.

## v0.2.0 — 2026-08-18

**Shared breaking.** Scope is `openapi/internal-provisioning-api-v1.yaml`
only. The other three documents are byte-identical to `v0.1.0` apart from
`info.version`.

Implements [ADR-KEM-008](../docs/adr/ADR-KEM-008-desired-state-and-observation-shape.md),
accepted 2026-08-18: the desired-state and observation shapes become the union
of Repo 1 §12.2 / Appendix A.32 and Repo 3 §49 / §50 / Appendices O.1, P.1,
which previously described the same interface differently.

This breaks before either side is implemented. That is the point — it is the
cheapest moment the break will ever be available.

### `DesiredState`

| Change | Was | Is | Decision |
| --- | --- | --- | --- |
| Envelope version added | — | `schema_version` (required) | 1 |
| Identity made uniform | `mailbox_id` | `resource_id` + `resource_type` | 2 |
| Generation disambiguated | `generation` | `desired_generation` | 3 |
| Target state added | — | `desired_status` (required) | 4 |
| Prerequisites added | — | `dependencies[]` | 4 |
| Typed fields nested | flat at envelope | `spec` | 5 |
| Correlation retained | `correlation` | `correlation` | 6 |

`mailbox_id`, `domain_id`, `storage_key`, `primary_address`, `quota_bytes`,
`auth_state`, `receive_state`, `send_state` and `filter_generation` moved into
`spec`. **Nothing was dropped**, and a validator check fails if any of them
goes missing from `DesiredStateSpec` or reappears at the envelope level.

### `ObservationReport`

| Change | Was | Is | Decision |
| --- | --- | --- | --- |
| Envelope version added | — | `schema_version` (required) | 1 |
| Generation split | `generation` | `desired_generation` + `observed_generation` | 3 |
| Readiness renamed and widened | `status`, 4 values | `readiness`, 7 values | 7 |
| Drift recordable | — | `checksum` | 8 |

`readiness` is Repo 3 §50's `PENDING/READY/DEGRADED/FAILED/RESTRICTED/DELETING`
plus Repo 1's `ABSENT`. `ABSENT` is not a synonym for `PENDING`: never-created
and mid-convergence require different operator responses.

`checksum` closes a real gap — Repo 3 §50 names checksum difference as one of
its two drift triggers, and Repo 1 Appendix A.32 had no column for it, so
checksum-detected drift could not be reported as such.

### New schemas

`DesiredStateSpec`, `DesiredStateResourceType`, `ResourceDependency`.

`DesiredStateResourceType` unifies two vocabularies that had never been
compared — see ADR-KEM-008 Amendment 1. `DKIM`→`dkim_key` and
`FILTER`→`filter_set` are the same concept under two spellings; `alias`,
`group` and `restriction` come from Repo 3; `organisation` and `placement`
from Repo 1 and remain **open items**, because Repo 3 has no materialization
row for either.

### Consumer action

- Pin **`v0.2.0`**. `v0.1.0` stays published and immutable, but its
  provisioning shape is superseded.
- Repo 3 T00.02 builds its fixture corpus against this tag. Its
  `unknown schema_version is nonretryable` golden case was unwritable against
  `v0.1.0`, which had no such field.
- Repo 1 Phase 6 and Repo 3 Phase 3 implement against this shape, not `v0.1.0`'s.
- Repo 1 and Repo 2 Phase 0 are unaffected: neither consumes this document.

### Specifications revised

Repo 1 §12.2, Appendix A.31, Appendix A.32. Repo 3 §49, §50, Appendix O.1,
Appendix P.1.

## v0.1.0 — 2026-08-18

Initial publication. 107 operations across four documents, reconciled 1:1 with
Repo 1 Appendix C.
