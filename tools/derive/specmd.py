"""Shared markdown helpers for transcribing repository-spec appendices.

Every generator in this directory is a *transcription* tool: it reads a
sibling repository's specification and emits the machine-readable form.
Nothing here may add, drop or reinterpret a row — divergence from the
appendix is a bug in the generator, never a fix applied to the contract.
"""

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROGRAMME_ROOT = os.path.dirname(REPO_ROOT)

SPEC_PATHS = {
    "repo1": "karyalay-mail/docs/spec/repository-spec-v1.0.md",
    "repo2": "karyalay-webmail/docs/spec/repository-spec-v1.0.md",
    "repo3": "karyalay-mail-infra/docs/spec/repository-spec-v1.0.md",
    "repo4": "karyalay-mail-ops/docs/spec/repository-spec-v1.0.md",
}


def spec_root():
    """Where the four consumer repositories are checked out.

    Defaults to this repository's parent directory, which is the layout the
    programme uses. Override with SPEC_ROOT when checkouts live elsewhere.
    """
    return os.environ.get("SPEC_ROOT", PROGRAMME_ROOT)


def read_spec(repo):
    path = os.path.join(spec_root(), SPEC_PATHS[repo])
    if not os.path.exists(path):
        sys.exit(
            "missing source specification: %s\n"
            "Set SPEC_ROOT to the directory holding the four consumer repositories." % path
        )
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def section(text, heading):
    """Return the body of a heading, up to the next heading of equal or higher level."""
    pattern = re.compile(r"^(#{1,6})\s+%s\s*$" % re.escape(heading), re.MULTILINE)
    match = pattern.search(text)
    if not match:
        sys.exit("heading not found in specification: %s" % heading)
    level = len(match.group(1))
    tail = text[match.end():]
    nxt = re.search(r"^#{1,%d}\s+" % level, tail, re.MULTILINE)
    return tail[: nxt.start()] if nxt else tail


def tables(body):
    """Every pipe table in a markdown body, as a list of {header, rows}."""
    out = []
    current = None
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if current is None:
                current = {"header": [unmark(c) for c in cells], "rows": []}
            elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            else:
                current["rows"].append([unmark(c) for c in cells])
        else:
            if current is not None:
                out.append(current)
                current = None
    if current is not None:
        out.append(current)
    return [t for t in out if t["rows"]]


def table(body, index=0):
    found = tables(body)
    if len(found) <= index:
        sys.exit("expected at least %d table(s), found %d" % (index + 1, len(found)))
    return found[index]


def unmark(cell):
    """Strip the bold markers and escaped punctuation the specs use in tables."""
    cell = cell.replace("\\_", "_").replace("\\*", "*").replace("\\[", "[").replace("\\]", "]")
    cell = re.sub(r"^\*\*(.*)\*\*$", r"\1", cell.strip())
    cell = re.sub(r"&lt;", "<", cell)
    cell = re.sub(r"&gt;", ">", cell)
    return cell.strip()


def rows_as_dicts(tbl):
    return [dict(zip(tbl["header"], row)) for row in tbl["rows"]]


def write_json(path, payload):
    import json

    full = os.path.join(REPO_ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return full


def write_text(path, payload):
    full = os.path.join(REPO_ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(payload)
    return full


# --- deterministic YAML emission -------------------------------------------
# The programme has no runtime Python dependencies and the contract documents
# use a small, fixed subset of YAML (maps, sequences, strings, ints, bools,
# nulls). A local emitter keeps generation reproducible without pinning a
# third-party parser into the derivation path.

_PLAIN_SAFE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9 _./:#@+-]*$")
_YAML_RESERVED = {
    "y", "Y", "yes", "Yes", "YES", "n", "N", "no", "No", "NO",
    "true", "True", "TRUE", "false", "False", "FALSE",
    "on", "On", "ON", "off", "Off", "OFF", "null", "Null", "NULL", "~", "",
}


def _scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if (
        text in _YAML_RESERVED
        or not _PLAIN_SAFE.match(text)
        or text.endswith(":")
        or ": " in text          # YAML would read this as a nested mapping
        or " #" in text          # ...and this as a trailing comment
        or text != text.strip()
        or re.fullmatch(r"-?\d+(\.\d+)?", text)
    ):
        return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return text


def _emit(value, indent, out):
    pad = "  " * indent
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                out.append("%s%s:" % (pad, _scalar(key)))
                _emit(item, indent + 1, out)
            elif isinstance(item, (dict, list)):
                out.append("%s%s: %s" % (pad, _scalar(key), "{}" if isinstance(item, dict) else "[]"))
            else:
                out.append("%s%s: %s" % (pad, _scalar(key), _scalar(item)))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item:
                first = True
                nested = []
                _emit(item, indent + 1, nested)
                for line in nested:
                    if first:
                        out.append(pad + "- " + line.lstrip()[: 0] + line[len(pad) + 2:])
                        first = False
                    else:
                        out.append(line)
            elif isinstance(item, list) and item:
                out.append("%s-" % pad)
                _emit(item, indent + 1, out)
            else:
                out.append("%s- %s" % (pad, _scalar(item)))


def to_yaml(document, header_comment=None):
    out = []
    _emit(document, 0, out)
    body = "\n".join(out) + "\n"
    if header_comment:
        prefix = "".join("# %s\n" % line if line else "#\n" for line in header_comment.splitlines())
        return prefix + "\n" + body
    return body


def write_yaml(path, document, header_comment=None):
    return write_text(path, to_yaml(document, header_comment))
