#!/usr/bin/env python3
"""Check machine-readable MUST coverage against the current spec."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "03-PROTOCOL-SPEC.md"
COVERAGE = ROOT / "test-vectors" / "must-coverage.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normative_must_lines() -> list[str]:
    lines = []
    for line in SPEC.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if "MUST" not in stripped:
            continue
        if "Normative keywords" in stripped:
            continue
        lines.append(stripped)
    return lines


def vector_ids() -> set[str]:
    ids: set[str] = set()
    for path in (ROOT / "test-vectors").glob("*.json"):
        data = load_json(path)
        for vector in data.get("vectors", []):
            if "id" in vector:
                ids.add(vector["id"])
    return ids


def main() -> int:
    failures = []
    coverage = load_json(COVERAGE)
    covered_lines = [entry["source_text"] for entry in coverage["requirements"]]
    known_vectors = vector_ids()

    for line in normative_must_lines():
        if line not in covered_lines:
            failures.append(f"uncovered MUST: {line}")

    for entry in coverage["requirements"]:
        if entry["source_text"] not in normative_must_lines():
            failures.append(f"coverage source not found in spec: {entry['id']}")
        if not entry.get("vectors"):
            failures.append(f"coverage entry has no vectors: {entry['id']}")
        for vector_id in entry.get("vectors", []):
            if vector_id not in known_vectors:
                failures.append(f"coverage entry {entry['id']} references unknown vector: {vector_id}")

    duplicate_ids = [
        item for item in {entry["id"] for entry in coverage["requirements"]}
        if [entry["id"] for entry in coverage["requirements"]].count(item) > 1
    ]
    for duplicate_id in sorted(duplicate_ids):
        failures.append(f"duplicate coverage id: {duplicate_id}")

    if failures:
        print("MUST coverage check failed:\n", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"MUST coverage OK: {len(coverage['requirements'])} requirements mapped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
