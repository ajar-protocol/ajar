# Phase 0 Baseline

This file records the local evidence for the v0.1 draft specification baseline.

## Evidence

- Normative draft: `docs/03-PROTOCOL-SPEC.md`
- Architecture review material: `docs/02-ARCHITECTURE.md`, `docs/04-SECURITY-MODEL.md`
- ADRs: `DECISIONS.md`
- Schemas: `schemas/*.schema.json`
- Registries: `registries/scopes.md`, `registries/error-codes.md`, `registries/settlement-adapters.md`
- Examples: `examples/`
- Implementer-style manifest fixtures: `examples/implementer-manifests/`
- Executable seed vectors: `test-vectors/`
- Phase 0 task review: `PHASE-0-REVIEW.md`
- Contribution rules: `CONTRIBUTING.md`
- Local validation: `make validate`
- Phase 0 readiness: `python3 tools/check_phase0.py`
- Hosted validation: `.github/workflows/validate.yml`

## Current Validation Summary

`make validate` must report:

```text
Validated 12 valid examples, 6 invalid examples, 4 signing vectors, 2 HTTP signature vectors, 5 extension vectors, 5 manifest check vectors, 10 core vectors, 18 runtime vectors, and 10 scope vectors.
MUST coverage OK: 21 requirements mapped.
Markdown links OK.
Markdown hygiene OK.
```

`python3 tools/check_phase0.py` must report:

```text
Phase 0 readiness OK.
```

## Hosted Validation

The hosted validation workflow is present at `.github/workflows/validate.yml`.
The copy at `ci/validate.yml` is retained as a reviewable template and runs the
same checks.

## Phase 0 Scope Boundary

This baseline finalizes the spec repo artifacts that can be verified locally.
The standalone implementation-facing conformance harness belongs in the future
`conformance` repo and should reuse the vector ids in `test-vectors/`.
