#!/usr/bin/env python3
"""T00.04 + T00.05 — author the four OpenAPI documents Master §0.3 names.

  openapi/public-control-api-v1.yaml        C.1-C.65, C.92-C.96   (70 operations)
  openapi/mailbox-api-v1.yaml               C.66-C.91             (26 operations)
  openapi/internal-provisioning-api-v1.yaml C.97-C.100, C.105-107 (7 operations)
  openapi/operations-api-v1.yaml            C.101-C.104           (4 operations)

Operations, methods, paths, purposes, permissions and per-endpoint notes are
transcribed from karyalay-mail repository-spec-v1.0 Appendix C. Conventions come
from its §26 and Master §20. Error responses are generated FROM
errors/error-catalog-v1.yaml, which is what makes "zero inline-invented error
codes" structural rather than a review promise.

Each document is self-contained: Master §0.3 names four files and no shared
components file, and a self-contained document is what every code generator
handles without a resolver step. The shared components are emitted from one
source here, so they cannot drift between documents.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import specmd
from openapi_schemas import SCHEMAS
from openapi_ops import OPS, QUERY, PUBLIC, MAILBOX, PROVISIONING, OPERATIONS

from version import CONTRACT_VERSION  # the one source; see version.py

DOCUMENTS = {
    PUBLIC: {
        "file": "openapi/public-control-api-v1.yaml",
        "title": "Karyalay Mail — public control API",
        "summary": "Customer administration: organisation, entitlements, members, domains, DNS, DKIM, transfers, mailboxes, aliases, identities, groups, mailbox settings, sessions, credentials, audit, security, exports and restrictions.",
        "spec": "karyalay-mail repository-spec-v1.0 §26-§27, Appendix C.1-C.65 and C.92-C.96",
        "audience": "Browser and API clients acting for a customer principal.",
        "server": "https://api.mail.karyalay.in",
        "internal": False,
    },
    MAILBOX: {
        "file": "openapi/mailbox-api-v1.yaml",
        "title": "Karyalay Mail — mailbox-user API",
        "summary": "The mailbox data plane served through MailboxBackend and SubmissionGateway: folders, messages, threads, search, drafts, compose attachments and send.",
        "spec": "karyalay-mail repository-spec-v1.0 §28, Appendix C.66-C.91",
        "audience": "Browser and mobile clients acting for a mailbox principal. Browser clients never receive Dovecot credentials and never connect directly to IMAP or Doveadm (Repo 1 §28).",
        "server": "https://api.mail.karyalay.in",
        "internal": False,
    },
    PROVISIONING: {
        "file": "openapi/internal-provisioning-api-v1.yaml",
        "title": "Karyalay Mail — internal provisioning API",
        "summary": "The desired-state and observation exchange with karyalay-mail-infra, plus service liveness, readiness and version.",
        "spec": "karyalay-mail repository-spec-v1.0 §29, Appendix C.97-C.100 and C.105-C.107; karyalay-mail-infra §48-§51",
        "audience": "karyalay-mail-infra service identities. Not a public route; a user access token with the wrong audience or client is rejected (Repo 1 §29.2).",
        "server": "https://internal.mail.karyalay.in",
        "internal": True,
    },
    OPERATIONS: {
        "file": "openapi/operations-api-v1.yaml",
        "title": "Karyalay Mail — operations API",
        "summary": "The typed restriction, diagnostics and security-signal surface karyalay-mail-ops calls. Ops requests; karyalay-mail decides and applies.",
        "spec": "karyalay-mail repository-spec-v1.0 §30, Appendix C.101-C.104; karyalay-mail-ops Appendix AI",
        "audience": "karyalay-mail-ops service identities. Not a public route (Repo 1 §29.2).",
        "server": "https://internal.mail.karyalay.in",
        "internal": True,
    },
}

TAG_DESCRIPTIONS = {
    "Organisation": "Organisation mail profile and activation state (Repo 1 §8).",
    "Entitlements": "Plan limits and feature availability. The commercial system remains source of truth (Repo 1 §9).",
    "Members": "Mail-related organisation membership and role assignment (Repo 1 §8, §18).",
    "Directory": "Bounded organisation directory search for addressable members (D-05, ADR-KEM-010).",
    "Domains": "Hosted domain lifecycle, DNS readiness and DKIM (Repo 1 §10, §11).",
    "Domain transfers": "Controlled cross-organisation domain transfer under dual authorization (Repo 1 §10.4).",
    "Mailboxes": "Mailbox lifecycle, quota, usage and recovery (Repo 1 §12, §16).",
    "Access grants": "Delegated mailbox access (Repo 1 §18, Appendix A.17).",
    "Aliases": "Alias graph and its loop/expansion invariants (Repo 1 §13).",
    "Identities": "Send-as identities bound to a mailbox (Repo 1 §13.2).",
    "Groups": "Distribution groups and their expansion invariants (Repo 1 §14).",
    "Mailbox settings": "Forwarding, vacation and structured filters (Repo 1 §15).",
    "Sessions": "Mail session visibility and revocation (Repo 1 §17.1, Master §9.5).",
    "Credentials": "App passwords (Repo 1 §17.2).",
    "Restrictions": "Effective restrictions on a resource (Repo 1 §36).",
    "Audit": "Tenant audit trail (Repo 1 §37.1).",
    "Security": "Tenant-visible security events (Repo 1 §37.2).",
    "Exports": "Asynchronous data export jobs (Repo 1 §38).",
    "Folders": "Mailbox folders, backed by MailboxBackend (Repo 1 §20.1).",
    "Contacts": "Personal contacts, private to the mailbox principal (D-04, ADR-KEM-010).",
    "Messages": "Message retrieval, mutation and threading (Repo 1 §20, §21.1, §24).",
    "Search": "Typed-AST mailbox search (Repo 1 §21.2).",
    "Drafts": "Draft lifecycle with ETag concurrency (Repo 1 §22).",
    "Compose": "Staged compose attachments (Repo 1 §25.2).",
    "Send": "Final SMTP submission and its accepted boundary (Repo 1 §23).",
    "Desired state": "Desired-state exchange and observation reporting with Infra (Repo 1 §29).",
    "Provisioning operations": "Typed provisioning operation lifecycle (Repo 1 §29, §33.5).",
    "Diagnostics": "Bounded operational diagnostics for Ops (Repo 1 §30).",
    "Security signals": "Normalised security signals submitted by Ops (Repo 1 §30, §37.2).",
    "Service": "Liveness, readiness and build identity (Repo 1 §50).",
}

TAG_BY_PREFIX = [
    ("/api/v1/organisations/{org}/mail", "Organisation"),
    ("/api/v1/organisations/{org}/entitlements", "Entitlements"),
    ("/api/v1/organisations/{org}/members", "Members"),
    ("/api/v1/organisations/{org}/directory", "Directory"),
    ("/api/v1/organisations/{org}/domains", "Domains"),
    ("/api/v1/organisations/{org}/mailboxes", "Mailboxes"),
    ("/api/v1/organisations/{org}/audit-events", "Audit"),
    ("/api/v1/organisations/{org}/security-events", "Security"),
    ("/api/v1/organisations/{org}/exports", "Exports"),
    ("/api/v1/exports", "Exports"),
    ("/api/v1/domain-transfers", "Domain transfers"),
    ("/api/v1/domains/{domain}/aliases", "Aliases"),
    ("/api/v1/domains/{domain}/groups", "Groups"),
    ("/api/v1/domains", "Domains"),
    ("/api/v1/aliases", "Aliases"),
    ("/api/v1/groups", "Groups"),
    ("/api/v1/mailbox-identities", "Identities"),
    ("/api/v1/me/mail-sessions", "Sessions"),
    ("/api/v1/me/session", "Sessions"),
    ("/api/v1/mailboxes/{mailbox}/identities", "Identities"),
    ("/api/v1/mailboxes/{mailbox}/access-grants", "Access grants"),
    ("/api/v1/mailboxes/{mailbox}/app-passwords", "Credentials"),
    ("/api/v1/mailboxes/{mailbox}/forwarding", "Mailbox settings"),
    ("/api/v1/mailboxes/{mailbox}/vacation", "Mailbox settings"),
    ("/api/v1/mailboxes/{mailbox}/filters", "Mailbox settings"),
    ("/api/v1/mailboxes/{mailbox}/restrictions", "Restrictions"),
    ("/api/v1/mailboxes/{mailbox}/usage", "Mailboxes"),
    ("/api/v1/mailboxes/{mailbox}/folders", "Folders"),
    ("/api/v1/mailboxes/{mailbox}/contacts", "Contacts"),
    ("/api/v1/mailboxes/{mailbox}/messages", "Messages"),
    ("/api/v1/mailboxes/{mailbox}/threads", "Messages"),
    ("/api/v1/mailboxes/{mailbox}/search", "Search"),
    ("/api/v1/mailboxes/{mailbox}/drafts", "Drafts"),
    ("/api/v1/mailboxes/{mailbox}/compose", "Compose"),
    ("/api/v1/mailboxes/{mailbox}/send", "Send"),
    ("/api/v1/mailboxes/{mailbox}/submissions", "Send"),
    ("/api/v1/mailboxes", "Mailboxes"),
    ("/internal/v1/resources", "Desired state"),
    ("/internal/v1/provisioning", "Provisioning operations"),
    ("/internal/v1/ops/restrictions", "Restrictions"),
    ("/internal/v1/ops/resources", "Diagnostics"),
    ("/internal/v1/ops/security-events", "Security signals"),
    ("/internal/v1/health", "Service"),
    ("/internal/v1/version", "Service"),
]

PARAM_DESCRIPTIONS = {
    "org": "Organisation identifier (Master §6.3 `organisation_id`).",
    "domain": "Hosted domain identifier (Master §6.3 `domain_id`).",
    "mailbox": "Mailbox identifier (Master §6.3 `mailbox_id`).",
    "subject": "OIDC subject of the member.",
    "transfer": "Domain transfer operation identifier.",
    "grant": "Mailbox access grant identifier.",
    "alias": "Alias identifier.",
    "identity": "Mailbox identity identifier.",
    "group": "Distribution group identifier.",
    "member": "Distribution group member identifier.",
    "session": "Mail session identifier.",
    "credential": "App password identifier.",
    "folder": "Opaque folder reference (Repo 1 §20.1).",
    "message": "Opaque, integrity-protected message reference (Repo 1 §20.3).",
    "part": "MIME part token within the message.",
    "thread": "Opaque thread reference.",
    "draft": "Opaque draft reference.",
    "attachment": "Staged compose attachment identifier.",
    "submission": "Send submission identifier.",
    "export": "Data export job identifier.",
    "operation": "Provisioning operation identifier.",
    "restriction": "Restriction identifier.",
    "contact": "Personal contact identifier (C.109 notes: private to the mailbox principal).",
    "type": "Resource type (Repo 1 Appendix A.31 `resource_type`).",
    "id": "Resource identifier.",
}

OPAQUE_PARAMS = {"folder", "message", "part", "thread", "draft"}


def load_error_catalog():
    """Read the codes back out of the generated YAML.

    Parsing our own emitted subset keeps the OpenAPI documents downstream of the
    error catalog rather than of a second copy of Appendix E.
    """
    path = os.path.join(specmd.REPO_ROOT, "errors/error-catalog-v1.yaml")
    codes = []
    current = None
    for line in open(path, encoding="utf-8"):
        stripped = line.strip()
        if stripped.startswith("- code:"):
            current = {"code": stripped.split(":", 1)[1].strip()}
            codes.append(current)
        elif current is not None and stripped.startswith("http_status:"):
            current["http_status"] = int(stripped.split(":", 1)[1].strip())
        elif current is not None and stripped.startswith("retry_class:"):
            current["retry_class"] = stripped.split(":", 1)[1].strip()
        elif current is not None and stripped.startswith("meaning:"):
            current["meaning"] = stripped.split(":", 1)[1].strip().strip('"')
    if not codes:
        sys.exit("errors/error-catalog-v1.yaml produced no codes; run gen_errors.py first")
    return codes


def parse_cards():
    repo1 = specmd.read_spec("repo1")
    body = specmd.section(repo1, "Appendix C — Complete Endpoint Catalog")
    heads = re.findall(r"^## (C\.\d+) ([A-Z]+) (\S+)\s*$", body, re.M)
    cards = []
    for cid, method, path in heads:
        rows = {r[0]: r[1] for r in specmd.table(specmd.section(body, "%s %s %s" % (cid, method, path)))["rows"]}
        cards.append(
            {
                "id": cid,
                "method": method.lower(),
                "path": path,
                "purpose": rows.get("Purpose", ""),
                "permission": rows.get("Permission / caller", ""),
                "idempotency": rows.get("Idempotency", ""),
                "concurrency": rows.get("Concurrency", ""),
                "audit": rows.get("Audit", ""),
                "events": rows.get("Events", ""),
                "errors": rows.get("Errors", ""),
                "rate": rows.get("Rate/size", ""),
                "notes": rows.get("Notes", ""),
            }
        )
    return cards


def tag_for(path):
    for prefix, tag in TAG_BY_PREFIX:
        if path.startswith(prefix):
            return tag
    sys.exit("no tag rule for path %s" % path)


def path_parameters(path):
    params = []
    for name in re.findall(r"\{(\w+)\}", path):
        if name not in PARAM_DESCRIPTIONS:
            sys.exit("no description for path parameter %r in %s" % (name, path))
        schema = {"type": "string"} if name in OPAQUE_PARAMS or name in {"subject", "type", "member"} else {"type": "string", "format": "uuid"}
        params.append(
            {
                "name": name,
                "in": "path",
                "required": True,
                "description": PARAM_DESCRIPTIONS[name],
                "schema": schema,
            }
        )
    return params


def query_parameters(cid):
    names = QUERY.get(cid)
    if not names:
        return []
    common = {"cursor", "limit"}
    out = []
    for name in names:
        if name in common:
            out.append({"$ref": "#/components/parameters/%s" % ("Cursor" if name == "cursor" else "Limit")})
        elif name == "q":
            out.append({"name": "q", "in": "query", "required": False, "description": "Free-text filter. For search operations the value is parsed to a typed AST; raw backend syntax is never interpolated (Repo 1 §21.2).", "schema": {"type": "string", "maxLength": 512}})
        elif name in {"from", "to"}:
            out.append({"name": name, "in": "query", "required": False, "description": "Inclusive RFC 3339 UTC bound on `occurred_at`.", "schema": {"type": "string", "format": "date-time"}})
        elif name == "folder_ref":
            out.append({"name": "folder_ref", "in": "query", "required": False, "description": "Opaque folder reference. Defaults to the INBOX special-use folder (C.70 notes).", "schema": {"type": "string"}})
        elif name.endswith("_id"):
            out.append({"name": name, "in": "query", "required": False, "schema": {"type": "string", "format": "uuid"}})
        else:
            out.append({"name": name, "in": "query", "required": False, "schema": {"type": "string", "maxLength": 128}})
    return out


def components(doc_key, catalog):
    internal = DOCUMENTS[doc_key]["internal"]
    by_status = {}
    for entry in catalog:
        by_status.setdefault(entry["http_status"], []).append(entry)

    schemas = {
        "Problem": {
            "type": "object",
            "description": "RFC 9457 problem details with the Karyalay extensions of Master §20.3 and Repo 1 §26.1. `code` is the stable programmatic identifier; `title` and `detail` are human strings that may be localized and may change.",
            "required": ["type", "title", "status", "code"],
            "properties": {
                "type": {"type": "string", "format": "uri", "description": "https://errors.karyalay.in/mail/{code}"},
                "title": {"type": "string"},
                "status": {"type": "integer", "minimum": 100, "maximum": 599},
                "code": {"$ref": "#/components/schemas/ErrorCode"},
                "detail": {"type": "string", "description": "Operator- and user-safe. Never SQL, a file path, a stack trace, an internal IP or another tenant's address (Master §23.5, Repo 1 §39)."},
                "request_id": {"type": "string", "maxLength": 128},
                "trace_id": {"type": "string", "pattern": "^[0-9a-f]{32}$"},
                "errors": {"type": "array", "items": {"$ref": "#/components/schemas/ValidationError"}},
            },
        },
        "ErrorCode": {
            "type": "string",
            "description": "A code from errors/error-catalog-v1.yaml. This enum is generated from that catalog, so an endpoint cannot introduce a code the catalog does not define.",
            "enum": [e["code"] for e in catalog],
        },
        "Cursor": {
            "type": ["string", "null"],
            "description": "Opaque pagination cursor. Clients do not construct, parse or reorder cursors (Master §20.4, Repo 1 §26).",
        },
    }
    for name, schema in SCHEMAS.items():
        schemas[name] = schema

    parameters = {
        "Cursor": {"name": "cursor", "in": "query", "required": False, "description": "Opaque cursor from a previous page's `next_cursor`.", "schema": {"$ref": "#/components/schemas/Cursor"}},
        "Limit": {"name": "limit", "in": "query", "required": False, "description": "Bounded page size. No total_count is returned unless it is efficient and explicit (Repo 1 §26).", "schema": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50}},
    }

    headers = {
        "RequestId": {"description": "Echo of the accepted or generated `X-Request-ID` (Repo 1 §26, Master §20.7).", "schema": {"type": "string", "maxLength": 128}},
        "ETag": {"description": "Optimistic concurrency token. Supply it as `If-Match` on the next update (Master §20.6).", "schema": {"type": "string"}},
        "RetryAfter": {"description": "Delay before retrying, for codes in the RETRY_AFTER class (Repo 1 §39).", "schema": {"type": "integer", "minimum": 0}},
    }

    responses = {}
    for status in sorted(by_status):
        if status == 202:
            continue
        entries = sorted(by_status[status], key=lambda e: e["code"])
        narrowed = json.loads(json.dumps(schemas["Problem"]))
        narrowed["description"] = (
            "RFC 9457 problem details for HTTP %d. `code` is narrowed to the catalog "
            "codes that map to this status." % status
        )
        narrowed["properties"]["status"] = dict(narrowed["properties"]["status"], const=status)
        narrowed["properties"]["code"] = {
            "type": "string",
            "description": "A code from errors/error-catalog-v1.yaml whose default HTTP mapping is %d." % status,
            "enum": [e["code"] for e in entries],
        }
        responses["E%d" % status] = {
            "description": "\n".join(["%s — %s (%s)" % (e["code"], e["meaning"], e["retry_class"]) for e in entries]),
            "headers": {"X-Request-ID": {"$ref": "#/components/headers/RequestId"}},
            "content": {"application/problem+json": {"schema": narrowed}},
        }
    if "E429" in responses:
        responses["E429"]["headers"]["Retry-After"] = {"$ref": "#/components/headers/RetryAfter"}

    if internal:
        security_schemes = {
            "serviceMtls": {
                "type": "mutualTLS",
                "description": "Mutually authenticated TLS between named service identities (Master §9.6, Repo 1 §29.2).",
            },
            "serviceToken": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Short-lived scoped workload token. `karyalay_principal_type` is `service_identity` and the token states audience and scopes (auth/claims-v1.yaml, Master §9.6). A user access token with the wrong audience or client is rejected (Repo 1 §29.2).",
            },
        }
    else:
        security_schemes = {
            "oidcBearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "OIDC access token from Karyalay identity, validated per Repo 1 §17.1 and shaped by auth/claims-v1.yaml. `karyalay_principal_type` is `end_user`. Roles and permissions are NOT read from the token: Repo 1 §8.1 loads membership and effective role assignments from canonical projections on every request.",
            }
        }

    return {
        "schemas": schemas,
        "parameters": parameters,
        "headers": headers,
        "responses": responses,
        "securitySchemes": security_schemes,
    }


def describe(card, binding):
    lines = [
        card["purpose"],
        "",
        "**Catalog:** Appendix C %s. **Permission:** `%s`." % (card["id"], card["permission"]),
        "",
        "**Notes:** %s" % card["notes"],
        "",
        "**Validation order:** Authentication → tenant/object visibility → permission/state/entitlement/restriction → request validation → concurrency/idempotency → transaction/external effect (Repo 1 Appendix C).",
        "",
        "**Audit:** %s" % card["audit"],
        "**Events:** %s" % card["events"],
        "**Errors:** %s" % card["errors"],
        "**Rate/size:** %s" % card["rate"],
    ]
    return "\n".join(l for l in lines if l is not None)


def build_operation(card, binding, catalog_codes):
    method = card["method"]
    notes = card["notes"]
    doc = DOCUMENTS[binding["doc"]]

    operation = {
        "operationId": binding["op"],
        "summary": card["purpose"],
        "description": describe(card, binding),
        "tags": [tag_for(card["path"])],
        "x-karyalay-catalog-id": card["id"],
        "x-karyalay-permission": card["permission"],
    }

    parameters = path_parameters(card["path"]) + query_parameters(card["id"])
    if parameters:
        operation["parameters"] = parameters

    if binding.get("unauthenticated"):
        operation["security"] = []
        operation["description"] += "\n\n**Auth:** unauthenticated within the internal network boundary; never routed from the public internet (C.105 notes)."

    # --- concurrency: If-Match where the card demands it -------------------
    if re.search(r"If-Match required|Requires If-Match|ETag/precondition", notes, re.I):
        operation.setdefault("parameters", []).append(
            {
                "name": "If-Match",
                "in": "header",
                "required": True,
                "description": "Required by this operation's Appendix C card. A stale or absent value returns VERSION_CONFLICT rather than silently overwriting (Master §20.6, §24.5).",
                "schema": {"type": "string"},
            }
        )
    elif method in {"put", "patch"}:
        operation.setdefault("parameters", []).append(
            {
                "name": "If-Match",
                "in": "header",
                "required": False,
                "description": "Optimistic concurrency token from the resource's ETag. Honoured when supplied (Master §20.6).",
                "schema": {"type": "string"},
            }
        )

    # --- idempotency: required where the card says so ----------------------
    #
    # The card states the requirement in two places and this reads both.
    #
    # The structured `Idempotency` row carries the class rule -- "Required for
    # POST create/final-send/provisioning/restriction operations" -- but it is
    # byte-identical boilerplate on all 115 cards, so it says which *classes*
    # need a key without saying which class a given operation is in. The Notes
    # line is where a card declares that, and it does so in prose.
    #
    # The first pattern below used to be the only one, and it matched the
    # literal token `Idempotency-Key`. C.101's Notes say "idempotency
    # required" -- the same requirement, two words different -- so it emitted
    # `required: false` on an operation whose own card says required, and
    # whose class (restriction) the row names explicitly. C.100 ("idempotency
    # validation mandatory") failed the same way. Both are replay-sensitive
    # mutations from Ops, which is the exact case Master §20.5 exists for.
    #
    # The second pattern matches the requirement however the card phrases it.
    # It deliberately does NOT match a bare "idempotent", which is a claim
    # about the operation's semantics rather than about the caller's duty to
    # send a key -- C.75's "idempotent flag semantics" is not a key
    # requirement, and reading it as one would put a mandatory header on a
    # flag mutation. Four cards sit in that ambiguous set (C.16, C.29, C.75,
    # C.77); they are recorded in ADR-KEM-010 as a question for the appendix
    # owner rather than resolved by this generator, because deciding them here
    # would be exactly the reinterpretation specmd.py forbids.
    idempotency_required = bool(
        re.search(r"Idempotency-Key (?:required|mandatory)|Idempotency-Key;", notes, re.I)
        or re.search(r"idempotenc(?:y|e)\b[^.;]{0,40}?\b(?:required|mandatory)", notes, re.I)
    )
    if method == "post" and idempotency_required:
        operation.setdefault("parameters", []).append(
            {
                "name": "Idempotency-Key",
                "in": "header",
                "required": True,
                "description": "Required by this operation's Appendix C card. Caller scope plus key maps to one request fingerprint and outcome for the retention window; the same key with a different canonical request is IDEMPOTENCY_KEY_REUSED (Master §20.5, §24.3, Repo 1 §34.1).",
                "schema": {"type": "string", "maxLength": 128},
            }
        )
    elif method == "post" and not binding.get("unauthenticated"):
        operation.setdefault("parameters", []).append(
            {
                "name": "Idempotency-Key",
                "in": "header",
                "required": False,
                "description": "Honoured when supplied (Master §20.5).",
                "schema": {"type": "string", "maxLength": 128},
            }
        )

    # --- request body ------------------------------------------------------
    if binding.get("req_media") == "multipart/form-data":
        operation["requestBody"] = {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["file"],
                        "properties": {
                            "file": {"type": "string", "format": "binary"},
                            "filename": {"type": "string", "maxLength": 255},
                        },
                    }
                }
            },
            "description": "Streamed upload to private temporary storage with a TTL and a scan hook (C.87 notes).",
        }
    elif binding.get("req"):
        operation["requestBody"] = {
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/%s" % binding["req"]}}},
        }

    # --- responses ---------------------------------------------------------
    status = binding.get("status", 200)
    success_headers = {"X-Request-ID": {"$ref": "#/components/headers/RequestId"}}
    if method in {"get", "put", "patch"} and binding.get("res") and not binding.get("list") and not binding.get("binary"):
        success_headers["ETag"] = {"$ref": "#/components/headers/ETag"}

    if binding.get("binary"):
        media = binding.get("media", "application/octet-stream")
        success = {
            "description": "Streamed content. Bounded, with a safe filename and Content-Disposition (C.73, C.74 notes).",
            "headers": dict(success_headers, **{"Content-Disposition": {"description": "attachment, with a sanitized filename.", "schema": {"type": "string"}}}),
            "content": {media: {"schema": {"type": "string", "format": "binary"}}},
        }
    elif status == 204:
        success = {"description": "Deleted. The operation is idempotent: repeating it on an already-absent resource is not an error.", "headers": success_headers}
    elif binding.get("list"):
        success = {
            "description": "A bounded page. There is no fetch-all endpoint (Repo 1 §20.2).",
            "headers": success_headers,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["data", "next_cursor"],
                        "properties": {
                            "data": {"type": "array", "items": {"$ref": "#/components/schemas/%s" % binding["res"]}},
                            "next_cursor": {"$ref": "#/components/schemas/Cursor"},
                        },
                    }
                }
            },
        }
    else:
        description = "Success."
        if status == 201:
            description = "Created."
        elif status == 202:
            description = "Accepted for asynchronous processing. 202 is used only with an explicit status resource, never to conceal a failed synchronous validation (Repo 1 §39.1)."
        success = {
            "description": description,
            "headers": success_headers,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/%s" % binding["res"]}}},
        }

    responses = {str(status): success}

    applicable = {401, 403, 404, 429, 500, 503}
    if not doc["internal"]:
        applicable.add(422)
    if method in {"post", "put", "patch", "delete"}:
        applicable |= {409, 422}
    if operation.get("requestBody"):
        applicable |= {413, 415, 422}
    if any(p.get("name") == "If-Match" for p in operation.get("parameters", [])):
        applicable.add(412)
    if method == "post" and idempotency_required:
        applicable.add(400)
    if binding["op"] == "sendMessage":
        applicable |= {202}
    for code in sorted(applicable):
        if code == 202:
            continue
        key = "E%d" % code
        responses[str(code)] = {"$ref": "#/components/responses/%s" % key}

    operation["responses"] = responses
    return operation


def prune(paths, all_components):
    """Emit only the components a document actually reaches.

    Master §0.3 names four self-contained documents, so every document carries
    its own components. Carrying the *whole* component set into each one leaves
    a reader unable to tell which schemas the document really uses, so the
    unreachable ones are dropped.
    """
    kept = {"schemas": {}, "parameters": {}, "headers": {}, "responses": {}, "securitySchemes": all_components["securitySchemes"]}
    pending = []

    def collect(node):
        if isinstance(node, list):
            for item in node:
                collect(item)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str) and value.startswith("#/components/"):
                    _, _, section, name = value.split("/", 3)
                    pending.append((section, name))
                else:
                    collect(value)

    collect(paths)
    while pending:
        section, name = pending.pop()
        if name in kept.get(section, {}):
            continue
        source = all_components.get(section, {})
        if name not in source:
            sys.exit("unresolved component reference: #/components/%s/%s" % (section, name))
        kept.setdefault(section, {})[name] = source[name]
        collect(source[name])

    for section in list(kept):
        if not kept[section]:
            del kept[section]
    return kept


def build_document(doc_key, cards, catalog):
    meta = DOCUMENTS[doc_key]
    paths = {}
    count = 0
    for card in cards:
        binding = OPS[card["id"]]
        if binding["doc"] != doc_key:
            continue
        operation = build_operation(card, binding, catalog)
        paths.setdefault(card["path"], {})[card["method"]] = operation
        count += 1

    security = [] if meta["internal"] else [{"oidcBearer": []}]
    if meta["internal"]:
        security = [{"serviceMtls": [], "serviceToken": []}]

    all_components = components(doc_key, catalog)
    used = prune(paths, all_components)
    tags = sorted({op["tags"][0] for item in paths.values() for op in item.values()})

    document = {
        "openapi": "3.1.0",
        "info": {
            "title": meta["title"],
            "version": CONTRACT_VERSION,
            "summary": meta["summary"],
            "description": "\n".join(
                [
                    meta["summary"],
                    "",
                    "**Source:** %s." % meta["spec"],
                    "**Audience:** %s" % meta["audience"],
                    "",
                    "Appendix C is exhaustive by invariant: no undocumented route may be exposed in production. Operation count in this document is %d and every operation carries `x-karyalay-catalog-id`, so the reconciliation against the appendix is mechanical." % count,
                    "",
                    "Conventions (Repo 1 §26, Master §20): base path `/api/v1` or `/internal/v1`; snake_case JSON; RFC 3339 UTC timestamps; opaque cursor pagination; `X-Request-ID` accepted or generated and echoed; W3C `traceparent` propagated; `Idempotency-Key` on documented replay-sensitive operations; ETag/`If-Match` on documented versioned updates; `application/problem+json` errors carrying a stable `code`.",
                ]
            ),
            "license": {"name": "Proprietary — Karyalay", "identifier": "LicenseRef-Karyalay-Proprietary"},
            "x-karyalay-contract": "karyalay-mail-contracts",
            "x-karyalay-contract-version": CONTRACT_VERSION,
        },
        "servers": [{"url": meta["server"], "description": "Production."}],
        "security": security,
        "tags": [{"name": t, "description": TAG_DESCRIPTIONS[t]} for t in tags],
        "paths": paths,
        "components": used,
    }
    return document, count


def main():
    catalog = load_error_catalog()
    cards = parse_cards()
    if len(cards) != 115:
        sys.exit("Appendix C parsed to %d cards; the appendix preamble states 115" % len(cards))

    missing = sorted(set(c["id"] for c in cards) - set(OPS))
    if missing:
        sys.exit("no binding for catalog entries: %s" % ", ".join(missing))
    extra = sorted(set(OPS) - set(c["id"] for c in cards))
    if extra:
        sys.exit("binding table names entries absent from Appendix C: %s" % ", ".join(extra))

    reconciliation = []
    total = 0
    for doc_key in (PUBLIC, MAILBOX, PROVISIONING, OPERATIONS):
        document, count = build_document(doc_key, cards, catalog)
        header = (
            "%s\n"
            "\n"
            "GENERATED by tools/derive/gen_openapi.py. Do not hand-edit.\n"
            "Operations transcribed from karyalay-mail repository-spec-v1.0 Appendix C.\n"
            "Error responses generated from errors/error-catalog-v1.yaml.\n"
            "Filename fixed by Master Contract §0.3." % DOCUMENTS[doc_key]["title"]
        )
        specmd.write_yaml(DOCUMENTS[doc_key]["file"], document, header)
        total += count
        print("wrote %s (%d operations)" % (DOCUMENTS[doc_key]["file"], count))
        for card in cards:
            if OPS[card["id"]]["doc"] == doc_key:
                reconciliation.append(
                    {
                        "catalog_id": card["id"],
                        "method": card["method"].upper(),
                        "path": card["path"],
                        "operation_id": OPS[card["id"]]["op"],
                        "document": os.path.basename(DOCUMENTS[doc_key]["file"]),
                        "permission": card["permission"],
                    }
                )

    if total != 115:
        sys.exit("emitted %d operations; expected 115" % total)

    reconciliation.sort(key=lambda r: int(r["catalog_id"].split(".")[1]))
    specmd.write_yaml(
        "openapi/catalog-reconciliation-v1.yaml",
        {
            "contract": "karyalay-mail-contracts/openapi",
            "contract_version": CONTRACT_VERSION,
            "source": "karyalay-mail repository-spec-v1.0 Appendix C",
            "declared_operation_count": 115,
            "emitted_operation_count": total,
            "public_surface_count": sum(1 for r in reconciliation if r["catalog_id"] in ["C.%d" % n for n in list(range(1, 66)) + list(range(92, 97))]),
            "operations": reconciliation,
        },
        "Karyalay Mail — Appendix C reconciliation\n"
        "\n"
        "GENERATED by tools/derive/gen_openapi.py. Do not hand-edit.\n"
        "T00.04/T00.05 evidence: the C-number to operationId map. The harness fails\n"
        "if any row's operationId is absent from the document it names.",
    )
    print("wrote openapi/catalog-reconciliation-v1.yaml (%d operations reconciled)" % total)


if __name__ == "__main__":
    main()
