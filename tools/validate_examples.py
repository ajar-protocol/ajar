#!/usr/bin/env python3
"""Validate Ajar schemas and examples.

Requires the `jsonschema` package. CI installs it before running this script.
"""

from __future__ import annotations

import json
import hashlib
import copy
import sys
import warnings
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import re

try:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from jsonschema import Draft202012Validator, FormatChecker, RefResolver
except ModuleNotFoundError:
    print("Missing dependency: install jsonschema, then rerun tools/validate_examples.py", file=sys.stderr)
    sys.exit(2)


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"
TEST_VECTORS = ROOT / "test-vectors"

from signing_profile import b64url, canonical_json_bytes, ed25519_verify, public_key, signing_payload, unb64url
from scope_match import scope_allowed
from http_signature import sign_request, verify_request
from manifest_check import check_manifest


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


def apply_json_pointer_add(instance: dict, pointer: str, value: object) -> None:
    if not pointer.startswith("/"):
        raise ValueError(f"JSON pointer must start with /: {pointer}")
    target: object = instance
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.lstrip("/").split("/")]
    for part in parts[:-1]:
        if isinstance(target, list):
            target = target[int(part)]
        elif isinstance(target, dict):
            target = target[part]
        else:
            raise ValueError(f"Cannot descend into pointer segment {part!r}")
    leaf = parts[-1]
    if isinstance(target, list):
        target.insert(int(leaf), value)
    elif isinstance(target, dict):
        target[leaf] = value
    else:
        raise ValueError(f"Cannot set pointer leaf {leaf!r}")


def vector_instance(vector: dict) -> dict:
    instance = copy.deepcopy(load_json(ROOT / vector["input"]))
    for addition in vector.get("add", []):
        apply_json_pointer_add(instance, addition["path"], addition["value"])
    return instance


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


def semantic_failure(case: dict, instance: dict, base_dir: Path) -> bool:
    rule = case.get("rule")
    if rule == "offer-expired-at-issue":
        return parse_dt(instance["expires_at"]) <= parse_dt(instance["issued_at"])

    if rule == "offer-exceeds-mandate-cap":
        mandate_path = case.get("mandate", case.get("context", {}).get("mandate"))
        mandate = load_json(base_dir / mandate_path)
        currency = instance["total_cost"]["currency"]
        amount = Decimal(instance["total_cost"]["amount"])
        cap = Decimal(str(mandate["caps"]["per_tx"][currency]))
        return amount > cap

    if rule == "manifest-sequence-rollback":
        last_seen = case.get("last_seen_sequence", case.get("state", {}).get("last_seen_sequence"))
        return int(instance["sequence"]) < int(last_seen)

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
            if not semantic_failure(case, instance, EXAMPLES / "invalid"):
                failures.append(f"{case['id']} did not trigger semantic rule {case['rule']}")
            continue

        failures.append(f"{case['id']} has unknown expected value {case['expected']}")

    return failures


def validate_crypto_vectors() -> list[str]:
    failures: list[str] = []
    path = TEST_VECTORS / "crypto-signing.json"
    vectors = load_json(path)

    for vector in vectors["vectors"]:
        artifact = load_json(ROOT / vector["artifact"])
        payload = signing_payload(artifact, vector["artifact_type"])
        canonical = canonical_json_bytes(payload)
        seed = bytes.fromhex(vector["seed_hex"])
        public = public_key(seed)
        signature = unb64url(vector["signature_b64url"])

        if canonical.decode("utf-8") != vector["canonical_utf8"]:
            failures.append(f"{vector['id']} canonical bytes changed")
        if hashlib.sha256(canonical).hexdigest() != vector["canonical_sha256"]:
            failures.append(f"{vector['id']} canonical sha256 changed")
        if b64url(public) != vector["public_key_b64url"]:
            failures.append(f"{vector['id']} public key changed")
        if not ed25519_verify(public, canonical, signature):
            failures.append(f"{vector['id']} signature did not verify")

    return failures


def validate_http_signature_vectors() -> list[str]:
    failures: list[str] = []
    vectors = load_json(TEST_VECTORS / "http-signature-vectors.json")["vectors"]
    error_registry = (ROOT / "registries" / "error-codes.md").read_text(encoding="utf-8")
    seen_ids: set[str] = set()

    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen_ids:
            failures.append(f"duplicate HTTP signature vector id: {vector_id}")
        seen_ids.add(vector_id)

        request = load_json(ROOT / vector["request"])
        request.update(vector.get("mutate", {}))

        if "seed_hex" in vector:
            generated = sign_request(
                request,
                bytes.fromhex(vector["seed_hex"]),
                vector["covered"],
                int(vector["created"]),
                vector["keyid"],
            )
            for field in ["public_key_b64url", "signature_input", "signature", "signature_b64url", "signature_base"]:
                if generated[field] != vector[field]:
                    failures.append(f"{vector_id} {field} changed")

        verified = verify_request(
            request,
            vector["public_key_b64url"],
            vector["signature_b64url"],
            vector["covered"],
            int(vector["created"]),
            vector["keyid"],
        )
        actual_verdict = "accept" if verified else "reject"
        expected = vector["expected"]
        if actual_verdict != expected["verdict"]:
            failures.append(f"{vector_id} expected {expected['verdict']} but got {actual_verdict}")
            continue

        if actual_verdict == "reject":
            error_code = expected.get("error_code")
            if not error_code:
                failures.append(f"{vector_id} reject vector is missing error_code")
            elif error_code not in error_registry:
                failures.append(f"{vector_id} references unknown error code: {error_code}")

    return failures


def validate_extension_vectors() -> list[str]:
    failures: list[str] = []
    vectors = load_json(TEST_VECTORS / "extension-vectors.json")["vectors"]
    store = load_schemas()
    seen_ids: set[str] = set()

    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen_ids:
            failures.append(f"duplicate extension vector id: {vector_id}")
        seen_ids.add(vector_id)

        instance = vector_instance(vector)
        errors = collect_errors(validator_for(vector["schema"], store), instance)
        verdict = "reject" if errors else "accept"
        if verdict != vector["expected"]["verdict"]:
            detail = "\n  " + "\n  ".join(errors) if errors else ""
            failures.append(f"{vector_id} expected {vector['expected']['verdict']} but got {verdict}{detail}")

    return failures


def validate_manifest_check_vectors() -> list[str]:
    failures: list[str] = []
    vectors = load_json(TEST_VECTORS / "manifest-check-vectors.json")["vectors"]
    seen_ids: set[str] = set()

    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen_ids:
            failures.append(f"duplicate manifest check vector id: {vector_id}")
        seen_ids.add(vector_id)

        result = check_manifest(ROOT / vector["manifest"], vector.get("served_path"))
        expected = vector["expected"]
        if result["valid"] != expected["valid"]:
            failures.append(f"{vector_id} expected valid={expected['valid']} but got valid={result['valid']}")
            continue
        contains = expected.get("contains")
        if contains:
            haystack = "\n".join(result["schema_errors"] + result["semantic_errors"])
            if contains not in haystack:
                failures.append(f"{vector_id} expected error containing {contains!r}")

    return failures


def validate_core_vectors() -> list[str]:
    failures: list[str] = []
    vectors = load_json(TEST_VECTORS / "core-vectors.json")["vectors"]
    invalid_cases = {case["error_code"] for case in load_json(EXAMPLES / "invalid" / "index.json")["cases"]}
    error_registry = (ROOT / "registries" / "error-codes.md").read_text(encoding="utf-8")
    store = load_schemas()
    seen_ids: set[str] = set()

    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen_ids:
            failures.append(f"duplicate core vector id: {vector_id}")
        seen_ids.add(vector_id)

        input_path = (TEST_VECTORS / vector["input"]).resolve()
        if not input_path.exists():
            failures.append(f"{vector_id} input does not exist: {vector['input']}")
            continue

        for context_path in vector.get("context", {}).values():
            resolved = (TEST_VECTORS / context_path).resolve()
            if not resolved.exists():
                failures.append(f"{vector_id} context path does not exist: {context_path}")

        verdict = vector["expected"].get("verdict")
        if verdict not in {"accept", "reject"}:
            failures.append(f"{vector_id} has invalid verdict: {verdict}")

        error_code = vector["expected"].get("error_code")
        if verdict == "reject":
            if not error_code:
                failures.append(f"{vector_id} reject vector is missing error_code")
            elif error_code not in invalid_cases and error_code not in error_registry:
                failures.append(f"{vector_id} references unknown error code: {error_code}")

        if "schema" not in vector:
            failures.append(f"{vector_id} is missing schema")
            continue

        instance = load_json(input_path)
        schema_errors = collect_errors(validator_for(vector["schema"], store), instance)
        rule = vector.get("rule")

        if verdict == "accept":
            if schema_errors:
                failures.append(f"{vector_id} expected accept but schema failed:\n  " + "\n  ".join(schema_errors))
            elif rule and semantic_failure(vector, instance, TEST_VECTORS):
                failures.append(f"{vector_id} expected accept but semantic rule failed: {rule}")
            continue

        if rule == "schema-fail":
            if not schema_errors:
                failures.append(f"{vector_id} expected schema failure but schema passed")
            continue

        if schema_errors:
            failures.append(f"{vector_id} expected semantic rejection but schema failed first:\n  " + "\n  ".join(schema_errors))
            continue

        if rule:
            if not semantic_failure(vector, instance, TEST_VECTORS):
                failures.append(f"{vector_id} did not trigger semantic rule: {rule}")
        else:
            failures.append(f"{vector_id} reject vector is missing rule")

    return failures


def validate_must_coverage() -> list[str]:
    failures: list[str] = []
    core_ids = {vector["id"] for vector in load_json(TEST_VECTORS / "core-vectors.json")["vectors"]}
    runtime_ids = {vector["id"] for vector in load_json(TEST_VECTORS / "runtime-vectors.json")["vectors"]}
    scope_ids = {vector["id"] for vector in load_json(TEST_VECTORS / "scope-vectors.json")["vectors"]}
    http_ids = {vector["id"] for vector in load_json(TEST_VECTORS / "http-signature-vectors.json")["vectors"]}
    extension_ids = {vector["id"] for vector in load_json(TEST_VECTORS / "extension-vectors.json")["vectors"]}
    manifest_check_ids = {vector["id"] for vector in load_json(TEST_VECTORS / "manifest-check-vectors.json")["vectors"]}
    vector_ids = core_ids | runtime_ids | scope_ids | http_ids | extension_ids | manifest_check_ids
    text = (TEST_VECTORS / "must-coverage.md").read_text(encoding="utf-8")
    for token in re.findall(r"`([^`]+)`", text):
        if token.startswith("/") or token.endswith(".json"):
            continue
        if "/" in token:
            continue
        if ":" in token or " " in token:
            continue
        if token.startswith("http") or token.startswith("Idempotency-Key"):
            continue
        if "<" in token or ">" in token:
            continue
        if token not in vector_ids:
            failures.append(f"must-coverage.md references unknown vector id: {token}")
    return failures


def validate_scope_vectors() -> list[str]:
    failures: list[str] = []
    vectors = load_json(TEST_VECTORS / "scope-vectors.json")["vectors"]
    seen_ids: set[str] = set()

    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen_ids:
            failures.append(f"duplicate scope vector id: {vector_id}")
        seen_ids.add(vector_id)

        actual = "allow" if scope_allowed(
            vector["mandate_scopes"],
            vector["required_scope"],
            vector.get("forbidden", []),
        ) else "deny"
        if actual != vector["expected"]:
            failures.append(f"{vector_id} expected {vector['expected']} but got {actual}")

    return failures


def runtime_verdict(vector: dict) -> tuple[str, str | None]:
    kind = vector["kind"]
    data = vector["input"]

    if kind == "http_surface":
        if data["method"] == "GET" and data["path"] == "/.well-known/ajar.json" and data["serves_manifest"]:
            return "accept", None
        return "reject", "AJAR-POLICY-DENIED"

    if kind == "client_action_sequence":
        if data["attempted_mode"] == "propose" and data["action_risk"] in {"R2", "R3"} and not data["prior_simulation"]:
            return "reject", "AJAR-SIMULATE-REQUIRED"
        return "accept", None

    if kind == "view_provenance":
        view = load_json(ROOT / data["view"])
        chunk_ids = {chunk["id"] for chunk in view["chunks"]}
        for chunk in data["chunks"]:
            if chunk["id"] not in chunk_ids:
                return "reject", "AJAR-CLIENT-PROVENANCE"
            if chunk["origin"] != data["origin"] or not chunk["inert"]:
                return "reject", "AJAR-CLIENT-PROVENANCE"
        return "accept", None

    if kind == "fallback_operation":
        if (
            not data["manifest_present"]
            and data["derived_operation_risk"] in {"R2", "R3"}
            and not data["human_confirmation"]
        ):
            return "reject", "AJAR-FALLBACK-HUMAN-REQUIRED"
        return "accept", None

    raise ValueError(f"Unknown runtime vector kind: {kind}")


def validate_runtime_vectors() -> list[str]:
    failures: list[str] = []
    vectors = load_json(TEST_VECTORS / "runtime-vectors.json")["vectors"]
    error_registry = (ROOT / "registries" / "error-codes.md").read_text(encoding="utf-8")
    seen_ids: set[str] = set()

    for vector in vectors:
        vector_id = vector["id"]
        if vector_id in seen_ids:
            failures.append(f"duplicate runtime vector id: {vector_id}")
        seen_ids.add(vector_id)

        actual_verdict, actual_error = runtime_verdict(vector)
        expected = vector["expected"]
        if actual_verdict != expected["verdict"]:
            failures.append(f"{vector_id} expected {expected['verdict']} but got {actual_verdict}")
            continue

        expected_error = expected.get("error_code")
        if actual_verdict == "reject":
            if not expected_error:
                failures.append(f"{vector_id} reject vector is missing error_code")
            elif expected_error != actual_error:
                failures.append(f"{vector_id} expected {expected_error} but got {actual_error}")
            elif expected_error not in error_registry:
                failures.append(f"{vector_id} references unknown error code: {expected_error}")

    return failures


def main() -> int:
    store = load_schemas()
    failures = (
        validate_valid_examples(store)
        + validate_invalid_examples(store)
        + validate_crypto_vectors()
        + validate_http_signature_vectors()
        + validate_extension_vectors()
        + validate_manifest_check_vectors()
        + validate_core_vectors()
        + validate_runtime_vectors()
        + validate_scope_vectors()
        + validate_must_coverage()
    )
    if failures:
        print("Ajar example validation failed:\n", file=sys.stderr)
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    valid_count = sum(len(paths) for paths in VALID_EXAMPLES.values())
    invalid_count = len(load_json(EXAMPLES / "invalid" / "index.json")["cases"])
    crypto_count = len(load_json(TEST_VECTORS / "crypto-signing.json")["vectors"])
    http_count = len(load_json(TEST_VECTORS / "http-signature-vectors.json")["vectors"])
    extension_count = len(load_json(TEST_VECTORS / "extension-vectors.json")["vectors"])
    manifest_check_count = len(load_json(TEST_VECTORS / "manifest-check-vectors.json")["vectors"])
    core_count = len(load_json(TEST_VECTORS / "core-vectors.json")["vectors"])
    runtime_count = len(load_json(TEST_VECTORS / "runtime-vectors.json")["vectors"])
    scope_count = len(load_json(TEST_VECTORS / "scope-vectors.json")["vectors"])
    print(
        f"Validated {valid_count} valid examples, {invalid_count} invalid examples, "
        f"{crypto_count} signing vectors, {http_count} HTTP signature vectors, "
        f"{extension_count} extension vectors, {manifest_check_count} manifest check vectors, {core_count} core vectors, "
        f"{runtime_count} runtime vectors, and {scope_count} scope vectors."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
