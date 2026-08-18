# `openapi/`

Four documents, named by **Master Contract §0.3**:

| File | Catalog range | Operations | Serves |
| --- | --- | --- | --- |
| `public-control-api-v1.yaml` | C.1–C.65, C.92–C.96 | 70 | Customer administration |
| `mailbox-api-v1.yaml` | C.66–C.91 | 26 | The mailbox data plane |
| `internal-provisioning-api-v1.yaml` | C.97–C.100, C.105–C.107 | 7 | `karyalay-mail-infra` |
| `operations-api-v1.yaml` | C.101–C.104 | 4 | `karyalay-mail-ops` |

Plus `catalog-reconciliation-v1.yaml`, which is an index rather than a contract:
the C-number → `operationId` map the harness checks against the documents.

## Granularity — the T00.04 decision

T00.04 asks for a recorded choice between a single specification and per-family
files with shared components. **Neither was available:** Master §0.3 fixes these
four filenames, so the split is decided upstream. What remained to decide was
what goes in each, and whether the documents share a components file.

**Where the C.1–C.96 public surface splits.** The discriminator is the
*backend*, not the caller. Repo 1 §28 lists the mailbox-user API families —
Folders, Messages, Search, Drafts, Attachments, Send — as served through
`MailboxBackend` and `SubmissionGateway`. Those are C.66–C.91, and they are
`mailbox-api-v1.yaml`. Everything else in the public surface is served from the
control database and is `public-control-api-v1.yaml`, including the mailbox
*settings* families (C.54–C.60), which Repo 1 §28 itself marks as
"Control DB + Filter/Infra reconcile".

The alternative — splitting by which client calls what — was rejected because
`karyalay-webmail` Appendix E consumes 47 endpoints across both groups. A
caller-based split would put the same backend behind two documents and still not
give any client a single file.

**Where C.105–C.107 go.** Liveness, readiness and version belong to neither
integration exclusively. They are in `internal-provisioning-api-v1.yaml` because
Repo 3 operates the edge and the health probes behind it (its §14 HAProxy health
checks). They are the only operations in these documents with `security: []` —
unauthenticated inside the network boundary, never routed from the internet
(C.105 notes).

**No shared components file.** Master §0.3 names four files and no fifth, and a
self-contained document is what every generator handles without a resolver step.
The shared components are emitted from one source in
`tools/derive/gen_openapi.py`, so they cannot drift between documents, and each
document carries only the components it actually reaches.

## What is generated, and from what

Everything here. `tools/derive/gen_openapi.py` reads:

- **karyalay-mail repository-spec-v1.0 Appendix C** — every method, path,
  purpose, permission and per-endpoint note. Idempotency and `If-Match`
  requirements come from the cards' own Notes, not from a rule someone invented:
  `Idempotency-Key required` in a card produces a required header, and its
  absence produces an optional one.
- **`errors/error-catalog-v1.yaml`** — every error response. The `ErrorCode`
  enum and the per-status `code` enums are generated from the catalog, which is
  what makes "zero inline-invented error codes" structural rather than a review
  promise.
- **`tools/derive/openapi_schemas.py`** — resource representations, each citing
  the Appendix A table it represents and naming any column deliberately withheld
  with the rule that withholds it.
- **`tools/derive/openapi_ops.py`** — the C-number → request/response binding.

Regenerate with `npm run derive`. Do not hand-edit the YAML.

## Fidelity, and its limit

Appendix C fixes operation-level semantics: method, path, purpose, permission,
validation order, idempotency, concurrency, audit, events, errors, rate limits.
It does **not** tabulate request and response bodies. Those are bound in
`openapi_ops.py` to representations derived from Appendix A, the canonical
database dictionary, minus the columns that Appendix A's own repeated rule — "no
generic mass assignment/serialization exposes sensitive/internal columns" —
together with §11.1's NO SECRET TRANSPORT and §17.2's CREDENTIAL INVARIANT
make unreturnable.

Where a specification genuinely fixes no field set, the schema says so rather
than inventing one. `DomainDnsRecordStatus.expected` is `type: object` because
Appendix A.7 stores it as `expected_json` and no appendix enumerates its shape.

## Verification

```bash
npm run validate   # harness: reconciliation, refs, error codes, permissions
npm run lint       # Redocly against .redocly.yaml
```

The reconciliation check is the important one. It fails if any operation in the
documents is missing from `catalog-reconciliation-v1.yaml`, if any `operationId`
is duplicated, if any path disagrees with its card, or if the total is not 107 —
which is the count Appendix C declares in its own preamble.
