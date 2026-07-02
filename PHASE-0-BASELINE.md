# Phase 0 Baseline

This file records the local evidence for the v0.1 draft specification baseline.

## Evidence

- Normative draft: `docs/03-PROTOCOL-SPEC.md`
- Architecture review material: `docs/02-ARCHITECTURE.md`, `docs/04-SECURITY-MODEL.md`
- ADRs: `DECISIONS.md`
- Schemas: `schemas/*.schema.json`
- Registries: `registries/scopes.md`, `registries/error-codes.md`, `registries/settlement-adapters.md`
- Examples: `examples/`
- Executable seed vectors: `test-vectors/`
- Local validation: `make validate`
- Phase 0 readiness: `python3 tools/check_phase0.py`

## Current Validation Summary

`make validate` must report:

```text
Validated 10 valid examples, 5 invalid examples, 4 signing vectors, 2 HTTP signature vectors, 5 extension vectors, 4 manifest check vectors, 10 core vectors, 8 runtime vectors, and 10 scope vectors.
Markdown links OK.
Markdown hygiene OK.
```

`python3 tools/check_phase0.py` must report:

```text
Phase 0 readiness OK.
```

## External Dependency

The hosted workflow file is not active yet because the current publishing token
does not have workflow permission. The workflow template is present at
`ci/validate.yml` and runs the same local checks.

## Phase 0 Scope Boundary

This baseline finalizes the spec repo artifacts that can be verified locally.
The standalone implementation-facing conformance harness belongs in the future
`conformance` repo and should reuse the vector ids in `test-vectors/`.
