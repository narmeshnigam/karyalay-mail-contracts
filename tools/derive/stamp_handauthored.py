#!/usr/bin/env python3
"""Stamp the contract version into the hand-authored artifacts.

Two published artifacts are written from prose rather than generated:

    observability/telemetry-contract-v1.yaml
    dns/domain-record-contract-v1.yaml

Being hand-authored, they sat outside the regeneration check, so cutting
v0.2.0 left both declaring `contract_version: 0.1.0` inside the v0.2.0 tag.
Bumping them by hand at each release just moves the same omission one release
later, so this rewrites the single line instead and runs as part of `derive`.
The CI regeneration stage then covers them exactly like a generated file.

Only the `contract_version:` line is touched. Everything else in these files
is prose-derived content this tool has no business editing.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version import CONTRACT_VERSION  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HAND_AUTHORED = (
    "observability/telemetry-contract-v1.yaml",
    "dns/domain-record-contract-v1.yaml",
    # Added 2026-08-24. This document is hand-authored -- it is not in
    # gen_openapi's DOCUMENTS -- and nothing stamped it, so its version sat at
    # whatever release it was last hand-edited in. It read 0.5.0 while every
    # other artifact moved to 0.6.0, and the only reason that was ever noticed
    # is that `validate.mjs` checks every OpenAPI document against the pin.
    #
    # A hand-authored artifact outside the stamper is an artifact that drifts
    # once per release and is corrected by hand each time, which is the shape
    # that eventually stops being corrected.
    "openapi/infra-executor-api-v1.yaml",
)

# Two spellings, because the two artifact families disagree and neither is
# wrong: the contract YAMLs carry `contract_version`, and an OpenAPI document
# carries `info.version` plus the `x-karyalay-contract-version` extension that
# `validate.mjs` reads. All three are the same number.
LINE = re.compile(r"^contract_version:.*$", re.MULTILINE)
OPENAPI_LINES = (
    re.compile(r"^(  version: ).*$", re.MULTILINE),
    re.compile(r"^(  x-karyalay-contract-version: ).*$", re.MULTILINE),
)


def main():
    changed = 0
    for rel in HAND_AUTHORED:
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as handle:
            body = handle.read()

        if rel.startswith("openapi/"):
            stamped = body
            for pattern in OPENAPI_LINES:
                if not pattern.search(stamped):
                    sys.exit(
                        "%s is missing a line this tool stamps (%s). Either it was "
                        "restructured or it is no longer a versioned artifact; this "
                        "tool will not guess which." % (rel, pattern.pattern)
                    )
                stamped = pattern.sub(lambda m: m.group(1) + CONTRACT_VERSION, stamped, count=1)

            if stamped != body:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(stamped)
                changed += 1
                print("stamped %s -> %s" % (rel, CONTRACT_VERSION))
            else:
                print("ok      %s (already %s)" % (rel, CONTRACT_VERSION))
            continue

        if not LINE.search(body):
            sys.exit(
                "%s has no top-level contract_version line. Either it was renamed "
                "or the file is no longer a versioned artifact; this tool will not "
                "guess which." % rel
            )

        stamped = LINE.sub("contract_version: %s" % CONTRACT_VERSION, body, count=1)
        if stamped != body:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(stamped)
            changed += 1
            print("stamped %s -> %s" % (rel, CONTRACT_VERSION))
        else:
            print("ok      %s (already %s)" % (rel, CONTRACT_VERSION))

    print("hand-authored artifacts stamped: %d changed, %d total"
          % (changed, len(HAND_AUTHORED)))


if __name__ == "__main__":
    main()
