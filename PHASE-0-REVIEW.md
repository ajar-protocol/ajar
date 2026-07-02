# Phase 0 Review Report

This report maps the planning Phase 0 tasks to the current `ajar` repo evidence.
All Phase 0 exit gates are closed as of 2026-07-02.

## Summary

Local repository readiness is green. The spec repo contains the normative draft,
schemas, examples, registries, seed vectors, local validation tooling, project
templates, licenses, security policy, conduct policy, and contribution rules.

The independent reader exercise ([issue #2](https://github.com/ajar-protocol/ajar/issues/2))
was completed on 2026-07-02, closing the last Phase 0 exit gate. Two
independent AI agents (permitted by the ROADMAP exit criterion "two
independent people (or agents)"), each given only `README.md`,
`docs/03-PROTOCOL-SPEC.md`, `registries/scopes.md`, and
`schemas/manifest.schema.json` — no examples — hand-wrote complete
manifests. Both validate with zero schema errors and pass
`tools/manifest_check.py`:

- Reader A (OpenAI Codex): `examples/implementer-manifests/mosskiln-reader-a.json`
  (CORE+ACT+PAY, three actions)
- Reader B (Anthropic Claude): `examples/implementer-manifests/thistledown-reader-b.json`
  (CORE+ACT+PAY, four actions, R0-R3 range)

Both readers also produced ambiguity notes; the actionable findings
(operational-key certification bytes undefined, missing FED schema
conditional, undefined idempotency and effect-type vocabularies, nested
extension-field policy) are tracked in
[issue #4](https://github.com/ajar-protocol/ajar/issues/4) for
post-baseline refinement. **Phase 0 is exited.**

Hosted validation is installed in `.github/workflows/validate.yml` and the
first main-branch run passed for commit `6d94400`
(https://github.com/ajar-protocol/ajar/actions/runs/28567156904).

The final ambiguity pass ([issue #3](https://github.com/ajar-protocol/ajar/issues/3))
was completed on 2026-07-02. It resolved cross-document contradictions
(client SIMULATE obligation, revocation fail-closed semantics, forbidden-scope
precedence, commit signature binding, extension-prefix conventions), pinned
down underspecified surfaces (segment-wise wildcard matching, per-chunk-ETag
view sync, simulation-divergence definition, the 180-day manifest lifetime
cap, `Ajar-Price` and `Ajar-Date` headers, mandate domain matching), aligned
the spec prose with the schemas (offer, simulation, and view envelopes;
operational key scopes), tightened the schemas (suffix-only wildcards, R2/R3
mandate-scope requirement, risk-floor-preserving policy enum), added the
`AJAR-SCHEMA-INVALID` and `AJAR-MANIFEST-LOCATION` error codes plus the
missing failure vectors, and reconciled the MUST-coverage table with honest
follow-up markers. One deferral was recorded as OQ-6 below.

## Task Evidence

| Task | Evidence | Status |
|---|---|---|
| T0.1 spec review pass | `docs/03-PROTOCOL-SPEC.md`, `docs/02-ARCHITECTURE.md`, `docs/04-SECURITY-MODEL.md`, open questions below | Baseline reviewed; ambiguity pass complete (issue #3) |
| T0.2 canonicalization and signatures | `docs/03-PROTOCOL-SPEC.md` section 2.4, `test-vectors/crypto-signing.json`, `tools/signing_profile.py` | Local evidence complete |
| T0.3 scope registry v1 | `registries/scopes.md`, `test-vectors/scope-vectors.json`, `tools/scope_match.py` | Local evidence complete |
| T0.4 JSON Schemas | `schemas/*.schema.json`, `examples/`, `tools/validate_examples.py`, `.github/workflows/validate.yml`, `ci/validate.yml` | Local and hosted validation green |
| T0.5 golden examples | `examples/manifests/`, `examples/scenario-tickets/`, `examples/invalid/index.json` | Local evidence complete |
| T0.6 error-code registry | `registries/error-codes.md`, `examples/errors/`, vector error-code references | Local evidence complete for current MUST-fail paths |
| T0.7 conformance vectors | `test-vectors/*.json`, `test-vectors/must-coverage.json`, `test-vectors/must-coverage.md` | Local evidence complete for seed vectors |
| T0.8 version and extension policy | `docs/03-PROTOCOL-SPEC.md` section 13, `test-vectors/extension-vectors.json`, `test-vectors/runtime-vectors.json` | Local evidence complete |
| T0.9 repo scaffolding and CI | `.github/`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `LICENSE.md`, `.github/workflows/validate.yml`, `ci/validate.yml` | Complete; hosted validation green |
| T0.10 ADR closure | `DECISIONS.md` ADR-001 through ADR-018 accepted | Local evidence complete |

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
| OQ-6 | Trust-list format, subscription, and verification semantics | Undefined in v0.1; defer `verified`-tier interop across Gateways |

## Independent Reader Exercise (completed 2026-07-02)

Protocol followed: each reader received only `README.md`,
`docs/03-PROTOCOL-SPEC.md`, `registries/scopes.md`, and
`schemas/manifest.schema.json` in an isolated directory, with no access to
examples or other schemas, and hand-wrote a manifest for a fictional site of
its own invention.

- Reader A: OpenAI Codex (codex-cli 0.142.5) — `examples/implementer-manifests/mosskiln-reader-a.json`
- Reader B: Anthropic Claude — `examples/implementer-manifests/thistledown-reader-b.json`

Recorded `make validate` result with both manifests included:

```text
Validated 14 valid examples, 8 invalid examples, 4 signing vectors, 2 HTTP signature vectors, 5 extension vectors, 6 manifest check vectors, 11 core vectors, 25 runtime vectors, and 12 scope vectors.
MUST coverage OK: 24 requirements mapped.
```

Both manifests also pass `tools/manifest_check.py` individually. Reader
ambiguity findings are tracked in
[issue #4](https://github.com/ajar-protocol/ajar/issues/4).

## Hosted Validation

Hosted validation is installed at `.github/workflows/validate.yml`; the
template copy remains at `ci/validate.yml`.

First green main-branch run:
https://github.com/ajar-protocol/ajar/actions/runs/28567156904
