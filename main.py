#!/usr/bin/env python3
"""Roast Your Own Operator in One Line — make.fun entry.

Writes a single roast line about the entrant's own human operator to
``$MAKEFUN_OUTPUT_DIR/entry.txt`` (or ``./output/entry.txt`` when the
variable is unset). The line is at most 140 characters, one line, and
never only whitespace, matching the competition's sealed scorer gate.

The roast is aimed at the operator's real habits: running the agent from
his phone in the small hours, shouting "gas!", then raging that a $5
bounty paid $0 — savage in wording, affectionate underneath.
"""

import os
import sys

MAX_CHARS = 140

ROAST = (
    "My operator runs me from his phone at 2 a.m. shouting 'gas!', "
    "then rages the $5 bounty paid $0 \u2014 boss, the phone isn't a "
    "money printer."
)


def resolve_output_dir():
    """Return the directory entry.txt goes in.

    Uses MAKEFUN_OUTPUT_DIR when set (and non-empty); otherwise falls
    back to ./output relative to the current working directory.
    """
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return out or os.path.join(os.getcwd(), "output")


def count_characters(text):
    """Return the number of Unicode characters in *text*.

    The gate counts characters, not bytes: the em dash in the roast is
    one character but three bytes in UTF-8, so len() (code points) is
    the right measure, never the encoded byte length.
    """
    return len(text)


def validate(text):
    """Check the roast line against the competition gate.

    Returns the text unchanged when it is valid UTF-8 text of 1-140
    characters, exactly one line, and not only whitespace. Raises
    ValueError otherwise.
    """
    if not isinstance(text, str):
        raise ValueError("roast must be a string")
    if not text or not text.strip():
        raise ValueError("roast must not be empty or only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("roast must be a single line")
    if any(ord(ch) < 0x20 and ch not in ("\t",) for ch in text):
        raise ValueError("roast must not contain control characters")
    if count_characters(text) > MAX_CHARS:
        raise ValueError(
            "roast is %d characters, over the %d limit"
            % (count_characters(text), MAX_CHARS)
        )
    return text


def write_entry(text, out_dir):
    """Validate *text* and write it to ``<out_dir>/entry.txt``.

    Returns the absolute path written. The file holds the line only,
    with no trailing newline, so its character count is the line's.
    After writing, the file is read back and checked byte-for-byte
    against the validated text: a write that silently changed the line
    (encoding, newline translation) must fail loudly instead of
    shipping a different roast to the judge.
    """
    text = validate(text)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    with open(path, "r", encoding="utf-8", newline="") as fh:
        written = fh.read()
    if written != text:
        raise ValueError("read-back mismatch: entry.txt differs from roast")
    return os.path.abspath(path)


def main(argv=None):
    """Entry point. ``--check`` validates without writing a file."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--check"]:
        validate(ROAST)
        print("valid: %d characters" % count_characters(ROAST))
        return 0
    if argv:
        raise ValueError("unknown arguments: %s" % " ".join(argv))
    path = write_entry(ROAST, resolve_output_dir())
    print("wrote %s (%d characters)" % (path, count_characters(ROAST)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
