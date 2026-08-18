#!/usr/bin/env python3
"""T00.03 — transcribe the claims, role and permission contracts into auth/.

Sources:
  - Master §10.2/§10.3   the canonical customer and platform role catalog
  - Master §9            identity, session and service-identity architecture
  - Master §6.3          canonical field names
  - Repo 1 Appendix B    the permission catalog and its default role bundles
  - Repo 1 §8.1, §17–§18 TenantContext construction and the authorization model

Nothing here invents policy. Where Repo 1 Appendix B qualifies a role bundle
in prose ("auditor (metadata only)", "mailbox_user or explicit send grant"),
the qualifier is preserved verbatim rather than normalised away.
"""

import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import specmd

ROLE_TOKEN = re.compile(r"^([a-z][a-z0-9_]*)(?=$|[\s(])")
BARE_ROLE = re.compile(r"[a-z][a-z0-9_]*(\s*\(.+\))?")


def parse_bundles(raw, known_roles):
    """Split an Appendix B 'Default role bundles' cell into roles and notes.

    A fragment whose leading token is a role in the Master Contract catalog
    yields a role, with any remaining prose kept verbatim as its condition.
    A fragment that reads as prose — "security-approved automation", "platform
    only via separate elevated operation" — is kept whole as a note, because it
    names a policy path rather than a role. A fragment that is a bare
    role-shaped token the Master Contract does not define is an error, not a
    note: that is a genuine divergence and belongs in an ADR.
    """
    roles, notes = [], []
    for fragment in [f.strip() for f in re.split(r"[;,]", raw) if f.strip()]:
        match = ROLE_TOKEN.match(fragment)
        token = match.group(1) if match else None
        if token in known_roles:
            condition = fragment[len(token):].strip().strip("()").strip()
            entry = {"role": token}
            if condition:
                entry["condition"] = condition
            roles.append(entry)
        elif token and BARE_ROLE.fullmatch(fragment):
            sys.exit(
                "Appendix B names %r as a role bundle but the Master Contract "
                "§10.2/§10.3 catalog does not define it.\n"
                "Raise an ADR (Master §0.2); do not add it here." % fragment
            )
        else:
            notes.append(fragment)
    return roles, notes


def parse_master_roles(master):
    out = []
    for heading, scope in (
        ("10.2 Customer roles baseline", "customer"),
        ("10.3 Platform roles baseline", "platform"),
    ):
        body = specmd.section(master, heading)
        for row in specmd.rows_as_dicts(specmd.table(body)):
            out.append(
                {
                    "role": specmd.unmark(row["Role"]).strip("`\\ "),
                    "scope": scope,
                    "baseline_purpose": row["Baseline purpose"],
                }
            )
    return out


# Fixed clock for the examples. Master §20.2 requires RFC 3339 UTC; a constant
# keeps regeneration byte-identical so a diff means a contract change.
EXAMPLE_IAT = 1787011200        # 2026-08-18T00:00:00Z
EXAMPLE_TTL = 900               # tokens are short-lived (Master §9.2)
ISSUER = "https://identity.karyalay.in"


def example_uuid(seed):
    """Deterministic UUIDv7-shaped identifier for fixtures only.

    Version and variant nibbles are set so the value is a syntactically valid
    UUIDv7 (RFC 9562, Master §6.2). It is a fixture, never a generator.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return "%s-%s-7%s-%s%s-%s" % (
        digest[0:8], digest[8:12], digest[13:16],
        "89ab"[int(digest[16], 16) % 4], digest[17:20], digest[20:32],
    )


def write_examples(roles):
    """One sample token per role, plus a service identity.

    Repo 1 §8.1 resolves roles server-side, so the role does not appear in the
    token. These fixtures record which role the subject is expected to resolve
    to, so T00.03's "validates a sample token for each defined role" acceptance
    criterion is testable without a role claim existing.
    """
    manifest = []
    for role in roles:
        code = role["role"]
        token = {
            "iss": ISSUER,
            "sub": example_uuid("subject:" + code),
            "aud": "karyalay-mail-api",
            "exp": EXAMPLE_IAT + EXAMPLE_TTL,
            "nbf": EXAMPLE_IAT,
            "iat": EXAMPLE_IAT,
            "jti": example_uuid("jti:" + code),
            "karyalay_principal_type": "end_user",
            "acr": "urn:karyalay:acr:mfa" if role["scope"] == "platform" else "urn:karyalay:acr:pwd",
            "amr": ["pwd", "hwk"] if role["scope"] == "platform" else ["pwd"],
            "auth_time": EXAMPLE_IAT - 60,
            "sid": example_uuid("sid:" + code),
            "azp": "karyalay-webmail",
            "scope": "openid profile email",
        }
        if role["scope"] == "customer":
            token["karyalay_organisation_id"] = example_uuid("organisation:" + code)
        name = "end-user-%s.json" % code.replace("_", "-")
        specmd.write_json("auth/examples/" + name, token)
        manifest.append(
            {
                "file": name,
                "principal_type": "end_user",
                "expected_role": code,
                "role_scope": role["scope"],
                "note": "The role is not a claim. It is what Repo 1 §8.1 step 3 resolves for this subject.",
            }
        )

    service = {
        "iss": ISSUER,
        "sub": "svc:karyalay-mail-infra-controller",
        "aud": "karyalay-mail-internal",
        "exp": EXAMPLE_IAT + 300,
        "nbf": EXAMPLE_IAT,
        "iat": EXAMPLE_IAT,
        "jti": example_uuid("jti:service"),
        "karyalay_principal_type": "service_identity",
        "scope": "provisioning.observe provisioning.report",
    }
    specmd.write_json("auth/examples/service-identity.json", service)
    manifest.append(
        {
            "file": "service-identity.json",
            "principal_type": "service_identity",
            "expected_role": None,
            "role_scope": None,
            "note": "Master §9.6: audience and scopes are stated; no tenant, session or MFA claim.",
        }
    )

    specmd.write_yaml(
        "auth/examples/manifest-v1.yaml",
        {
            "contract": "karyalay-mail-contracts/auth/examples",
            "contract_version": "0.1.0",
            "validates_against": "../claims-v1.yaml",
            "purpose": "T00.03 acceptance: a sample token for every role defined in roles-v1.yaml.",
            "examples": manifest,
        },
        "Karyalay Mail — claims examples manifest\n"
        "\n"
        "GENERATED by tools/derive/gen_auth.py. Do not hand-edit.\n"
        "Executable contract fixtures (Repo 1 §26.2): the harness validates every\n"
        "file listed here against auth/claims-v1.yaml.",
    )
    print("wrote auth/examples/ (%d fixtures)" % len(manifest))


def main():
    repo1 = specmd.read_spec("repo1")
    master = open(
        os.path.join(specmd.REPO_ROOT, "docs/spec/master-contract-v1.0.md"), encoding="utf-8"
    ).read()

    roles = parse_master_roles(master)
    known_roles = {r["role"] for r in roles}

    # --- permissions ------------------------------------------------------
    body = specmd.section(repo1, "Appendix B — Permission Matrix")
    permissions = []
    for row in specmd.rows_as_dicts(specmd.table(body, 0)):
        roles_for_row, notes = parse_bundles(row["Default role bundles"], known_roles)
        entry = {
            "permission": row["Permission"],
            "meaning": row["Meaning"],
            "default_role_bundles": roles_for_row,
            "source_text": row["Default role bundles"],
        }
        if notes:
            entry["notes"] = notes
        permissions.append(entry)

    relations = [
        {"resource": row["Resource"], "relation_requirement": row["Relation requirement"]}
        for row in specmd.rows_as_dicts(specmd.table(body, 1))
    ]

    permissions_doc = {
        "contract": "karyalay-mail-contracts/auth/permissions",
        "contract_version": "0.1.0",
        "sources": {
            "permissions": "karyalay-mail repository-spec-v1.0 Appendix B",
            "object_relations": "karyalay-mail repository-spec-v1.0 Appendix B.1",
            "model": "karyalay-mail repository-spec-v1.0 §18",
        },
        "authorization_model": {
            "description": (
                "allow = authenticated AND tenant_membership_valid AND permission_granted(action) "
                "AND object_relation_valid(resource) AND parent_states_allow(action) AND "
                "entitlement_allows(feature/limit) AND no_effective_restriction_blocks(action) AND "
                "assurance_level_sufficient"
            ),
            "source": "karyalay-mail repository-spec-v1.0 §18",
            "rules": [
                "Roles are bundles of permissions; the permission is the enforcement primitive (Master §10.1).",
                "Controllers call a centralized policy service; scattered role-name comparisons are forbidden (Repo 1 §18).",
                "Role defaults below are seed/policy guidance, not a shortcut to role-name checks (Repo 1 Appendix B preamble).",
                "UI hiding is not authorization (Master Appendix B.1).",
                "Roles are tenant-scoped (Master §10.2).",
            ],
        },
        "break_glass": {
            "permission": "platform.break_glass",
            "semantics_reference": "karyalay-mail repository-spec-v1.0 §18.1; Master §7.5, §10.3",
            "note": (
                "Referenced, not defined here. §18.1 requires a separately designed short-lived "
                "elevated workflow with reason/ticket capture, stronger authentication, optional "
                "dual approval, prominent audit/security events and automatic expiry. It cannot be "
                "implemented by a hidden master password, a shared credential, or a database role "
                "granted to the web process."
            ),
        },
        "object_relations": relations,
        "permissions": permissions,
    }
    specmd.write_yaml(
        "auth/permissions-v1.yaml",
        permissions_doc,
        "Karyalay Mail — permission catalog v1\n"
        "\n"
        "GENERATED by tools/derive/gen_auth.py. Do not hand-edit.\n"
        "Transcribed from karyalay-mail repository-spec-v1.0 Appendix B and B.1.\n"
        "Filename fixed by Master Contract §0.3.",
    )

    # --- roles ------------------------------------------------------------
    granted = {}
    for entry in permissions:
        for bundle in entry["default_role_bundles"]:
            record = {"permission": entry["permission"]}
            if "condition" in bundle:
                record["condition"] = bundle["condition"]
            granted.setdefault(bundle["role"], []).append(record)

    for role in roles:
        role["default_permissions"] = granted.get(role["role"], [])

    roles_doc = {
        "contract": "karyalay-mail-contracts/auth/roles",
        "contract_version": "0.1.0",
        "sources": {
            "role_catalog": "Karyalay Email Master Architecture & Integration Contract v1.0 §10.2, §10.3",
            "default_permissions": "karyalay-mail repository-spec-v1.0 Appendix B (inverted)",
        },
        "rules": [
            "The role catalog is the Master Contract's; a repository may not add a role at a shared boundary.",
            "default_permissions is the inverse index of auth/permissions-v1.yaml and carries no independent authority.",
            "A role with an empty default_permissions set is defined by the Master Contract but granted nothing by Repo 1 Appendix B; see ADR-KEM-007.",
        ],
        "roles": roles,
    }
    specmd.write_yaml(
        "auth/roles-v1.yaml",
        roles_doc,
        "Karyalay Mail — role catalog v1\n"
        "\n"
        "GENERATED by tools/derive/gen_auth.py. Do not hand-edit.\n"
        "Roles from Master Contract §10.2/§10.3; default permission bundles inverted\n"
        "from karyalay-mail repository-spec-v1.0 Appendix B.\n"
        "Filename fixed by Master Contract §0.3.",
    )

    write_examples(roles)

    ungranted = [r["role"] for r in roles if not r["default_permissions"]]
    print(
        "wrote auth/permissions-v1.yaml (%d permissions, %d object relations)"
        % (len(permissions), len(relations))
    )
    print("wrote auth/roles-v1.yaml (%d roles; %d with no Appendix B grant: %s)"
          % (len(roles), len(ungranted), ", ".join(ungranted) or "none"))


if __name__ == "__main__":
    main()
