"""Payload field type table for the event catalog.

Repo 1 Appendix D lists each event's *minimum semantic fields* by name and
states explicitly: "generated JSON Schema defines exact types/nullability."
This table is that definition. Every entry cites the normative source that
fixes the type, so a reviewer can check the derivation without re-reading the
whole specification.

Rules used, in order:
  1. Master §6.3 canonical naming fixes the identifier fields.
  2. Master §6.2 fixes UUID form and the `generation` integer.
  3. Repo 1 Appendix A fixes column types and enumerations for the rest.
  4. Repo 1 §33 / Appendix F fixes state values.
Anything none of those four fix is typed as a bounded string and marked so.
"""

UUID = {"type": "string", "format": "uuid"}
TIMESTAMP = {"type": "string", "format": "date-time"}


def _s(max_length, **extra):
    out = {"type": "string", "minLength": 1, "maxLength": max_length}
    out.update(extra)
    return out


FIELDS = {
    # --- canonical identifiers (Master §6.3, §6.2) -------------------------
    "organisation_id": (UUID, "Master §6.3 canonical tenant identifier; Master §6.2 UUID."),
    "domain_id": (UUID, "Master §6.3 canonical hosted-domain identifier."),
    "mailbox_id": (UUID, "Master §6.3 canonical mailbox identifier."),
    "from_organisation_id": (UUID, "Master §6.3 organisation_id, qualified by transfer direction (Repo 1 §10.4)."),
    "to_organisation_id": (UUID, "Master §6.3 organisation_id, qualified by transfer direction (Repo 1 §10.4)."),
    "alias_id": (UUID, "Repo 1 Appendix A.20 aliases.id BINARY(16)."),
    "group_id": (UUID, "Repo 1 Appendix A.22 distribution_groups.id BINARY(16)."),
    "key_id": (UUID, "Repo 1 Appendix A.11 dkim_keys.id BINARY(16)."),
    "credential_id": (UUID, "Repo 1 Appendix A.27 app_passwords.id BINARY(16)."),
    "session_id": (UUID, "Repo 1 Appendix A.28 mail_sessions.id BINARY(16)."),
    "submission_id": (UUID, "Repo 1 Appendix A.34 send_submission_records.id BINARY(16)."),
    "operation_id": (UUID, "Repo 1 Appendix A.31 provisioning_operations.id BINARY(16)."),
    "transfer_id": (UUID, "Repo 1 Appendix A.43 domain_transfer_operations.id BINARY(16)."),
    "export_id": (UUID, "Repo 1 Appendix A.42 data_export_jobs.id BINARY(16)."),
    "resource_id": (UUID, "Repo 1 Appendix A.31 provisioning_operations.resource_id BINARY(16)."),

    # --- non-UUID identifiers ---------------------------------------------
    "identity_subject": (
        _s(255, description="OIDC subject. Not a UUID: Repo 1 Appendix A.2 stores it as VARCHAR(255)."),
        "Repo 1 Appendix A.2/A.3 identity_subject VARCHAR(255).",
    ),
    "requested_by": (
        _s(255, description="OIDC subject of the requesting principal."),
        "Repo 1 §10.4 / Appendix A.2 identity_subject VARCHAR(255).",
    ),
    "cluster_id": (
        _s(64, description="Logical mail cluster the mailbox was observed ready on."),
        "Repo 1 Appendix A.14 mailbox_placements.cluster_id VARCHAR(64).",
    ),
    "smtp_queue_id": (
        _s(64, description="Postfix queue identifier for the accepted message. Opaque; not a UUID."),
        "Repo 1 §23.1 / Master §30.3 queue-ID correlation model.",
    ),

    # --- generations and counters (Master §6.2) ---------------------------
    "generation": (
        {"type": "integer", "minimum": 0, "description": "Desired revision of the resource."},
        "Master §6.2: every resource participating in reconciliation carries an integer generation.",
    ),
    "desired_generation": (
        {"type": "integer", "minimum": 0},
        "Master §6.2; Repo 1 §29.1 desired/observed rule.",
    ),
    "observed_generation": (
        {"type": "integer", "minimum": 0},
        "Master §6.2; Repo 1 Appendix A.32 observed_resource_states.generation.",
    ),
    "external_target_count": (
        {"type": "integer", "minimum": 0, "description": "Count only. The targets themselves are not carried (Master §22.5)."},
        "Repo 1 §15; Master §22.5 data minimisation.",
    ),
    "old_bytes": (
        {"type": "integer", "minimum": 0, "description": "Previous configured mailbox quota in bytes."},
        "Repo 1 Appendix A.15 mailbox_usage quota columns; Master §20.2 explicit units.",
    ),
    "new_bytes": (
        {"type": "integer", "minimum": 0, "description": "New configured mailbox quota in bytes."},
        "Repo 1 Appendix A.15 mailbox_usage quota columns; Master §20.2 explicit units.",
    ),

    # --- timestamps (Master §20.2 RFC 3339 UTC) ---------------------------
    "verified_at": (TIMESTAMP, "Repo 1 Appendix A.6 domain_verifications; Master §20.2."),
    "released_at": (TIMESTAMP, "Repo 1 §10.4; Master §20.2."),
    "deleted_at": (TIMESTAMP, "Repo 1 Appendix A.13 mailboxes; Master §20.2."),
    "accepted_at": (TIMESTAMP, "Repo 1 Appendix A.34 send_submission_records; Master §20.2."),
    "expires_at": (TIMESTAMP, "Repo 1 Appendix A.42 data_export_jobs; Master §20.2."),
    "recovery_expires_at": (TIMESTAMP, "Repo 1 §12.3 recovery window; Master §20.2."),
    "not_before": (
        dict(TIMESTAMP, description="Earliest time the requested teardown may proceed."),
        "Repo 1 §10.4 / §12.3 deletion timing policy; Master §20.2.",
    ),

    # --- enumerations fixed by a specification ----------------------------
    "state": (
        {
            "type": "string",
            "enum": [
                "PROVISIONING", "ACTIVE", "PAYMENT_GRACE",
                "RESTRICTED", "DELETION_PENDING", "DELETED",
            ],
            "description": "Organisation mail service state.",
        },
        "Repo 1 §33.1 organisation state machine.",
    ),
    "restriction_codes": (
        {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "enum": [
                    "SEND_BLOCKED", "SEND_RATE_REDUCED", "AUTH_BLOCKED",
                    "FORWARDING_BLOCKED", "ADMIN_CHANGES_FROZEN",
                ],
            },
        },
        "Repo 1 Appendix A.30 restrictions.restriction_code VARCHAR(48) enumeration.",
    ),
    "resource_type": (
        {
            "type": "string",
            "enum": ["DOMAIN", "MAILBOX", "DKIM", "FILTER", "QUOTA", "PLACEMENT"],
        },
        "Repo 1 Appendix A.31 provisioning_operations.resource_type VARCHAR(32) enumeration.",
    ),
    "retryable": (
        {"type": "boolean", "description": "Whether the provisioning failure is safe to retry without operator action."},
        "Repo 1 §39 retry classes; Appendix A.31 state RETRYABLE_FAILURE vs FAILED_ACTION_REQUIRED.",
    ),
    "enabled": ({"type": "boolean"}, "Repo 1 §15 forwarding/vacation rule state."),
    "change": (
        {"type": "string", "enum": ["GRANTED", "REVOKED"], "description": "Direction of the role assignment change."},
        "Repo 1 Appendix A.3 role_assignments lifecycle; Master §22.4 past-tense fact naming.",
    ),

    # --- bounded strings whose values no specification enumerates ---------
    "error_code": (
        _s(
            64,
            pattern="^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$",
            description="Stable error identifier from errors/error-catalog-v1.yaml. The catalog, not this schema, is the closed set.",
        ),
        "Repo 1 Appendix E; Appendix A.31 last_error_code VARCHAR(64).",
    ),
    "reason_code": (
        _s(64, pattern="^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$", description="Stable reason code."),
        "Repo 1 Appendix A.30 restrictions.reason_code VARCHAR(64).",
    ),
    "role_code": (
        _s(64, pattern="^[a-z][a-z0-9_]*$", description="Canonical role code from auth/roles-v1.yaml."),
        "Repo 1 Appendix A.3 role_assignments.role_code VARCHAR(64).",
    ),
    "source_version": (
        _s(128, description="Commercial entitlement snapshot version; opaque and monotonic to the commercial system."),
        "Repo 1 Appendix A.4 entitlement_snapshots.source_version VARCHAR(128); §9.1 stale-version rejection.",
    ),
    "selector": (
        _s(63, pattern="^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", description="DKIM selector; a DNS label, never a secret."),
        "Master Appendix F.3 (non-secret bounded DNS label); RFC 6376 selector syntax.",
    ),
    "label": (
        _s(64, description="User-supplied app-password label. Never the credential."),
        "Repo 1 Appendix A.27 app_passwords.label; §17.2 credential invariant.",
    ),
    "ascii_name": (
        _s(253, pattern="^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z]{2,63}$",
           description="Hosted domain in IDNA A-label canonical form, lower-cased."),
        "Master §6.4 canonical DNS form; Repo 1 Appendix A.5 mail_domains.",
    ),
    "address": (
        _s(320, format="idn-email", description="Canonical address. Classified data: consumer access is restricted (Repo 1 §31.3)."),
        "Repo 1 §6.1 address canonicalization; Appendix A.12 address_registry.",
    ),
    "changed_fields": (
        {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$", "maxLength": 64},
            "description": "Names of the fields that changed. Names only — values are not carried (Master §22.5).",
        },
        "Master §22.5 data minimisation; Repo 1 §31.3 event privacy.",
    ),
}
