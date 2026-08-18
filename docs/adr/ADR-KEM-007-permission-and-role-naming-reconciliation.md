# ADR-KEM-007 — Reconciling permission naming and the role catalog

| Field | Value |
| --- | --- |
| Status | **PROPOSED** |
| Date | 2026-08-18 |
| Raised by | Gate 0 task T00.03 (claims, roles and permissions contracts) |
| Affects | Master Contract Appendix B.1, §10.2, §10.3; Repo 1 Appendix B, §18 |
| Approvers | Architecture owner — pending |

## Context

T00.03 published `auth/permissions-v1.yaml` (32 permissions from Repo 1
Appendix B), `auth/roles-v1.yaml` (14 roles from Master §10.2/§10.3) and
`auth/claims-v1.yaml`. Two divergences surfaced.

## Divergence 1 — permission naming

Master Appendix B.1 gives twenty example permission names in `resource.action`
form. Repo 1 Appendix B names thirty-two, in the same form but with different
vocabulary:

| Master Appendix B.1 | Repo 1 Appendix B |
| --- | --- |
| `mail_domain.read` / `.create` / `.update` / `.delete` | `domain.view` / `.create` / `.manage` / `.delete` |
| `mailbox.read` / `.update` / `.restore` | `mailbox.view` / `.manage` / `.suspend` |
| `mailbox.security_reset` | — (covered by `security.sessions_revoke` + `security.mfa_admin`) |
| `security_event.read` | — (`audit.view` covers the tenant audit trail) |
| `audit.read` | `audit.view` |
| `billing.manage` | — (no billing permission in the mail catalog) |

The pattern is consistent: Master uses `.read`, Repo 1 uses `.view`; Master
prefixes `mail_domain`, Repo 1 uses `domain`.

Master Appendix B.1 introduces its list with "**for example**" and closes with
"the detailed matrix SHALL be machine-readable" — so it is illustrative of the
*form*, and delegates the vocabulary to the machine-readable catalog this task
produced. That reading makes the divergence a non-conflict.

## Divergence 2 — three roles with no permissions

Master §10.3 defines seven platform roles. Repo 1 Appendix B grants permissions
to four of them. Three receive nothing:

| Role | Master §10.3 purpose | Appendix B grants |
| --- | --- | --- |
| `platform_security` | security incident controls and privileged investigations | none |
| `deliverability_analyst` | IP/domain/provider reputation and delivery diagnostics | none |
| `platform_billing` | commercial subscription support | none |

A role that grants nothing is not harmless. Master §10.1 makes the permission
the enforcement primitive and the role a bundle; a bundle of zero permissions
means anyone assigned that role can do nothing, so an operator will either
assign a stronger role instead — silently over-granting — or the role will be
implemented with an undocumented permission invented at the call site, which
Repo 1 §18 forbids outright.

`deliverability_analyst` is the one with an immediate consequence: the
deliverability workstream is live now (BUILD-ORDER §4, "the longest-lead-time
item in the programme") and has no permission to stand behind.

Note that `platform_security` is a fourth spelling problem: Repo 1 Appendix B
grants `security.mfa_admin`, `mailbox.suspend` and `domain.dkim_rotate` to
`security_admin`, which Master §10.2 lists as a **customer** role, while
Master §10.3's platform equivalent is `platform_security`. The two are distinct
roles and only one of them has permissions.

## Decision (proposed)

1. **Permission vocabulary:** `auth/permissions-v1.yaml` publishes Repo 1
   Appendix B verbatim. Master Appendix B.1 is illustrative of form, and the
   next master revision should say so explicitly rather than list examples that
   read as normative names.
2. **Role catalog:** `auth/roles-v1.yaml` publishes the Master §10.2/§10.3
   catalog — all fourteen roles, because the Master owns the role catalog at a
   shared boundary. Three carry an empty `default_permissions` set, marked as
   such rather than silently omitted.
3. **The three empty roles are referred to the Repo 1 owner** as an Appendix B
   gap. They are **not** filled here: inventing a permission set for
   `platform_security` would be exactly the policy invention Master §0.2
   forbids.
4. **Claims:** no role or permission claim is defined. Repo 1 §8.1 step 3 loads
   membership and effective role assignments from canonical projections on every
   request, and §18 evaluates five factors of which the permission is one. A
   role claim would let a stale assertion stand in for that evaluation.

## Consequences

- Any consumer can compute a role's default permission bundle from the two
  published files, and the harness proves the two are inverse indexes.
- Work needing `deliverability_analyst`, `platform_security` or
  `platform_billing` authority has no permission to check until item 3 lands.
  Until then those roles must not be assigned in any environment.

## Evidence

`docs/reconciliation/auth-catalog.md`.
