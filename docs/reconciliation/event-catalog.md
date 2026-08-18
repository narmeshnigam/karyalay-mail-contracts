# Reconciliation — event catalog and envelope

T00.02 evidence, compared 2026-08-18. Disposition:
[ADR-KEM-006](../adr/ADR-KEM-006-event-catalog-and-envelope-reconciliation.md).

## 1. Envelope

| Member | Master §22.3 | Repo 1 §31.1 | Published in `events/envelope-v1.schema.json` |
| --- | --- | --- | --- |
| `event` | yes | yes | yes |
| `version` | yes | yes | yes |
| `event_id` | yes | yes | yes |
| `occurred_at` | yes | yes | yes |
| `producer` | yes | yes | yes |
| `trace_id` | yes | yes | yes |
| `request_id` | **yes** | **absent** | yes — Master §0.2 precedence |
| `organisation_id` | yes | yes | yes |
| aggregate reference | `resource {type, id, generation}` | `aggregate {type, id, version}` | `resource` — Master §0.2 precedence |
| `data` | yes | yes | yes |

`generation` and `version` are different numbers on the same row: Repo 1
Appendix A.5 and A.13 both carry a `version` (optimistic concurrency, Master
§24.5) **and** a `desired_generation` (reconciliation, Master §6.2). The
envelope carries the reconciliation number, because that is the one Master
§22.2 tells consumers to compare when ordering matters.

## 2. Master Appendix C reserved names against Repo 1 Appendix D

| Master reserved name | Producer (Master) | In Appendix D | Assessment |
| --- | --- | --- | --- |
| `organisation.created` | mail/control | — | **absent — genuine gap** |
| `organisation.suspended` | mail/control | `organisation.mail_restricted (near-equivalent)` | **renamed** in Appendix D |
| `domain.created` | mail/control | `domain.requested` | **renamed** in Appendix D |
| `domain.verification_requested` | mail/control | — | **absent — genuine gap** |
| `domain.verified` | mail/control | `domain.verified` | present |
| `domain.ready_for_cutover` | mail/control | `domain.ready_for_cutover` | present |
| `domain.activated` | mail/control | `domain.activated` | present |
| `domain.suspended` | mail/control | `domain.suspended` | present |
| `domain.deleted` | mail/control | `domain.released (+ domain.deletion_requested)` | **renamed** in Appendix D |
| `mailbox.requested` | mail/control | `mailbox.requested` | present |
| `mailbox.provisioned` | provisioning/control | `mailbox.provisioned` | present |
| `mailbox.provisioning_failed` | provisioning | `provisioning.failed` | **renamed** in Appendix D |
| `mailbox.restricted` | mail/control | `mailbox.restricted` | present |
| `mailbox.restriction_lifted` | mail/control | `mailbox.restriction_cleared` | **renamed** in Appendix D |
| `mailbox.suspended` | mail/control | `mailbox.suspended` | present |
| `mailbox.deleted` | mail/control | `mailbox.deleted` | present |
| `mailbox.restored` | mail/control/ops | `mailbox.restored` | present |
| `quota.changed` | mail/control | `quota.changed` | present |
| `dkim.rotation_started` | mail/ops | — | not a Repo 1 fact — owned by Repo 1/Repo 4 (see note) |
| `dkim.selector_activated` | infra/control | — | not a Repo 1 fact — owned by Repo 3 |
| `migration.started` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `migration.progressed` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `migration.completed` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `migration.failed` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `restore.started` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `restore.completed` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `abuse.case_opened` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `abuse.mailbox_restriction_requested` | ops | — | not a Repo 1 fact — owned by Repo 4 |
| `security.session_revoked` | identity/control | `security.session_revoked` | present |
| `security.credential_reset` | identity/control | — | **absent — genuine gap** |

| Figure | Value |
| --- | --- |
| Master reserved names | 30 |
| Present in Appendix D unchanged | 12 |
| Renamed in Appendix D | 5 |
| Owned by another repository | 10 |
| **Genuine gaps** | **3** |

## 3. Consumer expectations with no producer-side definition

Repo 4 Appendix E lists the subject families it consumes. Three name `mail.v1.*`
families that Repo 1 Appendix D does not define at all — a consumer subscribing
to a subject nothing publishes sees silence, which is indistinguishable from
no activity.

| Repo 4 consumes | Owner claimed | Defined in Appendix D? |
| --- | --- | --- |
| `mail.v1.domain.*` | Repo1 | yes |
| `mail.v1.mailbox.*` | Repo1 | yes |
| `mail.v1.auth.*` | Repo1/identity bridge | **no** |
| `mail.v1.submission.*` | Repo1 | yes |
| `mail.v1.delivery.*` | Repo1/Repo3 | **no** |
| `mail.v1.abuse.*` | Repo1/2 | **no** |

Additionally, Repo 1's **own** Appendix C.2 card states the endpoint "emits
`organisation.mail_settings_changed`". That event does not appear in Repo 1
Appendix D. One specification contradicting itself is the clearest possible
case for an ADR rather than a schema edit.

## 4. What `v0.1.0` publishes

| Artifact | Count |
| --- | --- |
| `events/envelope-v1.schema.json` | 1 |
| `events/<name>-v1.schema.json` | 45 |
| `events/catalog-v1.yaml` index rows | 45 |

Stream `KARYALAY_MAIL_EVENTS_V1`, subjects `mail.v1.<family>.<event>`,
`Nats-Msg-Id` = `event_id` (Repo 1 §31.2). Fourteen families:
`alias`, `data_export`, `dkim`, `domain`, `filters`, `forwarding`, `group`, `mailbox`, `organisation`, `provisioning`, `quota`, `security`, `submission`, `vacation`.

