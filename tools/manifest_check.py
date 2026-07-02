#!/usr/bin/env python3
"""Validate an Ajar Capability Manifest for implementers."""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

try:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from jsonschema import Draft202012Validator, FormatChecker, RefResolver
except ModuleNotFoundError:
    print("Missing dependency: install jsonschema, then rerun tools/manifest_check.py", file=sys.stderr)
    sys.exit(2)


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
MAX_MANIFEST_DAYS = 180


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schemas() -> dict[str, dict]:
    store: dict[str, dict] = {}
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        schema = load_json(path)
        store[path.name] = schema
        if "$id" in schema:
            store[schema["$id"]] = schema
    return store


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_errors(manifest: dict) -> list[str]:
    store = load_schemas()
    schema = store["manifest.schema.json"]
    resolver = RefResolver.from_schema(schema, store=store)
    validator = Draft202012Validator(schema, resolver=resolver, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors


def semantic_errors(manifest: dict, served_path: str | None) -> list[str]:
    errors: list[str] = []

    if served_path is not None and served_path != "/.well-known/ajar.json":
        errors.append("AJAR-POLICY-DENIED: manifest must be served at /.well-known/ajar.json")

    version = manifest.get("ajar_version")
    if version and version not in manifest.get("supported_versions", []):
        errors.append("AJAR-VERSION-UNSUPPORTED: ajar_version must appear in supported_versions")

    profiles = set(manifest.get("profiles", []))
    if "CORE" not in profiles:
        errors.append("AJAR-MANIFEST-PROFILE: manifests should include CORE for readable Views")
    if "ACT" in profiles and not manifest.get("actions"):
        errors.append("AJAR-MANIFEST-PROFILE: ACT profile requires at least one Action")
    if "PAY" in profiles and "metering" not in manifest:
        errors.append("AJAR-MANIFEST-PROFILE: PAY profile requires metering")
    if "FED" in profiles and "federation" not in manifest:
        errors.append("AJAR-MANIFEST-PROFILE: FED profile requires federation")

    try:
        issued = parse_dt(manifest["issued_at"])
        expires = parse_dt(manifest["expires_at"])
        if expires <= issued:
            errors.append("AJAR-VERIFY-EXPIRED: expires_at must be after issued_at")
        if (expires - issued).days > MAX_MANIFEST_DAYS:
            errors.append("AJAR-VERIFY-EXPIRED: manifest lifetime must not exceed 180 days")
    except KeyError:
        pass

    action_ids = [action.get("id") for action in manifest.get("actions", [])]
    duplicates = sorted({action_id for action_id in action_ids if action_id and action_ids.count(action_id) > 1})
    for action_id in duplicates:
        errors.append(f"AJAR-ACTION-DUPLICATE: duplicate action id {action_id}")

    return errors


def check_manifest(path: Path, served_path: str | None = None) -> dict:
    manifest = load_json(path)
    schema = schema_errors(manifest)
    semantic = [] if schema else semantic_errors(manifest, served_path)
    return {
        "path": str(path),
        "valid": not schema and not semantic,
        "schema_errors": schema,
        "semantic_errors": semantic,
    }


def command_check(args: argparse.Namespace) -> int:
    result = check_manifest(args.manifest, args.served_path)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("manifest-ok")
    else:
        print("manifest-failed", file=sys.stderr)
        for error in result["schema_errors"] + result["semantic_errors"]:
            print(error, file=sys.stderr)
    return 0 if result["valid"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check an Ajar Capability Manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--served-path")
    parser.add_argument("--json", action="store_true")
    parser.set_defaults(func=command_check)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
