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
)

LINE = re.compile(r"^contract_version:.*$", re.MULTILINE)


def main():
    changed = 0
    for rel in HAND_AUTHORED:
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as handle:
            body = handle.read()

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
