#!/usr/bin/env python3
"""Ajar scope matching helper.

Implements `registries/scopes.md` for deterministic vector checks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CORE_PREFIXES = {"content", "commerce", "communication", "account", "data"}
SCOPE_RE = re.compile(r"^(content|commerce|communication|account|data|x-[a-z0-9-]+)(\.[a-z0-9_*:-]+)+$")


def is_valid_scope(scope: str) -> bool:
    if not SCOPE_RE.match(scope):
        return False
    if "*" not in scope:
        return True
    return scope.endswith(".*") and scope.count("*") == 1


def is_private_scope(scope: str) -> bool:
    return scope.startswith("x-")


def scope_matches(grant: str, required: str) -> bool:
    if not is_valid_scope(grant) or not is_valid_scope(required):
        return False
    if is_private_scope(grant) != is_private_scope(required):
        return False
    if grant == required:
        return True
    if grant.endswith(".*"):
        prefix = grant[:-2]
        return required.startswith(prefix + ".")
    return False


def scope_allowed(mandate_scopes: list[str], required_scope: str, forbidden: list[str] | None = None) -> bool:
    forbidden = forbidden or []
    if not is_valid_scope(required_scope):
        return False
    if any(scope_matches(deny, required_scope) for deny in forbidden):
        return False
    return any(scope_matches(grant, required_scope) for grant in mandate_scopes)


def command_match(args: argparse.Namespace) -> int:
    allowed = scope_allowed(args.grant, args.required, args.forbidden)
    print("allow" if allowed else "deny")
    return 0 if allowed else 1


def command_validate_vector(args: argparse.Namespace) -> int:
    failures = []
    payload = json.loads(args.path.read_text(encoding="utf-8"))
    seen = set()
    for vector in payload["vectors"]:
        vector_id = vector["id"]
        if vector_id in seen:
            failures.append(f"duplicate scope vector id: {vector_id}")
        seen.add(vector_id)
        actual = "allow" if scope_allowed(
            vector["mandate_scopes"],
            vector["required_scope"],
            vector.get("forbidden", []),
        ) else "deny"
        expected = vector["expected"]
        if actual != expected:
            failures.append(f"{vector_id} expected {expected} but got {actual}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Validated {len(payload['vectors'])} scope vectors.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Ajar mandate scopes")
    subcommands = parser.add_subparsers(dest="command", required=True)

    match = subcommands.add_parser("match")
    match.add_argument("--grant", action="append", required=True)
    match.add_argument("--forbidden", action="append", default=[])
    match.add_argument("required")
    match.set_defaults(func=command_match)

    validate = subcommands.add_parser("validate-vector")
    validate.add_argument("path", type=Path)
    validate.set_defaults(func=command_validate_vector)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
