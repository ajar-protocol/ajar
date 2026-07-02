# /examples

Golden examples — the living documentation of Ajar objects.

These examples are validated by `tools/validate_examples.py`. Valid examples
MUST pass their schemas. Invalid examples MUST fail for the documented rule in
`examples/invalid/index.json`.

Contents:

- `manifests/` — blog CORE, docs CORE+PAY, commerce CORE+ACT+PAY
- `implementer-manifests/` — four valid manifests written as independent implementer-style fixtures, including the two Phase 0 reader-exercise manifests (mosskiln-reader-a, thistledown-reader-b)
- `views/` — signed semantic View example
- `policies/` — owner policy example
- `errors/` — RFC 9457 problem example
- `scenario-tickets/` — mandate, simulation, offer, and receipt for the canonical 50-ticket purchase
- `invalid/` — deliberately broken artifacts with expected `Ajar-Error-Code`

Most example signatures are deterministic stand-ins for schema and semantic
validation. Reproducible cryptographic vectors for Manifest, Mandate, Offer,
and Receipt signing live in `../test-vectors/crypto-signing.json`.
