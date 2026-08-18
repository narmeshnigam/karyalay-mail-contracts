#!/usr/bin/env python3
"""T00.02 — transcribe the event envelope and the 45-event catalog into events/.

Sources:
  - Master Contract §22.3   the canonical envelope (precedence 1, Master §0.2)
  - Master Contract §22.2   at-least-once / ordering / redelivery semantics
  - Master Contract §22.5   payload data minimisation
  - Repo 1 Appendix D       the 45 events and their minimum semantic fields
  - Repo 1 §31.2            NATS stream and subject naming
  - tools/derive/fieldtypes exact types, as Appendix D delegates

The envelope follows Master §22.3, not Repo 1 §31.1 — the two disagree and
the Master Contract has precedence. The divergence is recorded in
ADR-KEM-006; it is not resolved here.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import specmd
from fieldtypes import FIELDS
from version import CONTRACT_VERSION

STREAM = "KARYALAY_MAIL_EVENTS_V1"
SUBJECT_PREFIX = "mail.v1"
SCHEMA_BASE = "https://contracts.karyalay.in/mail/events"
GENERATED_BY = "tools/derive/gen_events.py"


def envelope_schema():
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "%s/envelope-v1.schema.json" % SCHEMA_BASE,
        "title": "Karyalay Mail event envelope v1",
        "description": (
            "The shared envelope every Karyalay event carries, transcribed from Master "
            "Contract §22.3. No repository redefines it. `data` is constrained by the "
            "per-event payload schema named in events/catalog-v1.yaml; this schema "
            "deliberately leaves it open so the envelope can be validated independently "
            "of any one event."
        ),
        "$comment": (
            "Consumer semantics (Master §22.2, Repo 1 §31.2): delivery is at-least-once and "
            "the same event_id may be redelivered after a broker acknowledgement that the "
            "producer failed to record. Handlers MUST be idempotent on event_id. Ordering is "
            "guaranteed only where documented for a resource; compare resource.generation "
            "when order matters. Poison events go to dead-letter with alerting, never silent "
            "deletion."
        ),
        "type": "object",
        "required": ["event", "version", "event_id", "occurred_at", "producer", "resource", "data"],
        "additionalProperties": False,
        "properties": {
            "event": {
                "type": "string",
                "description": "Lower-case dotted past-tense fact name (Master §22.4). Command-style names are not events.",
                "pattern": "^[a-z][a-z0-9_]*\\.[a-z][a-z0-9_]*$",
                "maxLength": 96,
            },
            "version": {
                "type": "integer",
                "minimum": 1,
                "description": (
                    "Event schema major version. An unknown version is routed to a compatibility "
                    "error/alert, never parsed as an older version (Repo 1 Appendix D.1)."
                ),
            },
            "event_id": {
                "type": "string",
                "format": "uuid",
                "description": (
                    "UUIDv7 (RFC 9562, Master §6.2). Also the NATS Nats-Msg-Id and the consumer "
                    "deduplication key. Never overloaded with request_id, trace_id or an "
                    "idempotency key (Master §6.2)."
                ),
            },
            "occurred_at": {
                "type": "string",
                "format": "date-time",
                "description": "RFC 3339 UTC instant the fact was committed (Master §20.2).",
            },
            "producer": {
                "type": "string",
                "description": "Repository/service that committed the fact.",
                "enum": ["karyalay-mail", "karyalay-mail-infra", "karyalay-mail-ops"],
            },
            "trace_id": {
                "type": ["string", "null"],
                "description": "W3C trace context trace-id carried across the outbox hop (Master §30.1, §20.7).",
                "pattern": "^[0-9a-f]{32}$",
            },
            "request_id": {
                "type": ["string", "null"],
                "description": "Correlation ID of the request that caused the fact (Master §6.3, §20.7). Null for scheduler-originated facts.",
                "maxLength": 128,
            },
            "organisation_id": {
                "type": ["string", "null"],
                "format": "uuid",
                "description": (
                    "Tenant the fact belongs to (Master §6.3). Null only for security/platform "
                    "events that belong to no customer (Master §22.3)."
                ),
            },
            "resource": {
                "type": "object",
                "description": "The aggregate the fact is about (Master §22.3).",
                "required": ["type", "id"],
                "additionalProperties": False,
                "properties": {
                    "type": {
                        "type": "string",
                        "pattern": "^[a-z][a-z0-9_]*$",
                        "maxLength": 32,
                        "description": "Canonical entity name (Master Appendix A / §6.1).",
                    },
                    "id": {"type": "string", "format": "uuid"},
                    "generation": {
                        "type": ["integer", "null"],
                        "minimum": 0,
                        "description": (
                            "Desired revision of the resource (Master §6.2). Present for every "
                            "resource that participates in reconciliation; null for those that "
                            "do not. Consumers compare it when ordering matters (Master §22.2)."
                        ),
                    },
                },
            },
            "data": {
                "type": "object",
                "description": (
                    "Event payload. MUST NOT carry message bodies, attachment contents, "
                    "passwords, app-password secrets or private cryptographic keys "
                    "(Master §22.5, Repo 1 §31.3)."
                ),
            },
        },
    }


def payload_schema(event, meaning, fields):
    properties = {}
    for name in fields:
        if name not in FIELDS:
            sys.exit(
                "Appendix D field %r on event %s has no entry in tools/derive/fieldtypes.py.\n"
                "Add a typed entry with its normative citation; do not guess at generation time."
                % (name, event)
            )
        schema, source = FIELDS[name]
        prop = dict(schema)
        prop["$comment"] = "Type source: %s" % source
        properties[name] = prop
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "%s/%s-v1.schema.json" % (SCHEMA_BASE, event),
        "title": "%s v1 payload" % event,
        "description": meaning,
        "$comment": (
            "Payload for the `data` member of envelope-v1. Fields are the minimum semantic "
            "set from karyalay-mail repository-spec-v1.0 Appendix D; exact types are defined "
            "here because Appendix D delegates them to the generated schema. Additive optional "
            "fields may be introduced within version 1 where old consumers safely ignore them "
            "(Master §22.6); consumers ignore unknown additive fields (Repo 1 Appendix D.1), so "
            "this schema does not close the object."
        ),
        "type": "object",
        "required": list(fields),
        "properties": properties,
    }


def main():
    repo1 = specmd.read_spec("repo1")
    rows = specmd.rows_as_dicts(specmd.table(specmd.section(repo1, "Appendix D — Event Catalog")))

    specmd.write_json("events/envelope-v1.schema.json", envelope_schema())

    catalog = []
    seen = set()
    for row in rows:
        event = row["Event"].strip()
        if event in seen:
            sys.exit("duplicate event in Appendix D: %s" % event)
        seen.add(event)
        version = int(row["Ver."])
        if version != 1:
            sys.exit("Appendix D declares %s at version %d; v0.1.0 publishes v1 only" % (event, version))
        fields = [f.strip() for f in row["Minimum data"].split(",") if f.strip()]
        family = event.split(".", 1)[0]
        filename = "%s-v1.schema.json" % event
        specmd.write_json("events/" + filename, payload_schema(event, row["Meaning"].strip(), fields))
        catalog.append(
            {
                "event": event,
                "version": version,
                "subject": "%s.%s" % (SUBJECT_PREFIX, event),
                "family": family,
                "meaning": row["Meaning"].strip(),
                "producer": "karyalay-mail",
                "payload_schema": filename,
                "minimum_data": fields,
            }
        )

    index = {
        "contract": "karyalay-mail-contracts/events",
        "contract_version": CONTRACT_VERSION,
        "sources": {
            "envelope": "Karyalay Email Master Architecture & Integration Contract v1.0 §22.3",
            "catalog": "karyalay-mail repository-spec-v1.0 Appendix D",
            "transport": "karyalay-mail repository-spec-v1.0 §31.2",
        },
        "transport": {
            "broker": "NATS JetStream",
            "stream": STREAM,
            "subject_pattern": "%s.<family>.<event>" % SUBJECT_PREFIX,
            "message_id_header": "Nats-Msg-Id",
            "message_id_value": "event_id",
            "delivery": "at-least-once",
            "ordering": "guaranteed only where documented per resource; compare resource.generation",
            "poison_handling": "dead-letter/quarantine with alerting; never silent deletion",
        },
        "envelope_schema": "envelope-v1.schema.json",
        "events": catalog,
    }
    header = (
        "Karyalay Mail — event catalog index v1\n"
        "\n"
        "GENERATED by %s. Do not hand-edit.\n"
        "An index over the schema files in this directory, not a second contract\n"
        "surface: every field is copied from Master §22 or Repo 1 Appendix D/§31.2.\n"
        "\n"
        "This index covers the mail.v1.* stream only. Repo 3 (infra.v1.*) and Repo 4\n"
        "(ops.v1.*) publish their own streams; see ADR-KEM-006 for the reconciliation\n"
        "of those namespaces against Master Appendix C." % GENERATED_BY
    )
    specmd.write_yaml("events/catalog-v1.yaml", index, header)
    print("wrote events/: envelope-v1.schema.json, catalog-v1.yaml, %d payload schemas" % len(catalog))
    families = sorted({e["family"] for e in catalog})
    print("families (%d): %s" % (len(families), ", ".join(families)))


if __name__ == "__main__":
    main()
