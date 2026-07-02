#!/usr/bin/env python3
"""Check local Markdown links.

External URLs are intentionally skipped; this script verifies only repository
paths and same-file anchors.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def slugify(heading: str) -> str:
    heading = re.sub(r"`([^`]*)`", r"\1", heading)
    heading = heading.strip().lower()
    heading = re.sub(r"[^a-z0-9\s-]", "", heading)
    heading = re.sub(r"\s+", "-", heading)
    return heading


def anchors_for(path: Path) -> set[str]:
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = slugify(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def is_external(target: str) -> bool:
    return (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
        or target.startswith("#")
    )


def check_link(source: Path, target: str) -> str | None:
    target = target.split()[0]
    if is_external(target):
        if target.startswith("#") and target[1:] not in anchors_for(source):
            return f"{source.relative_to(ROOT)}: missing anchor {target}"
        return None

    path_part, _, anchor = target.partition("#")
    candidate = (source.parent / path_part).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return f"{source.relative_to(ROOT)}: link escapes repo: {target}"

    if not candidate.exists():
        return f"{source.relative_to(ROOT)}: missing link target: {target}"

    if anchor:
        anchor_source = candidate if candidate.is_file() else candidate / "README.md"
        if not anchor_source.exists():
            return f"{source.relative_to(ROOT)}: anchor target is not a markdown file: {target}"
        if anchor not in anchors_for(anchor_source):
            return f"{source.relative_to(ROOT)}: missing anchor {anchor} in {anchor_source.relative_to(ROOT)}"

    return None


def main() -> int:
    failures = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            failure = check_link(path, match.group(1))
            if failure:
                failures.append(failure)

    if failures:
        print("Markdown link check failed:\n", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("Markdown links OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
