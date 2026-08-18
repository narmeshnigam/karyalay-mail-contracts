"""The contract version, read from the one place that defines it.

Before this module the version was a literal in five generators and two
hand-authored YAML files. Cutting v0.2.0 updated five of the seven, so the
published tag declared `contract_version: 0.1.0` inside `observability/` and
`dns/` while everything else said 0.2.0 -- and nothing failed, because no check
compared an artifact's self-declared version against the release it shipped in.

A consumer reading two different versions out of one tag has no way to decide
which is authoritative. So the version has exactly one source now, and
`tools/validate/validate.mjs` fails the build when any artifact disagrees
with it.
"""

import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def contract_version():
    """The version in package.json. Nothing else may define it."""
    with open(os.path.join(_ROOT, "package.json"), encoding="utf-8") as handle:
        return json.load(handle)["version"]


CONTRACT_VERSION = contract_version()
