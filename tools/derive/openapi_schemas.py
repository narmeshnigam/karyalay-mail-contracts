"""Resource representations for the OpenAPI documents.

Every schema names the Appendix A table it represents and, where columns are
withheld, says which and why. Withholding is not a design preference: Repo 1
Appendix A repeats "no generic mass assignment/serialization exposes
sensitive/internal columns" under every table, and §11.1's NO SECRET TRANSPORT
rule and §17.2's CREDENTIAL INVARIANT make specific columns unreturnable.
"""

UUID = {"type": "string", "format": "uuid"}
TS = {"type": "string", "format": "date-time"}
VERSION = {"type": "integer", "minimum": 1, "description": "Optimistic concurrency version; surfaced as the ETag (Master §24.5)."}
GENERATION = {"type": "integer", "minimum": 0}


def _obj(description, properties, required=None, source=None, withheld=None):
    schema = {"type": "object", "description": description, "properties": properties}
    if required:
        schema["required"] = required
    comment = []
    if source:
        comment.append("Source: %s." % source)
    if withheld:
        comment.append("Withheld: %s" % withheld)
    if comment:
        schema["$comment"] = " ".join(comment)
    return schema


SCHEMAS = {
    # --- organisation -----------------------------------------------------
    "OrganisationMailProfile": _obj(
        "Organisation mail activation state, limits summary and safe health summary.",
        {
            "organisation_id": UUID,
            "name": {"type": "string", "maxLength": 255},
            "mail_state": {"type": "string", "enum": ["PROVISIONING", "ACTIVE", "PAYMENT_GRACE", "RESTRICTED", "DELETION_PENDING", "DELETED"]},
            "default_timezone": {"type": "string", "description": "IANA time zone name."},
            "domain_count": {"type": "integer", "minimum": 0},
            "mailbox_count": {"type": "integer", "minimum": 0},
            "version": VERSION,
            "created_at": TS,
            "updated_at": TS,
        },
        ["organisation_id", "mail_state", "version"],
        "Repo 1 Appendix A.1 organisations; §33.1 state machine",
        "external_organisation_id and deleted_at — commercial-system linkage and tombstone metadata, not product state.",
    ),
    "OrganisationMailProfileUpdate": _obj(
        "Mutable organisation-level mail settings.",
        {"name": {"type": "string", "maxLength": 255}, "default_timezone": {"type": "string"}},
        None,
        "Repo 1 Appendix A.1",
    ),
    "EntitlementSnapshot": _obj(
        "Effective entitlement snapshot and usage against limits.",
        {
            "organisation_id": UUID,
            "source_version": {"type": "string", "maxLength": 128, "description": "Commercial entitlement version. The commercial system remains source of truth (C.3 notes)."},
            "plan_code": {"type": "string", "maxLength": 64},
            "features": {"type": "object", "additionalProperties": {"type": "boolean"}},
            "limits": {"type": "object", "additionalProperties": {"type": "integer"}},
            "usage": {"type": "object", "additionalProperties": {"type": "integer"}},
            "effective_from": TS,
            "effective_until": {"oneOf": [TS, {"type": "null"}]},
        },
        ["organisation_id", "source_version", "plan_code"],
        "Repo 1 Appendix A.4 entitlement_snapshots; §9",
    ),
    "Member": _obj(
        "Mail-related organisation membership and effective role assignments.",
        {
            "identity_subject": {"type": "string", "maxLength": 255},
            "status": {"type": "string", "enum": ["ACTIVE", "INVITED", "SUSPENDED", "REMOVED"]},
            "joined_at": TS,
            "roles": {"type": "array", "items": {"$ref": "#/components/schemas/RoleAssignment"}},
        },
        ["identity_subject", "status", "roles"],
        "Repo 1 Appendix A.2 organisation_memberships and A.3 role_assignments",
    ),
    "RoleAssignment": _obj(
        "One role granted to a subject, optionally scoped below the organisation.",
        {
            "role_code": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$", "maxLength": 64, "description": "A role from auth/roles-v1.yaml."},
            "scope_type": {"type": "string", "enum": ["ORGANISATION", "DOMAIN", "MAILBOX"]},
            "scope_id": {"oneOf": [UUID, {"type": "null"}]},
            "granted_by": {"type": "string", "maxLength": 255},
            "expires_at": {"oneOf": [TS, {"type": "null"}]},
        },
        ["role_code", "scope_type"],
        "Repo 1 Appendix A.3 role_assignments",
    ),
    "MemberRolesReplacement": _obj(
        "Complete replacement of a subject's mail role assignments.",
        {"roles": {"type": "array", "items": {"$ref": "#/components/schemas/RoleAssignment"}, "maxItems": 32}},
        ["roles"],
        "Repo 1 Appendix A.3; C.5 forbids removing the last org_owner without replacement.",
    ),

    # --- domain -----------------------------------------------------------
    "Domain": _obj(
        "Hosted domain, its lifecycle state and its readiness gates.",
        {
            "domain_id": UUID,
            "organisation_id": UUID,
            "ascii_name": {"type": "string", "maxLength": 253, "description": "IDNA A-label canonical form (Master §6.4)."},
            "unicode_name": {"oneOf": [{"type": "string", "maxLength": 253}, {"type": "null"}], "description": "Display form; never a routing key."},
            "state": {"type": "string", "enum": ["REQUESTED", "OWNERSHIP_PENDING", "VERIFIED", "CONFIGURING", "READY_FOR_CUTOVER", "ACTIVE", "SUSPENDED", "DELETION_PENDING", "RELEASED"]},
            "desired_generation": GENERATION,
            "observed_generation": GENERATION,
            "readiness": {"$ref": "#/components/schemas/DomainReadiness"},
            "policy": {"$ref": "#/components/schemas/DomainPolicy"},
            "version": VERSION,
            "created_at": TS,
            "updated_at": TS,
        },
        ["domain_id", "organisation_id", "ascii_name", "state", "desired_generation", "observed_generation", "version"],
        "Repo 1 Appendix A.5 mail_domains, A.9 domain_policies; Appendix F.2 state machine",
        "primary_dkim_keyset_id — an internal foreign key; DKIM state is served by C.18.",
    ),
    "DomainReadiness": _obj(
        "The three gates of dns/domain-record-contract-v1.yaml, evaluated on a fresh snapshot.",
        {
            "ownership": {"$ref": "#/components/schemas/HealthState"},
            "dns_readiness": {"$ref": "#/components/schemas/HealthState"},
            "infrastructure": {"$ref": "#/components/schemas/HealthState"},
            "evaluated_at": TS,
        },
        ["ownership", "dns_readiness", "infrastructure", "evaluated_at"],
        "Repo 1 §10; dns/domain-record-contract-v1.yaml gates",
    ),
    "HealthState": {
        "type": "string",
        "enum": ["PASS", "WARN", "FAIL", "PENDING", "NOT_APPLICABLE"],
        "description": "Master §12.4. A single green boolean is explicitly insufficient.",
    },
    "DomainPolicy": _obj(
        "Per-domain product policy knobs.",
        {
            "allow_external_forwarding": {"type": "boolean"},
            "allow_catch_all": {"type": "boolean"},
            "max_message_bytes": {"type": "integer", "minimum": 0},
            "max_recipients": {"type": "integer", "minimum": 1},
            "retention_profile": {"type": "string", "maxLength": 64},
        },
        None,
        "Repo 1 Appendix A.9 domain_policies",
    ),
    "DomainCreateRequest": _obj(
        "Add a hosted domain.",
        {"name": {"type": "string", "maxLength": 253, "description": "Unicode or A-label; normalised to canonical IDNA A-label (Repo 1 §10.1 step 1)."}},
        ["name"],
        "Repo 1 §10.1",
    ),
    "DomainUpdate": _obj(
        "Change domain policy. May increment desired_generation (C.9 notes).",
        {"policy": {"$ref": "#/components/schemas/DomainPolicy"}},
        None,
        "Repo 1 Appendix A.9",
    ),
    "DomainVerificationChallenge": _obj(
        "The verification record the customer must publish. The raw token is returned exactly once, at creation or renewal (C.11 notes).",
        {
            "verification_id": UUID,
            "method": {"type": "string", "const": "DNS_TXT", "description": "DNS_TXT for v1 (Repo 1 Appendix A.6)."},
            "record_name": {"type": "string", "maxLength": 255},
            "record_value": {"type": "string", "description": "Present only in the response that creates or renews the challenge."},
            "expires_at": TS,
            "verified_at": {"oneOf": [TS, {"type": "null"}]},
            "attempt_count": {"type": "integer", "minimum": 0},
        },
        ["verification_id", "method", "record_name", "expires_at"],
        "Repo 1 Appendix A.6 domain_verifications; §10.1",
        "token_hash — the stored hash. Returning it would make the challenge forgeable.",
    ),
    "DomainDnsStatus": _obj(
        "Per-record requirement, latest observation and remediation guidance.",
        {
            "domain_id": UUID,
            "generation": GENERATION,
            "records": {"type": "array", "items": {"$ref": "#/components/schemas/DomainDnsRecordStatus"}},
        },
        ["domain_id", "generation", "records"],
        "Repo 1 Appendix A.7/A.8; dns/domain-record-contract-v1.yaml",
    ),
    "DomainDnsRecordStatus": _obj(
        "One required or recommended record and what the resolver last saw.",
        {
            "record_kind": {"type": "string", "enum": ["VERIFICATION_TXT", "MX", "SPF", "DKIM", "DMARC", "AUTOCONFIG", "AUTODISCOVER", "MTA_STS", "TLS_RPT", "CAA"]},
            "name": {"type": "string", "maxLength": 255},
            "expected": {"type": "object", "description": "Normalised expected value or policy (Repo 1 Appendix A.7 expected_json)."},
            "observed": {"oneOf": [{"type": "object"}, {"type": "null"}], "description": "Normalised safe observed values (Repo 1 Appendix A.8 observed_json)."},
            "required_for_activation": {"type": "boolean"},
            "observation_status": {"type": "string", "enum": ["MATCH", "MISSING", "MISMATCH", "TEMPORARY_ERROR"]},
            "health_state": {"$ref": "#/components/schemas/HealthState"},
            "checked_at": {"oneOf": [TS, {"type": "null"}]},
            "expires_at": {"oneOf": [TS, {"type": "null"}], "description": "Freshness boundary. A stale observation cannot satisfy a gate."},
            "remediation": {"type": "string", "description": "Operator-safe guidance (Master §12.4)."},
        },
        ["record_kind", "name", "expected", "required_for_activation", "observation_status", "health_state"],
        "Repo 1 Appendix A.7, A.8; Master §12.4",
        "resolver_trace_id — diagnostic correlation, not customer-facing.",
    ),
    "DkimState": _obj(
        "DKIM keyset, its rotation state and the published selectors.",
        {
            "keyset_id": UUID,
            "domain_id": UUID,
            "rotation_state": {"type": "string", "maxLength": 32},
            "rotation_due_at": {"oneOf": [TS, {"type": "null"}]},
            "active_key_id": {"oneOf": [UUID, {"type": "null"}]},
            "keys": {"type": "array", "items": {"$ref": "#/components/schemas/DkimKey"}},
            "version": VERSION,
        },
        ["keyset_id", "domain_id", "rotation_state", "keys"],
        "Repo 1 Appendix A.10 dkim_keysets; §11",
    ),
    "DkimKey": _obj(
        "One DKIM key. Public material only.",
        {
            "key_id": UUID,
            "selector": {"type": "string", "pattern": "^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$"},
            "algorithm": {"type": "string", "maxLength": 32},
            "public_key_b64": {"type": "string", "description": "Public key, base64. The only key material any API returns."},
            "state": {"type": "string", "enum": ["PLANNED", "PUBLISHED_PENDING", "ACTIVE", "ROTATING_OUT", "RETIRED", "REVOKED"]},
            "activated_at": {"oneOf": [TS, {"type": "null"}]},
            "retired_at": {"oneOf": [TS, {"type": "null"}]},
        },
        ["key_id", "selector", "algorithm", "public_key_b64", "state"],
        "Repo 1 Appendix A.11 dkim_keys; Appendix F.3 state machine",
        "private_key_ref — NO SECRET TRANSPORT (Repo 1 §11.1). C.18 additionally forbids returning it to non-platform clients.",
    ),
    "DkimRotateRequest": _obj(
        "Begin a DKIM rotation.",
        {"reason": {"type": "string", "maxLength": 512}},
        None,
        "Repo 1 §11.1",
    ),
    "DomainTransfer": _obj(
        "Controlled cross-organisation domain transfer.",
        {
            "transfer_id": UUID,
            "domain_id": UUID,
            "from_organisation_id": UUID,
            "to_organisation_id": UUID,
            "state": {"type": "string", "maxLength": 32},
            "generation": GENERATION,
            "created_at": TS,
            "updated_at": TS,
        },
        ["transfer_id", "domain_id", "from_organisation_id", "to_organisation_id", "state"],
        "Repo 1 Appendix A.43 domain_transfer_operations; §10.4",
        "approval_json — dual-approval evidence, released only through the audit surface.",
    ),
    "DomainTransferRequest": _obj(
        "Request a controlled tenant transfer. A raw organisation_id update is forbidden (Repo 1 §10.4).",
        {"to_organisation_id": UUID, "reason": {"type": "string", "maxLength": 512}},
        ["to_organisation_id"],
        "Repo 1 §10.4",
    ),

    # --- mailbox ----------------------------------------------------------
    "Mailbox": _obj(
        "Mailbox metadata, generations, restrictions and quota summary as authorized (C.26 notes).",
        {
            "mailbox_id": UUID,
            "organisation_id": UUID,
            "domain_id": UUID,
            "primary_address": {"type": "string", "format": "idn-email"},
            "display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "state": {"type": "string", "maxLength": 32},
            "quota_bytes": {"type": "integer", "minimum": 0},
            "desired_generation": GENERATION,
            "observed_generation": GENERATION,
            "recovery_expires_at": {"oneOf": [TS, {"type": "null"}]},
            "restrictions": {"type": "array", "items": {"$ref": "#/components/schemas/Restriction"}},
            "usage": {"$ref": "#/components/schemas/MailboxUsage"},
            "version": VERSION,
            "created_at": TS,
            "updated_at": TS,
        },
        ["mailbox_id", "organisation_id", "domain_id", "primary_address", "state", "quota_bytes", "desired_generation", "observed_generation", "version"],
        "Repo 1 Appendix A.13 mailboxes; §12",
        "primary_address_id — an internal registry key; the address itself is returned instead.",
    ),
    "MailboxCreateRequest": _obj(
        "Create a mailbox within entitlement.",
        {
            "domain_id": UUID,
            "local_part": {"type": "string", "maxLength": 64, "description": "Case-insensitive within the domain (Master §6.5). v1 defaults to ASCII local-parts."},
            "display_name": {"type": "string", "maxLength": 255},
            "quota_bytes": {"type": "integer", "minimum": 0},
        },
        ["domain_id", "local_part"],
        "Repo 1 §12.1; Master §6.5",
    ),
    "MailboxUpdate": _obj(
        "Change mailbox metadata. Pure display metadata does not increment the infra generation (Repo 1 §12.3).",
        {"display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]}},
        None,
        "Repo 1 Appendix A.13, §12.3",
    ),
    "MailboxQuotaUpdate": _obj(
        "Change the configured quota. Increments generation; enforcement is acknowledged asynchronously (C.28 notes).",
        {"quota_bytes": {"type": "integer", "minimum": 0}},
        ["quota_bytes"],
        "Repo 1 §16",
    ),
    "MailboxUsage": _obj(
        "Observed usage. May be stale rather than a synchronous backend query (C.33 notes).",
        {
            "bytes_used": {"type": "integer", "minimum": 0},
            "message_count": {"type": "integer", "minimum": 0},
            "quota_percent_bp": {"type": "integer", "minimum": 0, "description": "Basis points, so 10000 is 100%."},
            "observed_at": TS,
            "stale": {"type": "boolean", "description": "True when the figures predate the freshness policy."},
        },
        ["bytes_used", "message_count", "observed_at", "stale"],
        "Repo 1 Appendix A.15 mailbox_usage; §16.1",
    ),
    "MailboxAccessGrant": _obj(
        "Delegated access to a mailbox. Sensitive authorization metadata (C.34 notes).",
        {
            "grant_id": UUID,
            "grantee_subject": {"type": "string", "maxLength": 255},
            "scopes": {"type": "array", "items": {"type": "string", "enum": ["mail.read", "mail.write", "mail.send", "mail.settings"]}, "minItems": 1},
            "granted_by": {"type": "string", "maxLength": 255},
            "expires_at": {"oneOf": [TS, {"type": "null"}]},
            "revoked_at": {"oneOf": [TS, {"type": "null"}]},
        },
        ["grant_id", "grantee_subject", "scopes"],
        "Repo 1 Appendix A.17 mailbox_access_grants",
    ),
    "MailboxAccessGrantRequest": _obj(
        "Grant delegated mailbox access. Scopes are allow-listed and self-escalation is prohibited (C.35 notes).",
        {
            "grantee_subject": {"type": "string", "maxLength": 255},
            "scopes": {"type": "array", "items": {"type": "string", "enum": ["mail.read", "mail.write", "mail.send", "mail.settings"]}, "minItems": 1},
            "expires_at": TS,
        },
        ["grantee_subject", "scopes"],
        "Repo 1 §18, Appendix A.17",
    ),
    "Restriction": _obj(
        "An effective restriction. Reason detail is privacy filtered (C.96 notes).",
        {
            "restriction_id": UUID,
            "resource_type": {"type": "string", "enum": ["ORGANISATION", "DOMAIN", "MAILBOX"]},
            "resource_id": UUID,
            "restriction_code": {"type": "string", "enum": ["SEND_BLOCKED", "SEND_RATE_REDUCED", "AUTH_BLOCKED", "FORWARDING_BLOCKED", "ADMIN_CHANGES_FROZEN"]},
            "reason_code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$", "maxLength": 64},
            "source": {"type": "string", "maxLength": 64},
            "starts_at": TS,
            "expires_at": {"oneOf": [TS, {"type": "null"}]},
            "cleared_at": {"oneOf": [TS, {"type": "null"}]},
        },
        ["restriction_id", "resource_type", "resource_id", "restriction_code", "starts_at"],
        "Repo 1 Appendix A.30 restrictions; §36",
    ),

    # --- addressing -------------------------------------------------------
    "Alias": _obj(
        "Alias and its targets. Targets are shown according to permission and privacy policy (C.39 notes).",
        {
            "alias_id": UUID,
            "organisation_id": UUID,
            "domain_id": UUID,
            "address": {"type": "string", "format": "idn-email"},
            "state": {"type": "string", "maxLength": 32},
            "max_hops": {"type": "integer", "minimum": 1},
            "targets": {"type": "array", "items": {"$ref": "#/components/schemas/AliasTarget"}},
            "version": VERSION,
        },
        ["alias_id", "organisation_id", "domain_id", "address", "state", "targets", "version"],
        "Repo 1 Appendix A.20 aliases, A.21 alias_targets; §13.1",
    ),
    "AliasTarget": _obj(
        "One alias destination.",
        {
            "target_type": {"type": "string", "enum": ["MAILBOX", "ALIAS", "GROUP", "EXTERNAL"]},
            "target_ref": {"type": "string", "maxLength": 320},
            "position": {"type": "integer", "minimum": 0},
            "state": {"type": "string", "maxLength": 32},
        },
        ["target_type", "target_ref"],
        "Repo 1 Appendix A.21 alias_targets",
    ),
    "AliasWrite": _obj(
        "Create or replace an alias. Loop and expansion validation runs across the whole alias/group graph (C.38, C.40 notes).",
        {
            "local_part": {"type": "string", "maxLength": 64},
            "targets": {"type": "array", "items": {"$ref": "#/components/schemas/AliasTarget"}, "minItems": 1},
            "max_hops": {"type": "integer", "minimum": 1},
        },
        ["targets"],
        "Repo 1 §13.1",
    ),
    "MailboxIdentity": _obj(
        "A send-as identity bound to a mailbox.",
        {
            "identity_id": UUID,
            "mailbox_id": UUID,
            "address": {"type": "string", "format": "idn-email"},
            "display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "reply_to": {"oneOf": [{"type": "string", "format": "idn-email"}, {"type": "null"}]},
            "is_default": {"type": "boolean"},
            "state": {"type": "string", "maxLength": 32},
        },
        ["identity_id", "mailbox_id", "address", "is_default", "state"],
        "Repo 1 Appendix A.18 mailbox_identities; §13.2",
        "signature_ref — an internal storage pointer, not the signature body.",
    ),
    "MailboxIdentityCreate": _obj(
        "Create a send-as identity. Requires domain/address ownership and sender-authorization rules (C.43 notes).",
        {
            "address": {"type": "string", "format": "idn-email"},
            "display_name": {"type": "string", "maxLength": 255},
            "reply_to": {"type": "string", "format": "idn-email"},
            "is_default": {"type": "boolean"},
        },
        ["address"],
        "Repo 1 §13.2",
    ),
    "MailboxIdentityUpdate": _obj(
        "Change identity presentation. The underlying address cannot change; that needs a new identity (C.44 notes).",
        {
            "display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "reply_to": {"oneOf": [{"type": "string", "format": "idn-email"}, {"type": "null"}]},
            "is_default": {"type": "boolean"},
        },
        None,
        "Repo 1 Appendix A.18",
    ),
    "DistributionGroup": _obj(
        "Distribution group. Member visibility is permission-aware (C.48 notes).",
        {
            "group_id": UUID,
            "organisation_id": UUID,
            "domain_id": UUID,
            "address": {"type": "string", "format": "idn-email"},
            "display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "posting_policy": {"type": "string", "maxLength": 32},
            "max_expansion": {"type": "integer", "minimum": 1},
            "state": {"type": "string", "maxLength": 32},
            "version": VERSION,
        },
        ["group_id", "organisation_id", "domain_id", "address", "posting_policy", "state", "version"],
        "Repo 1 Appendix A.22 distribution_groups; §14",
    ),
    "DistributionGroupWrite": _obj(
        "Create or change a distribution group. Expansion limit and posting policy are validated (C.47 notes).",
        {
            "local_part": {"type": "string", "maxLength": 64},
            "display_name": {"type": "string", "maxLength": 255},
            "posting_policy": {"type": "string", "maxLength": 32},
            "max_expansion": {"type": "integer", "minimum": 1},
        },
        None,
        "Repo 1 §14",
    ),
    "GroupMember": _obj(
        "One distribution group member.",
        {
            "member_id": UUID,
            "member_type": {"type": "string", "enum": ["MAILBOX", "ALIAS", "GROUP", "EXTERNAL"]},
            "member_ref": {"type": "string", "maxLength": 320},
            "state": {"type": "string", "maxLength": 32},
            "created_at": TS,
        },
        ["member_id", "member_type", "member_ref", "state"],
        "Repo 1 Appendix A.23 distribution_group_members; §14.1",
    ),
    "GroupMemberCreate": _obj(
        "Add a member. Cycle detection runs for nested groups and external member policy is enforced (C.52 notes).",
        {
            "member_type": {"type": "string", "enum": ["MAILBOX", "ALIAS", "GROUP", "EXTERNAL"]},
            "member_ref": {"type": "string", "maxLength": 320},
        },
        ["member_type", "member_ref"],
        "Repo 1 §14.1",
    ),

    # --- mailbox settings -------------------------------------------------
    "ForwardingRule": _obj(
        "Mailbox forwarding configuration.",
        {
            "enabled": {"type": "boolean"},
            "keep_copy": {"type": "boolean"},
            "targets": {"type": "array", "items": {"$ref": "#/components/schemas/ForwardingTarget"}},
            "version": VERSION,
        },
        ["enabled", "keep_copy", "targets", "version"],
        "Repo 1 Appendix A.24 forwarding_rules; §15",
    ),
    "ForwardingTarget": _obj(
        "One forwarding destination and its verification state.",
        {
            "address": {"type": "string", "format": "idn-email"},
            "external": {"type": "boolean"},
            "verified": {"type": "boolean", "description": "An unverified external target does not receive mail (FORWARDING_TARGET_UNVERIFIED)."},
        },
        ["address", "external", "verified"],
        "Repo 1 Appendix A.24 verification_json; §15",
    ),
    "ForwardingRuleWrite": _obj(
        "Replace forwarding configuration. External forwarding may require verification and domain policy (C.55 notes).",
        {
            "enabled": {"type": "boolean"},
            "keep_copy": {"type": "boolean"},
            "targets": {"type": "array", "items": {"type": "string", "format": "idn-email"}, "maxItems": 16},
        },
        ["enabled", "keep_copy", "targets"],
        "Repo 1 §15",
    ),
    "VacationRule": _obj(
        "Vacation responder. Content is returned sanitized (C.56 notes).",
        {
            "enabled": {"type": "boolean"},
            "starts_at": {"oneOf": [TS, {"type": "null"}]},
            "ends_at": {"oneOf": [TS, {"type": "null"}]},
            "subject": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "body_text": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "body_html": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "reply_interval_seconds": {"type": "integer", "minimum": 0},
            "version": VERSION,
        },
        ["enabled", "reply_interval_seconds", "version"],
        "Repo 1 Appendix A.25 vacation_rules; §15.2",
    ),
    "VacationRuleWrite": _obj(
        "Replace the vacation responder. Date range, responder loop suppression and content size are validated (C.57 notes).",
        {
            "enabled": {"type": "boolean"},
            "starts_at": TS,
            "ends_at": TS,
            "subject": {"type": "string", "maxLength": 255},
            "body_text": {"type": "string"},
            "body_html": {"type": "string"},
            "reply_interval_seconds": {"type": "integer", "minimum": 0},
        },
        ["enabled"],
        "Repo 1 §15.2",
    ),
    "FilterSet": _obj(
        "Structured filters and their installation generation. Never an arbitrary backend script (C.58 notes).",
        {
            "rules": {"type": "array", "items": {"$ref": "#/components/schemas/FilterRule"}},
            "generation": GENERATION,
            "observed_generation": GENERATION,
            "state": {"type": "string", "maxLength": 32},
        },
        ["rules", "generation", "observed_generation", "state"],
        "Repo 1 Appendix A.26 sieve_filter_sets; §15.1",
        "compiled_hash — an internal integrity value over generated Sieve.",
    ),
    "FilterRule": _obj(
        "One structured filter rule. Structured primitives only; no raw Sieve.",
        {
            "name": {"type": "string", "maxLength": 128},
            "enabled": {"type": "boolean"},
            "conditions": {"type": "array", "items": {"type": "object"}, "minItems": 1},
            "actions": {"type": "array", "items": {"type": "object"}, "minItems": 1},
            "stop": {"type": "boolean"},
        },
        ["name", "enabled", "conditions", "actions"],
        "Repo 1 §15.1 structured filter v1 primitives",
    ),
    "FilterSetWrite": _obj(
        "Replace the filter set. Compiled deterministically to Sieve; installation is asynchronous (C.59 notes).",
        {"rules": {"type": "array", "items": {"$ref": "#/components/schemas/FilterRule"}}},
        ["rules"],
        "Repo 1 §15.1",
    ),
    "FilterValidationResult": _obj(
        "Validation outcome. This operation has no side effects (C.60 notes).",
        {
            "valid": {"type": "boolean"},
            "errors": {"type": "array", "items": {"$ref": "#/components/schemas/ValidationError"}},
        },
        ["valid", "errors"],
        "Repo 1 §15.1",
    ),

    # --- sessions and credentials ----------------------------------------
    "MailSession": _obj(
        "Privacy-safe session metadata (C.61 notes).",
        {
            "session_id": UUID,
            "device_label": {"oneOf": [{"type": "string", "maxLength": 128}, {"type": "null"}]},
            "last_seen_at": TS,
            "revoked_at": {"oneOf": [TS, {"type": "null"}]},
            "current": {"type": "boolean"},
        },
        ["session_id", "last_seen_at", "current"],
        "Repo 1 Appendix A.28 mail_sessions; Master §9.5",
        "ip_prefix_hash and oidc_session_id — correlation values that would re-identify a device or bridge to the IdP session.",
    ),
    "AppPassword": _obj(
        "App password metadata. The secret is never in this representation.",
        {
            "credential_id": UUID,
            "label": {"type": "string", "maxLength": 64},
            "scopes": {"type": "array", "items": {"type": "string"}},
            "last_used_at": {"oneOf": [TS, {"type": "null"}]},
            "expires_at": {"oneOf": [TS, {"type": "null"}]},
            "revoked_at": {"oneOf": [TS, {"type": "null"}]},
        },
        ["credential_id", "label", "scopes"],
        "Repo 1 Appendix A.27 app_passwords; §17.2",
        "secret_verifier — the stored verifier. §17.2 step 5 is explicit that no endpoint can recover an old secret.",
    ),
    "AppPasswordCreated": _obj(
        "The one and only response that carries the raw secret (Repo 1 §17.2 step 2, C.64 notes).",
        {
            "credential": {"$ref": "#/components/schemas/AppPassword"},
            "secret": {"type": "string", "description": "Raw secret, returned exactly once over TLS. At least 128 bits of CSPRNG entropy."},
        },
        ["credential", "secret"],
        "Repo 1 §17.2",
    ),
    "AppPasswordCreateRequest": _obj(
        "Create an app password. Requires strong re-authentication per policy (C.64 notes).",
        {
            "label": {"type": "string", "maxLength": 64},
            "scopes": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "expires_at": TS,
        },
        ["label"],
        "Repo 1 §17.2",
    ),

    # --- audit, security, exports ----------------------------------------
    "AuditEvent": _obj(
        "Tenant audit record. Never carries message content (C.92 notes).",
        {
            "audit_event_id": UUID,
            "occurred_at": TS,
            "actor_type": {"type": "string", "maxLength": 32},
            "actor_id": {"type": "string", "maxLength": 255},
            "action": {"type": "string", "maxLength": 128},
            "resource_type": {"type": "string", "maxLength": 32},
            "resource_id": {"oneOf": [UUID, {"type": "null"}]},
            "outcome": {"type": "string", "enum": ["success", "failure", "rejected", "timeout", "cancelled", "unknown"]},
            "request_id": {"oneOf": [{"type": "string", "maxLength": 128}, {"type": "null"}]},
            "trace_id": {"oneOf": [{"type": "string", "pattern": "^[0-9a-f]{32}$"}, {"type": "null"}]},
            "metadata": {"type": "object"},
        },
        ["audit_event_id", "occurred_at", "actor_type", "action", "outcome"],
        "Repo 1 Appendix A.39 audit_events; §37.1",
        "integrity_hash — the tamper-evidence chain value, verified server-side.",
    ),
    "SecurityEvent": _obj(
        "Tenant-visible security event. Platform-only fields are redacted (C.93 notes).",
        {
            "security_event_id": UUID,
            "occurred_at": TS,
            "event_code": {"type": "string", "maxLength": 64},
            "severity": {"type": "string", "enum": ["INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL"]},
            "status": {"type": "string", "maxLength": 32},
            "mailbox_id": {"oneOf": [UUID, {"type": "null"}]},
            "identity_subject": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "details": {"type": "object", "description": "Bounded, privacy-filtered detail."},
        },
        ["security_event_id", "occurred_at", "event_code", "severity", "status"],
        "Repo 1 Appendix A.40 security_events; §37.2",
        "source and ops_case_ref — platform-only fields (C.93).",
    ),
    "DataExportJob": _obj(
        "Asynchronous export job. The artifact is encrypted and expiring (C.94 notes).",
        {
            "export_id": UUID,
            "export_type": {"type": "string", "maxLength": 64},
            "state": {"type": "string", "maxLength": 32},
            "requested_by": {"type": "string", "maxLength": 255},
            "expires_at": {"oneOf": [TS, {"type": "null"}]},
            "download_url": {"oneOf": [{"type": "string", "format": "uri"}, {"type": "null"}], "description": "Signed and short-lived; issued only after authorization (C.95 notes)."},
            "created_at": TS,
        },
        ["export_id", "export_type", "state", "created_at"],
        "Repo 1 Appendix A.42 data_export_jobs; §38",
        "storage_ref — the internal object location behind the signed URL.",
    ),
    "DataExportRequest": _obj(
        "Request an export. Export-type authorization applies (C.94 notes).",
        {"export_type": {"type": "string", "maxLength": 64}},
        ["export_type"],
        "Repo 1 §38",
    ),

    # --- mailbox data plane ----------------------------------------------
    "Folder": _obj(
        "One mailbox folder.",
        {
            "folder_ref": {"type": "string", "description": "Opaque, integrity-protected locator. Never a raw filesystem path (Repo 1 §20.1)."},
            "display_name": {"type": "string", "maxLength": 255},
            "special_use": {"oneOf": [{"type": "string", "enum": ["INBOX", "SENT", "DRAFTS", "TRASH", "JUNK", "ARCHIVE"]}, {"type": "null"}]},
            "message_count": {"type": "integer", "minimum": 0},
            "unread_count": {"type": "integer", "minimum": 0},
            "counts_observed_at": TS,
            "rights": {"type": "array", "items": {"type": "string"}, "description": "Derived from the mailbox grant and backend capability; never trusted from the client (Repo 1 §20.1)."},
            "protected": {"type": "boolean", "description": "A special-use folder that cannot be renamed or deleted (FOLDER_PROTECTED)."},
        },
        ["folder_ref", "display_name", "special_use", "rights", "protected"],
        "Repo 1 §20.1 folder model",
    ),
    "FolderCreate": _obj(
        "Create a folder. Reserved and special-use names are protected (C.67 notes).",
        {"display_name": {"type": "string", "maxLength": 255}, "parent_folder_ref": {"type": "string"}},
        ["display_name"],
        "Repo 1 §20.1",
    ),
    "FolderUpdate": _obj(
        "Rename or move a folder. Protected folders cannot be renamed (C.68 notes).",
        {"display_name": {"type": "string", "maxLength": 255}, "parent_folder_ref": {"oneOf": [{"type": "string"}, {"type": "null"}]}},
        None,
        "Repo 1 §20.1",
    ),
    "MessageSummary": _obj(
        "List-view message metadata. Metadata only — no body (C.70 notes).",
        {
            "message_ref": {"type": "string", "description": "Opaque and integrity protected; binds mailbox, folder, backend locator and UIDVALIDITY-equivalent (Repo 1 §20.3)."},
            "thread_ref": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "from": {"$ref": "#/components/schemas/AddressDisplay"},
            "to": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "cc": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "subject": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "sent_at": {"oneOf": [TS, {"type": "null"}]},
            "internal_at": TS,
            "flags": {"type": "array", "items": {"type": "string"}},
            "size_bytes": {"type": "integer", "minimum": 0},
            "has_attachments": {"type": "boolean"},
            "snippet": {"oneOf": [{"type": "string", "maxLength": 512}, {"type": "null"}], "description": "Included only where safely available (Repo 1 §20.2)."},
        },
        ["message_ref", "from", "internal_at", "flags", "size_bytes", "has_attachments"],
        "Repo 1 §20.2 message summary",
    ),
    "MessageView": _obj(
        "Full message view: normalised envelope, parsed body structure and part descriptors. Raw MIME streams only from the raw endpoint (Repo 1 §20.2).",
        {
            "message_ref": {"type": "string"},
            "thread_ref": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "envelope": {"$ref": "#/components/schemas/MessageEnvelope"},
            "body_parts": {"type": "array", "items": {"$ref": "#/components/schemas/BodyPartDescriptor"}},
            "attachments": {"type": "array", "items": {"$ref": "#/components/schemas/AttachmentDescriptor"}},
            "flags": {"type": "array", "items": {"type": "string"}},
            "size_bytes": {"type": "integer", "minimum": 0},
        },
        ["message_ref", "envelope", "body_parts", "attachments", "flags", "size_bytes"],
        "Repo 1 §20.2",
    ),
    "MessageEnvelope": _obj(
        "Normalised message envelope.",
        {
            "from": {"$ref": "#/components/schemas/AddressDisplay"},
            "reply_to": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "to": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "cc": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "bcc": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "subject": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "sent_at": {"oneOf": [TS, {"type": "null"}]},
        },
        ["from", "to"],
        "Repo 1 §20.2",
    ),
    "AddressDisplay": _obj(
        "One display address.",
        {"address": {"type": "string", "format": "idn-email"}, "display_name": {"oneOf": [{"type": "string"}, {"type": "null"}]}},
        ["address"],
        "Repo 1 §20.2",
    ),
    "BodyPartDescriptor": _obj(
        "An allowed body-part descriptor.",
        {
            "part_ref": {"type": "string"},
            "media_type": {"type": "string"},
            "size_bytes": {"type": "integer", "minimum": 0},
            "charset": {"oneOf": [{"type": "string"}, {"type": "null"}]},
        },
        ["part_ref", "media_type", "size_bytes"],
        "Repo 1 §20.2",
    ),
    "AttachmentDescriptor": _obj(
        "An attachment descriptor. Bytes stream from the attachment endpoint.",
        {
            "part_ref": {"type": "string"},
            "filename_safe": {"type": "string", "description": "Sanitised filename (Repo 1 §25.1)."},
            "media_type": {"type": "string"},
            "size_bytes": {"type": "integer", "minimum": 0},
            "inline": {"type": "boolean"},
        },
        ["part_ref", "filename_safe", "media_type", "size_bytes", "inline"],
        "Repo 1 §25.1",
    ),
    "MessageContent": _obj(
        "Renderable message content after the sanitization and render policy has been applied (C.72 notes, Repo 2 Appendix Q).",
        {
            "message_ref": {"type": "string"},
            "content_type": {"type": "string", "enum": ["text/html", "text/plain"]},
            "content": {"type": "string"},
            "sanitizer_outcome": {"type": "string", "maxLength": 64},
            "blocked_remote_resources": {"type": "integer", "minimum": 0},
        },
        ["message_ref", "content_type", "content", "sanitizer_outcome"],
        "Repo 1 §20.2; karyalay-webmail Appendix Q",
    ),
    "MessageRefBatch": _obj(
        "A bounded batch of message references. Exceeding the limit is MESSAGE_BATCH_LIMIT (Repo 1 §24.1).",
        {"message_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1}},
        ["message_refs"],
        "Repo 1 §24, §24.1",
    ),
    "FlagMutationRequest": _obj(
        "Add or remove flags across a bounded batch. Flag semantics are idempotent (C.75 notes).",
        {
            "message_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "add_flags": {"type": "array", "items": {"type": "string"}},
            "remove_flags": {"type": "array", "items": {"type": "string"}},
        },
        ["message_refs"],
        "Repo 1 §24",
    ),
    "MessageTransferRequest": _obj(
        "Move or copy a bounded batch to a destination folder.",
        {
            "message_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "destination_folder_ref": {"type": "string"},
        },
        ["message_refs", "destination_folder_ref"],
        "Repo 1 §24",
    ),
    "ExpungeRequest": _obj(
        "Permanently remove messages. Never implicit on an ordinary delete; requires strong confirmation (C.79 notes).",
        {
            "message_refs": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "confirm": {"type": "boolean", "const": True},
        },
        ["message_refs", "confirm"],
        "Repo 1 §24",
    ),
    "BulkMutationResult": _obj(
        "Per-item outcome. Returned per item where partial backend semantics are unavoidable (C.76 notes) — a partial failure is never reported as overall success.",
        {
            "results": {
                "type": "array",
                "items": _obj(
                    "One item's outcome.",
                    {
                        "message_ref": {"type": "string"},
                        "outcome": {"type": "string", "enum": ["success", "failure"]},
                        "code": {"oneOf": [{"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"}, {"type": "null"}], "description": "A code from errors/error-catalog-v1.yaml when the item failed."},
                    },
                    ["message_ref", "outcome"],
                ),
            },
            "succeeded": {"type": "integer", "minimum": 0},
            "failed": {"type": "integer", "minimum": 0},
        },
        ["results", "succeeded", "failed"],
        "Repo 1 §24, §24.1",
    ),
    "Thread": _obj(
        "A thread projection. Thread identity is an application projection, not an authoritative mail storage key (C.80 notes).",
        {
            "thread_ref": {"type": "string"},
            "messages": {"type": "array", "items": {"$ref": "#/components/schemas/MessageSummary"}},
        },
        ["thread_ref", "messages"],
        "Repo 1 §21.1",
    ),
    "ThreadSummary": _obj(
        "One thread in a folder or search scope. The list form of the C.80 projection, so a client never re-threads message pages itself (D-01, ADR-KEM-010).",
        {
            "thread_ref": {"type": "string", "description": "Opaque thread reference; the same application projection C.80 returns, not an authoritative mail storage key."},
            "subject": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "participants": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/AddressDisplay"},
                "maxItems": 32,
                "description": "Distinct participants, most recent first, hard bounded. An unbounded list on a long thread is payload amplification the sender controls by replying.",
            },
            "message_count": {"type": "integer", "minimum": 1},
            "unread_count": {"type": "integer", "minimum": 0},
            "has_attachments": {"type": "boolean"},
            "latest": {"$ref": "#/components/schemas/MessageSummary"},
        },
        ["thread_ref", "message_count", "unread_count", "has_attachments", "latest"],
        "Repo 1 §21.1; delta D-01 accepted by ADR-KEM-010",
    ),
    "Contact": _obj(
        "A personal contact. Private to the mailbox principal, not shared across the organisation (D-04, ADR-KEM-010).",
        {
            "contact_id": UUID,
            "display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "addresses": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/AddressDisplay"},
                "minItems": 1,
                "maxItems": 16,
                "description": "Normalized addresses, hard bounded.",
            },
            "organisation": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}], "description": "Free-text employer or organisation label. Unrelated to the tenant organisation_id."},
            "notes": {"oneOf": [{"type": "string", "maxLength": 2048}, {"type": "null"}]},
            "version": VERSION,
            "created_at": TS,
            "updated_at": TS,
        },
        ["contact_id", "addresses", "version", "created_at", "updated_at"],
        "delta D-04 accepted by ADR-KEM-010",
    ),
    "ContactWrite": _obj(
        "Create or update a personal contact. The server normalizes addresses; the client does not choose contact_id or version.",
        {
            "display_name": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "addresses": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/AddressDisplay"},
                "minItems": 1,
                "maxItems": 16,
            },
            "organisation": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "notes": {"oneOf": [{"type": "string", "maxLength": 2048}, {"type": "null"}]},
        },
        ["addresses"],
        "delta D-04 accepted by ADR-KEM-010",
    ),
    "DirectoryEntry": _obj(
        "One addressable member of the caller's organisation. Deliberately narrower than Member: an autocomplete needs a name and an address, and every field not returned is a field that cannot leak (D-05, ADR-KEM-010).",
        {
            "member_id": UUID,
            "display_name": {"type": "string", "maxLength": 255},
            "primary_address": {"type": "string", "format": "idn-email"},
            "role": {"oneOf": [{"type": "string", "maxLength": 64}, {"type": "null"}]},
        },
        ["member_id", "display_name", "primary_address"],
        "Repo 1 Appendix A.2 organisation_memberships; delta D-05 accepted by ADR-KEM-010",
        "entitlements, membership dates and role history -- a directory autocomplete has no use for them and they widen the blast radius of an enumeration",
    ),
    "SearchResult": _obj(
        "Search results. The query is parsed to a typed AST; raw backend syntax is never interpolated (C.81 notes).",
        {
            "messages": {"type": "array", "items": {"$ref": "#/components/schemas/MessageSummary"}},
            "next_cursor": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "truncated": {"type": "boolean", "description": "True when a result or time limit stopped the search short."},
        },
        ["messages", "next_cursor", "truncated"],
        "Repo 1 §21.2",
    ),
    "Draft": _obj(
        "A draft. Drafts live in the backend Drafts folder (C.82 notes).",
        {
            "draft_ref": {"type": "string", "description": "Opaque draft reference."},
            "envelope": {"$ref": "#/components/schemas/MessageEnvelope"},
            "body_text": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "body_html": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "attachments": {"type": "array", "items": {"$ref": "#/components/schemas/AttachmentDescriptor"}},
            "identity_id": {"oneOf": [UUID, {"type": "null"}]},
            "updated_at": TS,
        },
        ["draft_ref", "envelope", "updated_at"],
        "Repo 1 §22",
    ),
    "DraftWrite": _obj(
        "Structured compose payload. The server builds standards-compliant MIME from it (C.83 notes); the client never supplies raw MIME.",
        {
            "identity_id": UUID,
            "to": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "cc": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "bcc": {"type": "array", "items": {"$ref": "#/components/schemas/AddressDisplay"}},
            "subject": {"type": "string"},
            "body_text": {"type": "string"},
            "body_html": {"type": "string"},
            "staged_attachment_ids": {"type": "array", "items": UUID},
            "in_reply_to_message_ref": {"type": "string"},
        },
        None,
        "Repo 1 §22.2 compose payload",
    ),
    "StagedAttachment": _obj(
        "A staged compose attachment. Owner- and mailbox-bound; never a public URL (C.88 notes).",
        {
            "attachment_id": UUID,
            "filename_safe": {"type": "string"},
            "media_type": {"type": "string"},
            "size_bytes": {"type": "integer", "minimum": 0},
            "content_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "scan_state": {"type": "string", "enum": ["PENDING", "CLEAN", "BLOCKED", "ERROR"]},
            "expires_at": TS,
        },
        ["attachment_id", "filename_safe", "media_type", "size_bytes", "scan_state", "expires_at"],
        "Repo 1 Appendix A.35 staged_attachments; §25.2",
        "storage_ref — the internal object location.",
    ),
    "SendRequest": _obj(
        "Final send. Idempotency-Key is mandatory (C.90 notes).",
        {
            "draft_ref": {"type": "string", "description": "Send an existing draft, or supply the structured payload instead."},
            "message": {"$ref": "#/components/schemas/DraftWrite"},
        },
        None,
        "Repo 1 §23.1",
    ),
    "SubmissionRecord": _obj(
        "The Karyalay submission boundary outcome. It does NOT claim remote delivery (C.91 notes).",
        {
            "submission_id": UUID,
            "state": {"type": "string", "enum": ["PENDING", "ACCEPTED", "REJECTED", "STATUS_UNKNOWN"]},
            "smtp_queue_id": {"oneOf": [{"type": "string", "maxLength": 64}, {"type": "null"}]},
            "accepted_at": {"oneOf": [TS, {"type": "null"}]},
            "sent_copy_state": {"type": "string", "maxLength": 32},
            "last_error_code": {"oneOf": [{"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"}, {"type": "null"}]},
        },
        ["submission_id", "state", "sent_copy_state"],
        "Repo 1 Appendix A.34 send_submission_records; §23.1, §33.6",
        "idempotency_key and message_fingerprint — replay-detection inputs, not client-readable state.",
    ),

    # --- internal ---------------------------------------------------------
    "ResourceDependency": _obj(
        "A prerequisite this resource must not be exposed ahead of. Repo 3 §49: dependency generations \"prevent exposing a mailbox before domain/routing/key prerequisites have converged\".",
        {
            "resource_type": {"$ref": "#/components/schemas/DesiredStateResourceType"},
            "resource_id": UUID,
            "min_generation": GENERATION,
        },
        ["resource_type", "resource_id", "min_generation"],
        "Repo 3 §49 / Appendix O.1 dependencies[]; adopted by ADR-KEM-008 decision 4",
    ),
    "DesiredStateResourceType": {
        "type": "string",
        "description": (
            "Resource kinds carried by this exchange. Repo 3 Appendix O.1 spells the eight it "
            "materializes; Repo 1 Appendix A.31 spells seven it dispatches. ADR-KEM-008 Amendment 1 "
            "unifies them on Repo 3's spelling where the two name the same concept (dkim_key, "
            "filter_set) and keeps the two Repo 1 kinds Repo 3 has no materialization row for."
        ),
        "enum": [
            "organisation",
            "domain",
            "mailbox",
            "alias",
            "group",
            "quota",
            "filter_set",
            "restriction",
            "dkim_key",
            "placement",
        ],
        "$comment": (
            "Source: Repo 3 Appendix O.1 resource_type union Repo 1 Appendix A.31 resource_type. "
            "organisation and placement are Repo 1-only and carry no Repo 3 Appendix O.1 "
            "materialization row — see ADR-KEM-008 Amendment 1 open item 1."
        ),
    },
    "DesiredState": _obj(
        "The desired-state document Infra reconciles toward. The control plane may not send arbitrary config fragments or shell commands (Repo 1 §12.2). Unified shape per ADR-KEM-008.",
        {
            "schema_version": {
                "type": "integer",
                "minimum": 1,
                "description": "Envelope version. Repo 3 §49: an unknown schema version is nonretryable until code upgrade, and the controller MUST NOT guess.",
            },
            "resource_type": {"$ref": "#/components/schemas/DesiredStateResourceType"},
            "resource_id": UUID,
            "organisation_id": UUID,
            "desired_generation": GENERATION,
            "desired_status": {
                "type": "string",
                "pattern": "^[A-Z][A-Z0-9_]*$",
                "maxLength": 40,
                "description": (
                    "Target lifecycle state for this resource. The vocabulary is per resource type and "
                    "is Repo 1's Appendix A lifecycle column for that resource (for example A.14 mailboxes "
                    "REQUESTED/CONFIGURING/ACTIVE/RESTRICTED/SUSPENDED/PROVISIONING_FAILED/DELETION_PENDING/"
                    "RECOVERY_WINDOW/DELETED). Neither Repo 3 Appendix O.1 nor Appendix Q fixes a single "
                    "cross-type enum — Appendix Q says \"ACTIVE/RESTRICTED/DELETING etc mapped from desired "
                    "state\" — so this is constrained by grammar, not enumerated. See ADR-KEM-008 "
                    "Amendment 1 open item 2."
                ),
            },
            "dependencies": {
                "type": "array",
                "maxItems": 32,
                "items": {"$ref": "#/components/schemas/ResourceDependency"},
                "description": "Prerequisites that must have converged to at least min_generation before this resource is exposed (Repo 3 §49).",
            },
            "spec": {"$ref": "#/components/schemas/DesiredStateSpec"},
            "correlation": _obj(
                "Correlation for the reconciliation attempt. Master §30 requires the correlation to survive this hop; Repo 3 §49 omits it, and ADR-KEM-008 decision 6 keeps Repo 1's.",
                {"operation_id": UUID, "trace_id": {"type": "string", "pattern": "^[0-9a-f]{32}$"}},
                ["operation_id"],
            ),
        },
        ["schema_version", "resource_type", "resource_id", "organisation_id", "desired_generation", "desired_status", "spec", "correlation"],
        "Repo 1 §12.2 unified with Repo 3 §49 / Appendix O.1 per ADR-KEM-008",
    ),
    "DesiredStateSpec": _obj(
        "Typed resource fields, nested per Repo 3 Appendix O.1 (ADR-KEM-008 decision 5). Type-specific identity keys live here; the envelope carries only the uniform resource_id. Fields present depend on resource_type; Repo 3 Appendix O.1 tabulates the minimum set each kind requires.",
        {
            "domain_id": {"oneOf": [UUID, {"type": "null"}], "description": "Parent domain. Repo 3 Appendix O.1 requires it in the mailbox, alias and group spec."},
            "mailbox_id": {"oneOf": [UUID, {"type": "null"}], "description": "Repo 1 §12.2's type-specific key, relocated here by ADR-KEM-008 decision 2."},
            "storage_key": {
                "oneOf": [{"type": "string", "pattern": "^[A-Za-z0-9._-]+$", "maxLength": 128}, {"type": "null"}],
                "description": "Opaque. Repo 3 Appendix O.2: cannot contain '/', '..', NUL or shell metacharacter semantics.",
            },
            "primary_address": {"oneOf": [{"type": "string", "format": "idn-email"}, {"type": "null"}]},
            "quota_bytes": {"oneOf": [{"type": "integer", "minimum": 0}, {"type": "null"}], "description": "Nonnegative and bounded by infrastructure maximum (Repo 3 Appendix O.2)."},
            "auth_state": {"type": "string", "enum": ["enabled", "disabled"]},
            "receive_state": {"type": "string", "enum": ["enabled", "disabled"]},
            "send_state": {"type": "string", "enum": ["enabled", "disabled"]},
            "filter_generation": {"oneOf": [GENERATION, {"type": "null"}]},
        },
        None,
        "Repo 1 §12.2 typed fields, nested per Repo 3 Appendix O.1",
    ),
    "ObservationReport": _obj(
        "An observation of real infrastructure state, reported by a service identity. Unified shape per ADR-KEM-008.",
        {
            "schema_version": {"type": "integer", "minimum": 1, "description": "Envelope version (Repo 3 Appendix P.1)."},
            "desired_generation": GENERATION,
            "observed_generation": GENERATION,
            "readiness": {
                "type": "string",
                "enum": ["PENDING", "READY", "DEGRADED", "FAILED", "RESTRICTED", "DELETING", "ABSENT"],
                "description": (
                    "Repo 3 §50's six readiness values plus Repo 1 Appendix A.32's ABSENT (ADR-KEM-008 "
                    "decision 7). ABSENT means observed to not exist and is not a synonym for PENDING: a "
                    "resource never created and one mid-convergence require different operator responses."
                ),
            },
            "checksum": {
                "oneOf": [{"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}, {"type": "null"}],
                "description": "Checksum of the active generated state. Repo 3 §50 names checksum difference as one of its two drift triggers; Repo 1 Appendix A.32 had no column for it (ADR-KEM-008 decision 8).",
            },
            "details": {"type": "object", "description": "Safe bounded diagnostics. No raw daemon configuration or secrets (Repo 1 §29.2). Carries Repo 3 Appendix P.1 component statuses."},
            "source_service": {"type": "string", "maxLength": 64, "description": "Observer. Carries Repo 3 Appendix P.1 controller_instance."},
            "observed_at": TS,
        },
        ["schema_version", "desired_generation", "observed_generation", "readiness", "source_service", "observed_at"],
        "Repo 1 Appendix A.32 / §29.1-§29.3 unified with Repo 3 §50 / Appendix P.1 per ADR-KEM-008",
    ),
    "ObservationAccepted": _obj(
        "Acknowledgement of an observation, including whether it superseded the stored one.",
        {
            "accepted": {"type": "boolean"},
            "stored_generation": GENERATION,
            "note": {"type": "string", "description": "Why a stale or observed-ahead report was not stored. §29.3 treats observed-ahead as a security/consistency alert, never a silent accept."},
        },
        ["accepted", "stored_generation"],
        "Repo 1 §29.3",
    ),
    "ProvisioningOperation": _obj(
        "A typed provisioning operation and its lifecycle state.",
        {
            "operation_id": UUID,
            "organisation_id": UUID,
            "resource_type": {"type": "string", "enum": ["DOMAIN", "MAILBOX", "DKIM", "FILTER", "QUOTA", "PLACEMENT"]},
            "resource_id": UUID,
            "operation_type": {"type": "string", "maxLength": 48},
            "generation": GENERATION,
            "state": {"type": "string", "enum": ["REQUESTED", "DISPATCH_PENDING", "IN_PROGRESS", "SUCCEEDED", "RETRYABLE_FAILURE", "FAILED_ACTION_REQUIRED", "CANCELLED"]},
            "attempt_count": {"type": "integer", "minimum": 0},
            "next_attempt_at": {"oneOf": [TS, {"type": "null"}]},
            "last_error_code": {"oneOf": [{"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"}, {"type": "null"}]},
        },
        ["operation_id", "organisation_id", "resource_type", "resource_id", "operation_type", "generation", "state"],
        "Repo 1 Appendix A.31 provisioning_operations; §33.5",
        "idempotency_key — a replay-detection input, echoed to nobody.",
    ),
    "ProvisioningStarted": _obj(
        "Report that an operation has begun. The transition is idempotent (C.99 notes).",
        {"generation": GENERATION, "started_at": TS, "source_service": {"type": "string", "maxLength": 64}},
        ["generation", "started_at", "source_service"],
        "Repo 1 §29",
    ),
    "ProvisioningResult": _obj(
        "Report a terminal operation outcome. Generation and idempotency validation are mandatory (C.100 notes).",
        {
            "generation": GENERATION,
            "outcome": {"type": "string", "enum": ["SUCCEEDED", "RETRYABLE_FAILURE", "FAILED_ACTION_REQUIRED"]},
            "error_code": {"oneOf": [{"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"}, {"type": "null"}]},
            "details": {"type": "object", "description": "Safe bounded diagnostics only (Repo 1 §29.2)."},
            "finished_at": TS,
            "source_service": {"type": "string", "maxLength": 64},
        },
        ["generation", "outcome", "finished_at", "source_service"],
        "Repo 1 §29.2, §29.3",
    ),
    "RestrictionRequest": _obj(
        "Request a typed restriction. Repo 4 requests; Repo 1 decides and applies (OPS-BND-001).",
        {
            "resource_type": {"type": "string", "enum": ["ORGANISATION", "DOMAIN", "MAILBOX"]},
            "resource_id": UUID,
            "restriction_code": {"type": "string", "enum": ["SEND_BLOCKED", "SEND_RATE_REDUCED", "AUTH_BLOCKED", "FORWARDING_BLOCKED", "ADMIN_CHANGES_FROZEN"]},
            "reason_code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$", "maxLength": 64},
            "case_ref": {"type": "string", "maxLength": 128, "description": "Evidence or case reference. Required (C.101 notes)."},
            "expires_at": TS,
        },
        ["resource_type", "resource_id", "restriction_code", "reason_code", "case_ref"],
        "Repo 1 §30; karyalay-mail-ops Appendix AI delta AI-01",
    ),
    "ResourceDiagnostics": _obj(
        "Bounded operational diagnostics. No message body, attachment or secret (C.103 notes).",
        {
            "resource_type": {"type": "string", "maxLength": 32},
            "resource_id": UUID,
            "state": {"type": "string", "maxLength": 32},
            "desired_generation": GENERATION,
            "observed_generation": GENERATION,
            "observation_status": {"type": "string", "enum": ["READY", "DEGRADED", "FAILED", "ABSENT"]},
            "open_operations": {"type": "array", "items": {"$ref": "#/components/schemas/ProvisioningOperation"}},
            "recent_error_codes": {"type": "array", "items": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"}},
            "correlation": _obj(
                "Correlation identifiers for the operator's next hop.",
                {"trace_id": {"type": "string", "pattern": "^[0-9a-f]{32}$"}, "request_id": {"type": "string", "maxLength": 128}},
            ),
        },
        ["resource_type", "resource_id", "state", "desired_generation", "observed_generation", "observation_status"],
        "Repo 1 §30",
    ),
    "SecurityEventSubmission": _obj(
        "A normalised security signal from Ops. A deduplication key is required and the privacy schema is enforced (C.104 notes).",
        {
            "dedupe_key": {"type": "string", "maxLength": 128},
            "event_code": {"type": "string", "maxLength": 64},
            "severity": {"type": "string", "enum": ["INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL"]},
            "organisation_id": {"oneOf": [UUID, {"type": "null"}]},
            "mailbox_id": {"oneOf": [UUID, {"type": "null"}]},
            "identity_subject": {"oneOf": [{"type": "string", "maxLength": 255}, {"type": "null"}]},
            "occurred_at": TS,
            "details": {"type": "object", "description": "Bounded detail. No message content or secrets."},
            "ops_case_ref": {"type": "string", "maxLength": 128},
        },
        ["dedupe_key", "event_code", "severity", "occurred_at"],
        "Repo 1 §30, §37.2; karyalay-mail-ops §11",
    ),
    "HealthStatus": _obj(
        "Liveness or readiness. Not exposed to the public internet (C.105 notes).",
        {
            "status": {"type": "string", "enum": ["ok", "degraded", "unavailable"]},
            "checks": {
                "type": "array",
                "items": _obj(
                    "One dependency check.",
                    {"name": {"type": "string"}, "status": {"type": "string", "enum": ["ok", "degraded", "unavailable"]}, "duration_ms": {"type": "number", "minimum": 0}},
                    ["name", "status"],
                ),
                "description": "Present on readiness only. Safe diagnostics under a short bounded timeout (C.106 notes).",
            },
        },
        ["status"],
        "Repo 1 §50",
    ),
    "VersionInfo": _obj(
        "Build identity. No secrets or configuration dump (C.107 notes).",
        {
            "service": {"type": "string"},
            "version": {"type": "string"},
            "commit": {"type": "string"},
            "built_at": TS,
            "contract_version": {"type": "string", "description": "The karyalay-mail-contracts tag this build validates against."},
        },
        ["service", "version", "contract_version"],
        "Repo 1 §50, §44",
    ),
    "ReasonRequest": _obj(
        "Reason for an administrative state change. Mandatory where the card says so (C.16, C.29).",
        {"reason_code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$", "maxLength": 64}, "detail": {"type": "string", "maxLength": 512}},
        ["reason_code"],
        "Repo 1 Appendix A.30 restrictions.reason_code; C.16/C.29 notes",
    ),
    "SecurityEventAccepted": _obj(
        "Acknowledgement of a submitted security signal, including whether the deduplication key collapsed it into an existing event.",
        {"security_event_id": UUID, "deduplicated": {"type": "boolean"}, "restriction_workflow_started": {"type": "boolean"}},
        ["security_event_id", "deduplicated"],
        "Repo 1 §30",
    ),
    "ValidationError": _obj(
        "One structured, bounded validation error (Repo 1 §26.1 `errors[]`).",
        {
            "field": {"type": "string", "description": "JSON Pointer to the offending member."},
            "code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
            "detail": {"type": "string", "maxLength": 512},
        },
        ["field", "code"],
        "Repo 1 §26.1",
    ),
}
