# Reconciliation — OpenAPI against the webmail consumption matrix

T00.04 evidence, compared 2026-08-18. **No divergence found**, so no ADR.

karyalay-webmail Appendix E is the client-side cross-check on the public
surface: it maps the Repo 1 endpoints the browser calls. Its own preamble states
internal endpoints C.97-C.107 are explicitly forbidden to browser code.

## Coverage

| Figure | Value |
| --- | --- |
| Endpoints webmail consumes | 47 |
| Of those, present in the published OpenAPI | 47 |
| Of those, missing | 0 |

## The C.92-C.95 gap is intentional

T00.04 flags it: webmail does not consume C.92 (audit events), C.93 (security
events), C.94 (create export) or C.95 (get export). Those are administrative
surfaces with no webmail screen, so their absence from Appendix E is
non-consumption, not an omission. All four are published in
`public-control-api-v1.yaml` regardless — Appendix C is exhaustive by invariant
and the contract does not shrink to fit one client.

| Catalog id | Endpoint | In webmail Appendix E |
| --- | --- | --- |
| `C.92` | `listAuditEvents` | no — intentional |
| `C.93` | `listSecurityEvents` | no — intentional |
| `C.94` | `createDataExport` | no — intentional |
| `C.95` | `getDataExport` | no — intentional |
| `C.96` | `listMailboxRestrictions` | yes |

## Which document serves each consumed endpoint

| Document | Endpoints webmail consumes |
| --- | --- |
| `mailbox-api-v1.yaml` | 26 |
| `public-control-api-v1.yaml` | 21 |

The split follows the backend, not the caller: `mailbox-api-v1.yaml` holds the
operations Repo 1 §28 serves through MailboxBackend and SubmissionGateway;
everything else is control-plane. Webmail consumes from both, which is expected
— the two documents are a producer-side boundary, not a client-side one.

## Client rules that became contract constraints

Several Appendix E "critical client rules" are enforceable in the contract, and
are enforced there rather than left to client discipline:

| Appendix E rule | Where it lives in the contract |
| --- | --- |
| "Secret values never returned after creation" (C.63) | `AppPassword` withholds `secret_verifier`; only `AppPasswordCreated` (C.64) carries a secret. |
| "If-Match; conflict UX" (C.85) | `If-Match` is a required header on `replaceDraft`. |
| "Protected folders denied" (C.68) | `Folder.protected` is a required response member. |
| "Bounded/partial results" (C.76, C.77) | `BulkMutationResult` returns a per-item outcome, so partial failure cannot be reported as success. |
| "Explicit confirmation; never blind retry" (C.79) | `ExpungeRequest.confirm` is required and `const: true`. |
| "No public object URL" (C.88) | `StagedAttachment` withholds `storage_ref`. |

