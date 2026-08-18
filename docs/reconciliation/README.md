# Reconciliation notes

Gate 0 evidence. Each note is the field-by-field comparison behind one ADR:
what two specifications say about the same thing, where they differ, and what
`v0.1.0` published as a result.

These are **evidence, not contracts.** Nothing validates against them and no
consumer pins them. Where a note and an ADR disagree, the ADR is the decision
and the note is stale.

| Note | Task | Compares | ADR |
| --- | --- | --- | --- |
| [error-catalog.md](error-catalog.md) | T00.01 | Master Appendix D ↔ Repo 1 Appendix E | [ADR-KEM-005](../adr/ADR-KEM-005-error-catalog-baseline-reconciliation.md) |
| [event-catalog.md](event-catalog.md) | T00.02 | Master §22.3/Appendix C ↔ Repo 1 §31.1/Appendix D ↔ Repo 4 Appendix E | [ADR-KEM-006](../adr/ADR-KEM-006-event-catalog-and-envelope-reconciliation.md) |
| [auth-catalog.md](auth-catalog.md) | T00.03 | Master Appendix B.1/§10.2/§10.3 ↔ Repo 1 Appendix B | [ADR-KEM-007](../adr/ADR-KEM-007-permission-and-role-naming-reconciliation.md) |
| [provisioning-interface.md](provisioning-interface.md) | T00.05 | Repo 1 §12.2/§29/A.31/A.32 ↔ Repo 3 §48–§51 | [ADR-KEM-008](../adr/ADR-KEM-008-desired-state-and-observation-shape.md) |
| [openapi-consumption.md](openapi-consumption.md) | T00.04 | Repo 1 Appendix C ↔ Repo 2 Appendix E | — (no divergence) |

## What Gate 0 found

Five reconciliations produced four proposed ADRs. That is not a sign the
specifications are poor — it is the expected yield of the first exercise that
forced four independently written documents to agree on one machine-readable
artifact. Every divergence below was invisible while the contracts lived in
prose:

| Finding | Would have surfaced at |
| --- | --- |
| Envelope disagreement (`resource` vs `aggregate`, missing `request_id`) | First cross-repo event consumption — after both sides were built |
| Three `mail.v1.*` subject families Repo 4 consumes and nobody publishes | Production, as silence |
| Desired-state shape disagreement | Repo 1 ↔ Repo 3 integration |
| Readiness enum: 3 of 6 Repo 3 values unstorable | First `RESTRICTED` observation, read as a fault |
| Five duplicate error-code names | Client error handling, per client |
| Three roles with no permissions | First attempt to assign one |
