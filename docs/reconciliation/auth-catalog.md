# Reconciliation — auth catalog

T00.03 evidence, compared 2026-08-18. Disposition:
[ADR-KEM-007](../adr/ADR-KEM-007-permission-and-role-naming-reconciliation.md).

## 1. Permission naming

Master Appendix B.1 gives twenty names introduced with "for example" and closes
with "the detailed matrix SHALL be machine-readable". Repo 1 Appendix B names
thirty-two. The vocabularies differ systematically: Master uses `.read` where
Repo 1 uses `.view`, and `mail_domain.` where Repo 1 uses `domain.`.

| Master Appendix B.1 example | Nearest Repo 1 Appendix B permission |
| --- | --- |
| `mail_domain.read` | `domain.view` |
| `mail_domain.create` | `domain.create` |
| `mail_domain.update` | `domain.manage` |
| `mail_domain.delete` | `domain.delete` |
| `mailbox.read` | `mailbox.view` |
| `mailbox.create` | `mailbox.create` |
| `mailbox.update` | `mailbox.manage` |
| `mailbox.delete` | `mailbox.delete` |
| `mailbox.restore` | `mailbox.suspend` (covers suspend/restore as one) |
| `mailbox.security_reset` | `security.sessions_revoke` + `security.mfa_admin` |
| `alias.manage` | `alias.manage` |
| `group.manage` | `group.manage` |
| `mail_policy.manage` | `domain.manage` |
| `security_event.read` | `audit.view` |
| `audit.read` | `audit.view` |
| `billing.manage` | **none — out of scope for the mail catalog** |

## 2. Role catalog and its permission bundles

Roles come from Master §10.2 (customer) and §10.3 (platform); the bundles are
the inverse index of Repo 1 Appendix B. The harness proves the two published
files are consistent inverses of each other.

| Role | Scope | Default permissions |
| --- | --- | --- |
| `org_owner` | customer | 21 |
| `mail_admin` | customer | 19 |
| `helpdesk_admin` | customer | 4 |
| `security_admin` | customer | 7 |
| `billing_admin` | customer | 2 |
| `auditor` | customer | 8 |
| `mailbox_user` | customer | 7 |
| `platform_ops` | platform | 2 |
| `platform_support` | platform | 2 |
| `platform_security` | platform | **0 — see ADR-KEM-007** |
| `abuse_analyst` | platform | 1 |
| `deliverability_analyst` | platform | **0 — see ADR-KEM-007** |
| `platform_billing` | platform | **0 — see ADR-KEM-007** |
| `break_glass_admin` | platform | 1 |

## 3. Claims

No role or permission claim is defined. Repo 1 §8.1 step 3 loads active
membership and effective role assignments from canonical projections on every
request, and §18 evaluates five factors of which the permission is one. A role
claim in the token would let a stale assertion stand in for that evaluation.
`karyalay_organisation_id` is published as **advisory only** for the same
reason: §8.1 step 2 resolves the organisation without trusting a client-supplied
value.

T00.03's acceptance criterion — "claims schema validates a sample token for each
defined role" — is met by `auth/examples/`: one fixture per role, each recording
the role the subject is expected to resolve to server-side, all validating
against the one schema. The harness fails if a role has no fixture.

