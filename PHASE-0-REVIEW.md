# Phase 0 Review Report

This report maps the planning Phase 0 tasks to the current `ajar` repo evidence.
It is a readiness report for the initial v0.1 draft baseline, not a claim that
the formal Phase 0 exit gate has closed.

## Summary

Local repository readiness is green. The spec repo contains the normative draft,
schemas, examples, registries, seed vectors, local validation tooling, project
templates, licenses, security policy, conduct policy, and contribution rules.

Formal Phase 0 exit still requires two non-local proofs:

- hosted validation must run on GitHub main
  ([issue #1](https://github.com/ajar-protocol/ajar/issues/1))
- two independent readers must hand-write valid manifests from the spec alone,
  and those manifests must validate
  ([issue #2](https://github.com/ajar-protocol/ajar/issues/2))

The final ambiguity pass is tracked separately because it can produce either
blocking fixes or documented deferrals
([issue #3](https://github.com/ajar-protocol/ajar/issues/3)).

## Task Evidence

| Task | Evidence | Status |
|---|---|---|
| T0.1 spec review pass | `docs/03-PROTOCOL-SPEC.md`, `docs/02-ARCHITECTURE.md`, `docs/04-SECURITY-MODEL.md`, open questions below | Baseline reviewed; independent issue pass still needed before final freeze |
| T0.2 canonicalization and signatures | `docs/03-PROTOCOL-SPEC.md` section 2.4, `test-vectors/crypto-signing.json`, `tools/signing_profile.py` | Local evidence complete |
| T0.3 scope registry v1 | `registries/scopes.md`, `test-vectors/scope-vectors.json`, `tools/scope_match.py` | Local evidence complete |
| T0.4 JSON Schemas | `schemas/*.schema.json`, `examples/`, `tools/validate_examples.py`, `ci/validate.yml` | Local evidence complete; hosted workflow pending |
| T0.5 golden examples | `examples/manifests/`, `examples/scenario-tickets/`, `examples/invalid/index.json` | Local evidence complete |
| T0.6 error-code registry | `registries/error-codes.md`, `examples/errors/`, vector error-code references | Local evidence complete for current MUST-fail paths |
| T0.7 conformance vectors | `test-vectors/*.json`, `test-vectors/must-coverage.json`, `test-vectors/must-coverage.md` | Local evidence complete for seed vectors |
| T0.8 version and extension policy | `docs/03-PROTOCOL-SPEC.md` section 13, `test-vectors/extension-vectors.json`, `test-vectors/runtime-vectors.json` | Local evidence complete |
| T0.9 repo scaffolding and CI | `.github/`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `LICENSE.md`, `ci/validate.yml` | Local scaffolding complete; hosted workflow pending |
| T0.10 ADR closure | `DECISIONS.md` ADR-001 through ADR-017 accepted | Local evidence complete |

## Deferred Open Questions

These questions are intentionally tracked for AEPs, ADR updates, or later phase
work. None block the initial v0.1 draft baseline, but each must be resolved
before the affected surface is declared stable.

| ID | Question | Current handling |
|---|---|---|
| OQ-1 | Manifest size limits and sharding for very large sites | Keep manifests unsharded in v0.1 draft; revisit with large-site pilots |
| OQ-2 | Revocation transport shape | Keep mandate revocation endpoint plus log publication language; finalize with implementation feedback |
| OQ-3 | SIMULATE for uncertain outcomes | Keep zero-side-effect and faithful resolved-effect requirement; add probabilistic syntax only through AEP |
| OQ-4 | Privacy-preserving discovery | Keep Index discovery optional and untrusted; defer private query mechanisms |
| OQ-5 | Scope-registry governance | Use AEPs for v0.1 draft; define external registry governance before neutral transfer |

## Independent Reader Exercise

The repo includes implementer-style manifest fixtures in
`examples/implementer-manifests/`. They are useful preparation, but they do not
replace the Phase 0 exit exercise.

To close the gate:

1. Give two readers only `README.md`, `docs/03-PROTOCOL-SPEC.md`,
   `registries/scopes.md`, and `schemas/manifest.schema.json`.
2. Ask each reader to write a manifest without copying an existing example.
3. Add the resulting manifests under `examples/implementer-manifests/` with
   reviewer names or handles in the commit message or issue.
4. Run `make validate` and record the result in this file.

## Hosted Validation

The workflow template is present at `ci/validate.yml`. It should be copied to
`.github/workflows/validate.yml` once the publishing account has permission to
create or update GitHub Actions workflow files.

Until that is active, `make validate` and `make phase0` are the authoritative
local checks.
