#!/usr/bin/env python3
"""Check Phase 0 baseline evidence for the spec repo."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCHEMAS = {
    "manifest.schema.json",
    "view.schema.json",
    "action.schema.json",
    "mandate.schema.json",
    "offer.schema.json",
    "receipt.schema.json",
    "policy.schema.json",
    "error.schema.json",
    "simulation.schema.json",
}

REQUIRED_REGISTRIES = {
    "scopes.md",
    "error-codes.md",
    "settlement-adapters.md",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(command: list[str]) -> str:
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def check_required_files(failures: list[str]) -> None:
    schemas = {path.name for path in (ROOT / "schemas").glob("*.schema.json")}
    missing_schemas = sorted(REQUIRED_SCHEMAS - schemas)
    if missing_schemas:
        failures.append(f"missing schemas: {', '.join(missing_schemas)}")

    registries = {path.name for path in (ROOT / "registries").glob("*")}
    missing_registries = sorted(REQUIRED_REGISTRIES - registries)
    if missing_registries:
        failures.append(f"missing registries: {', '.join(missing_registries)}")

    required_paths = [
        "examples/manifests/blog-core.json",
        "examples/manifests/docs-core-pay.json",
        "examples/manifests/commerce-core-act-pay.json",
        "examples/implementer-manifests/static-knowledge-base.json",
        "examples/implementer-manifests/service-desk-act.json",
        "examples/scenario-tickets/mandate.json",
        "examples/scenario-tickets/offer.json",
        "examples/scenario-tickets/receipt.json",
        "examples/invalid/index.json",
        "test-vectors/must-coverage.md",
        "PHASE-0-REVIEW.md",
        "CONTRIBUTING.md",
        ".github/workflows/validate.yml",
        "ci/validate.yml",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "LICENSE.md",
        "LICENSE-APACHE-2.0.txt",
        "LICENSE-CC-BY-4.0.txt",
    ]
    for rel_path in required_paths:
        if not (ROOT / rel_path).exists():
            failures.append(f"missing required path: {rel_path}")


def check_adr_closure(failures: list[str]) -> None:
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    proposed = re.findall(r"^## ADR-\d+.*?\n\*\*Status:\*\* proposed\b", decisions, re.MULTILINE)
    if proposed:
        failures.append("one or more ADRs remain proposed")


def check_scope_registry(failures: list[str]) -> None:
    scopes = (ROOT / "registries" / "scopes.md").read_text(encoding="utf-8")
    concrete_scopes = re.findall(r"^\| `(content|commerce|communication|account|data)\.[^`]+` \|", scopes, re.MULTILINE)
    if len(concrete_scopes) < 20:
        failures.append(f"scope registry has {len(concrete_scopes)} concrete scopes; expected at least 20")


def check_examples_and_vectors(failures: list[str]) -> None:
    invalid_cases = load_json(ROOT / "examples" / "invalid" / "index.json")["cases"]
    if len(invalid_cases) < 5:
        failures.append("expected at least 5 invalid examples")

    vector_files = [
        "core-vectors.json",
        "crypto-signing.json",
        "extension-vectors.json",
        "http-signature-vectors.json",
        "manifest-check-vectors.json",
        "must-coverage.json",
        "runtime-vectors.json",
        "scope-vectors.json",
    ]
    for filename in vector_files:
        path = ROOT / "test-vectors" / filename
        if not path.exists():
            failures.append(f"missing vector file: {filename}")
            continue
        data = load_json(path)
        entries = data.get("vectors", data.get("requirements", []))
        if not entries:
            failures.append(f"vector file has no vectors: {filename}")

    coverage = (ROOT / "test-vectors" / "must-coverage.md").read_text(encoding="utf-8")
    if "harness follow-up" in coverage:
        failures.append("MUST coverage still contains harness follow-up entries")


def check_local_validation(failures: list[str]) -> None:
    try:
        output = run(["make", "validate"])
    except subprocess.CalledProcessError as exc:
        failures.append(f"make validate failed:\n{exc.stdout}\n{exc.stderr}")
        return
    expected = "Validated 12 valid examples, 6 invalid examples, 4 signing vectors, 2 HTTP signature vectors, 5 extension vectors, 5 manifest check vectors, 10 core vectors, 18 runtime vectors, and 10 scope vectors."
    if expected not in output:
        failures.append("make validate output did not include expected vector summary")
    if "MUST coverage OK: 21 requirements mapped." not in output:
        failures.append("make validate output did not include expected MUST coverage summary")


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    check_adr_closure(failures)
    check_scope_registry(failures)
    check_examples_and_vectors(failures)
    check_local_validation(failures)

    if failures:
        print("Phase 0 readiness check failed:\n", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("Phase 0 readiness OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
