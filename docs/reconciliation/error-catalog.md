# Reconciliation — error catalog

T00.01 evidence. Master Contract Appendix D (26 baseline codes) against
`karyalay-mail` repository-spec-v1.0 Appendix E (80 codes), compared on 2026-08-18.
Disposition: [ADR-KEM-005](../adr/ADR-KEM-005-error-catalog-baseline-reconciliation.md).

Master Appendix D's column is headed **HTTP class**, and several of its entries
are ranges (`401/403 by flow`, `409/202 status`). A range that contains
Appendix E's single value is a *narrowing*, not a conflict — Appendix E is the
detailed catalog the baseline delegates to. Only a value **outside** the
Master's range is a real divergence.

## Master Appendix D against Appendix E

| Master code | Master HTTP class | In Appendix E | Appendix E HTTP | Status |
| --- | --- | --- | --- | --- |
| `AUTH_REQUIRED` | 401 | `AUTH_REQUIRED` | 401 | match |
| `AUTH_INVALID` | 401 | — | — | **absent — see ADR-KEM-005** |
| `AUTH_MFA_REQUIRED` | 401/403 by flow | `AUTH_MFA_REQUIRED` | 401 | narrowed within the Master range |
| `AUTHZ_FORBIDDEN` | 403 | `AUTHZ_FORBIDDEN` | 403 | match |
| `MAIL_DOMAIN_NOT_FOUND` | 404 | `MAIL_DOMAIN_NOT_FOUND` | 404 | match |
| `MAIL_DOMAIN_NOT_VERIFIED` | 409 | `MAIL_DOMAIN_NOT_VERIFIED` | 409 | match |
| `MAIL_DOMAIN_NOT_ACTIVE` | 409 | `MAIL_DOMAIN_NOT_ACTIVE` | 409 | match |
| `MAILBOX_NOT_FOUND` | 404 | `MAILBOX_NOT_FOUND` | 404 | match |
| `MAILBOX_ALREADY_EXISTS` | 409 | `MAILBOX_ALREADY_EXISTS` | 409 | match |
| `MAILBOX_NOT_ACTIVE` | 409 | `MAILBOX_NOT_ACTIVE` | 409 | match |
| `MAILBOX_RESTRICTED` | 403/409 | `MAILBOX_RESTRICTED` | 403 | narrowed within the Master range |
| `MAILBOX_SUSPENDED` | 403 | `MAILBOX_SUSPENDED` | 403 | match |
| `MAILBOX_QUOTA_EXCEEDED` | 409 | `MAILBOX_QUOTA_EXCEEDED` | 507 | **outside the Master range** |
| `SENDER_IDENTITY_NOT_AUTHORIZED` | 403 | — | — | **absent — see ADR-KEM-005** |
| `MESSAGE_TOO_LARGE` | 413 | `MESSAGE_TOO_LARGE` | 413 | match |
| `TOO_MANY_RECIPIENTS` | 422/429 | — | — | **absent — see ADR-KEM-005** |
| `PROVISIONING_IN_PROGRESS` | 409/202 status | `PROVISIONING_IN_PROGRESS` | 409 | narrowed within the Master range |
| `PROVISIONING_FAILED` | 409/500 by caller | `PROVISIONING_FAILED` | 503 | **outside the Master range** |
| `MAIL_STORAGE_UNAVAILABLE` | 503 | `MAIL_STORAGE_UNAVAILABLE` | 503 | match |
| `DEPENDENCY_UNAVAILABLE` | 503 | `DEPENDENCY_UNAVAILABLE` | 503 | match |
| `RATE_LIMIT_EXCEEDED` | 429 | `RATE_LIMIT_EXCEEDED` | 429 | match |
| `ABUSE_RESTRICTED` | 403/429 | `ABUSE_RESTRICTED` | 403 | narrowed within the Master range |
| `IDEMPOTENCY_CONFLICT` | 409 | — | — | **absent — see ADR-KEM-005** |
| `CONCURRENCY_CONFLICT` | 409/412 | — | — | **absent — see ADR-KEM-005** |
| `VALIDATION_FAILED` | 422 | `VALIDATION_FAILED` | 422 | match |
| `INTERNAL_ERROR` | 500 | `INTERNAL_ERROR` | 500 | match |

## The two real HTTP divergences

| Code | Master Appendix D | Appendix E | Note |
| --- | --- | --- |  --- |
| `MAILBOX_QUOTA_EXCEEDED` | 409 | **507** | 507 Insufficient Storage is the semantically exact status. |
| `PROVISIONING_FAILED` | 409/500 by caller | **503** | 503 with `OPERATOR_ATTENTION` says *retry will not help until someone acts*, which 500 does not. |

Both are cases where Appendix E is the more precise statement. ADR-KEM-005
proposes Appendix E stands and the Master baseline is corrected.

## Appendix E codes not in the Master baseline

Fifty-nine. Expected: the Master carries a *baseline*, Appendix E the detailed
catalog. Not a divergence.

| Code | HTTP | Retry class |
| --- | --- | --- |
| `AUTH_INVALID_TOKEN` | 401 | AUTH_REFRESH |
| `AUTH_REAUTH_REQUIRED` | 401 | NON_RETRYABLE |
| `AUTHZ_RESOURCE_NOT_VISIBLE` | 404 | NON_RETRYABLE |
| `ORGANISATION_NOT_FOUND` | 404 | NON_RETRYABLE |
| `ORGANISATION_NOT_ACTIVE` | 409 | NON_RETRYABLE |
| `ENTITLEMENT_LIMIT_EXCEEDED` | 409 | NON_RETRYABLE |
| `ENTITLEMENT_FEATURE_DISABLED` | 403 | NON_RETRYABLE |
| `MAIL_DOMAIN_ALREADY_HOSTED` | 409 | NON_RETRYABLE |
| `MAIL_DOMAIN_INVALID` | 422 | NON_RETRYABLE |
| `DOMAIN_VERIFICATION_PENDING` | 409 | RETRY_AFTER |
| `DOMAIN_VERIFICATION_EXPIRED` | 410 | NON_RETRYABLE |
| `DNS_RESOLUTION_TEMPORARY_FAILURE` | 503 | RETRYABLE_BACKOFF |
| `DNS_REQUIREMENT_NOT_MET` | 409 | NON_RETRYABLE |
| `DKIM_KEY_NOT_READY` | 409 | RETRY_AFTER |
| `DKIM_ROTATION_IN_PROGRESS` | 409 | RETRY_AFTER |
| `DKIM_ROTATION_FAILED` | 503 | OPERATOR_ATTENTION |
| `DKIM_KEY_REVOKED` | 409 | NON_RETRYABLE |
| `MAILBOX_OVER_ENTITLEMENT` | 409 | NON_RETRYABLE |
| `MAILBOX_RECOVERY_WINDOW_EXPIRED` | 410 | NON_RETRYABLE |
| `ADDRESS_ALREADY_IN_USE` | 409 | NON_RETRYABLE |
| `ADDRESS_INVALID` | 422 | NON_RETRYABLE |
| `ALIAS_NOT_FOUND` | 404 | NON_RETRYABLE |
| `ALIAS_LOOP_DETECTED` | 422 | NON_RETRYABLE |
| `GROUP_NOT_FOUND` | 404 | NON_RETRYABLE |
| `GROUP_EXPANSION_LIMIT` | 422 | NON_RETRYABLE |
| `FORWARDING_NOT_ALLOWED` | 403 | NON_RETRYABLE |
| `FORWARDING_TARGET_UNVERIFIED` | 409 | NON_RETRYABLE |
| `FILTER_RULE_INVALID` | 422 | NON_RETRYABLE |
| `FILTER_INSTALLATION_PENDING` | 409 | RETRY_AFTER |
| `VACATION_RANGE_INVALID` | 422 | NON_RETRYABLE |
| `SESSION_NOT_FOUND` | 404 | NON_RETRYABLE |
| `APP_PASSWORD_NOT_ALLOWED` | 403 | NON_RETRYABLE |
| `APP_PASSWORD_LIMIT_EXCEEDED` | 409 | NON_RETRYABLE |
| `APP_PASSWORD_NOT_FOUND` | 404 | NON_RETRYABLE |
| `PROVISIONING_STALE_OBSERVATION` | 409 | NON_RETRYABLE |
| `FOLDER_NOT_FOUND` | 404 | NON_RETRYABLE |
| `FOLDER_PROTECTED` | 409 | NON_RETRYABLE |
| `MESSAGE_NOT_FOUND` | 404 | NON_RETRYABLE |
| `MESSAGE_REFERENCE_STALE` | 409 | NON_RETRYABLE |
| `MESSAGE_BATCH_LIMIT` | 422 | NON_RETRYABLE |
| `SEARCH_QUERY_INVALID` | 422 | NON_RETRYABLE |
| `SEARCH_UNAVAILABLE` | 503 | RETRYABLE_BACKOFF |
| `DRAFT_VERSION_CONFLICT` | 412 | NON_RETRYABLE |
| `ATTACHMENT_NOT_FOUND` | 404 | NON_RETRYABLE |
| `ATTACHMENT_UPLOAD_EXPIRED` | 410 | NON_RETRYABLE |
| `ATTACHMENT_BLOCKED` | 422 | NON_RETRYABLE |
| `SUBMISSION_SENDER_NOT_AUTHORIZED` | 403 | NON_RETRYABLE |
| `SUBMISSION_RECIPIENT_LIMIT` | 422 | NON_RETRYABLE |
| `SUBMISSION_MESSAGE_TOO_LARGE` | 413 | NON_RETRYABLE |
| `SUBMISSION_TEMPORARY_FAILURE` | 503 | RETRYABLE_BACKOFF |
| `SUBMISSION_REJECTED` | 422 | NON_RETRYABLE |
| `SUBMISSION_STATUS_UNKNOWN` | 202 | RECONCILIATION_REQUIRED |
| `SUBMISSION_ALREADY_ACCEPTED` | 409 | NON_RETRYABLE |
| `IDEMPOTENCY_KEY_REQUIRED` | 400 | NON_RETRYABLE |
| `IDEMPOTENCY_KEY_REUSED` | 409 | NON_RETRYABLE |
| `IDEMPOTENCY_IN_PROGRESS` | 409 | RETRY_AFTER |
| `VERSION_CONFLICT` | 412 | NON_RETRYABLE |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | NON_RETRYABLE |
| `REQUEST_TOO_LARGE` | 413 | NON_RETRYABLE |

## Counts

| Figure | Value |
| --- | --- |
| Appendix E codes | 80 |
| Master baseline codes | 26 |
| Identical HTTP mapping | 15 |
| Appendix E narrows a Master range | 4 |
| **Appendix E outside the Master range** | **2** |
| **Master name absent from Appendix E** | **5** |
| Appendix E only | 59 |

## Retry-class coverage

Every Appendix E code carries one of the six §39 retry classes; the harness
check `errors/error-catalog-v1.yaml validates against error-catalog-v1.schema.json`
fails if a seventh ever appears.

| Retry class | Codes |
| --- | --- |
| `NON_RETRYABLE` | 63 |
| `AUTH_REFRESH` | 1 |
| `RETRY_AFTER` | 7 |
| `RETRYABLE_BACKOFF` | 5 |
| `RECONCILIATION_REQUIRED` | 1 |
| `OPERATOR_ATTENTION` | 3 |
