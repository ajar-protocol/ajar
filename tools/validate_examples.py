#!/usr/bin/env python3
"""Validate Ajar schemas and examples.

Requires the `jsonschema` package. CI installs it before running this script.
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime
from decimal import Decimal
from pathlib import Path

try:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from jsonschema import Draft202012Validator, FormatChecker, RefResolver
except ModuleNotFoundError:
    print("Missing dependency: install jsonschema, then rerun tools/validate_examples.py", file=sys.stderr)
    sys.exit(2)


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"


VALID_EXAMPLES = {
    "manifest.schema.json": [
        "manifests/blog-core.json",
        "manifests/docs-core-pay.json",
        "manifests/commerce-core-act-pay.json",
    ],
    "view.schema.json": ["views/blog-home.view.json"],
    "policy.schema.json": ["policies/default-owner-policy.json"],
    "error.schema.json": ["errors/mandate-cap.problem.json"],
    "mandate.schema.json": ["scenario-tickets/mandate.json"],
    "simulation.schema.json": ["scenario-tickets/simulation.json"],
    "offer.schema.json": ["scenario-tickets/offer.json"],
    "receipt.schema.json": ["scenario-tickets/receipt.json"],
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_schemas() -> dict[str, dict]:
    store: dict[str, dict] = {}
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        schema = load_json(path)
        store[path.name] = schema
        if "$id" in schema:
            store[schema["$id"]] = schema
    return store


def validator_for(schema_name: str, store: dict[str, dict]) -> Draft202012Validator:
    schema = store[schema_name]
    resolver = RefResolver.from_schema(schema, store=store)
    return Draft202012Validator(schema, resolver=resolver, format_checker=FormatChecker())


def collect_errors(validator: Draft202012Validator, instance: dict) -> list[str]:
    errors = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def semantic_failure(case: dict, instance: dict) -> bool:
    rule = case.get("rule")
    if rule == "offer-expired-at-issue":
        return parse_dt(instance["expires_at"]) <= parse_dt(instance["issued_at"])

    if rule == "offer-exceeds-mandate-cap":
        mandate = load_json(EXAMPLES / "invalid" / case["mandate"])
        currency = instance["total_cost"]["currency"]
        amount = Decimal(instance["total_cost"]["amount"])
        cap = Decimal(str(mandate["caps"]["per_tx"][currency]))
        return amount > cap

    if rule == "manifest-sequence-rollback":
        return int(instance["sequence"]) < int(case["last_seen_sequence"])

    raise ValueError(f"Unknown invalid semantic rule: {rule}")


def validate_valid_examples(store: dict[str, dict]) -> list[str]:
    failures: list[str] = []
    for schema_name, rel_paths in VALID_EXAMPLES.items():
        validator = validator_for(schema_name, store)
        for rel_path in rel_paths:
            instance = load_json(EXAMPLES / rel_path)
            errors = collect_errors(validator, instance)
            if errors:
                failures.append(f"{rel_path} failed {schema_name}:\n  " + "\n  ".join(errors))
    return failures


def validate_invalid_examples(store: dict[str, dict]) -> list[str]:
    failures: list[str] = []
    index = load_json(EXAMPLES / "invalid" / "index.json")

    for case in index["cases"]:
        instance = load_json(EXAMPLES / "invalid" / case["path"])
        validator = validator_for(case["schema"], store)
        errors = collect_errors(validator, instance)

        if case["expected"] == "schema-fail":
            if not errors:
                failures.append(f"{case['id']} should fail schema validation with {case['error_code']}")
            continue

        if errors:
            failures.append(f"{case['id']} should pass schema before semantic check:\n  " + "\n  ".join(errors))
            continue

        if case["expected"] == "semantic-fail":
            if not semantic_failure(case, instance):
                failures.append(f"{case['id']} did not trigger semantic rule {case['rule']}")
            continue

        failures.append(f"{case['id']} has unknown expected value {case['expected']}")

    return failures


def main() -> int:
    store = load_schemas()
    failures = validate_valid_examples(store) + validate_invalid_examples(store)
    if failures:
        print("Ajar example validation failed:\n", file=sys.stderr)
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    valid_count = sum(len(paths) for paths in VALID_EXAMPLES.values())
    invalid_count = len(load_json(EXAMPLES / "invalid" / "index.json")["cases"])
    print(f"Validated {valid_count} valid examples and {invalid_count} invalid examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
