#!/usr/bin/env python3
"""Small Markdown hygiene checks for repository docs."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        if path.name == "LICENSE.md":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            failures.append(f"{path.relative_to(ROOT)}: empty markdown file")
            continue
        if not lines[0].startswith("#"):
            failures.append(f"{path.relative_to(ROOT)}: first line should be a heading")
        for index, line in enumerate(lines, start=1):
            if line.rstrip() != line:
                failures.append(f"{path.relative_to(ROOT)}:{index}: trailing whitespace")
            if "\t" in line:
                failures.append(f"{path.relative_to(ROOT)}:{index}: tab character")

    if failures:
        print("Markdown hygiene check failed:\n", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("Markdown hygiene OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
