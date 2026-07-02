# /examples

Golden examples — the living documentation of Ajar objects.

These examples are validated by `tools/validate_examples.py`. Valid examples
MUST pass their schemas. Invalid examples MUST fail for the documented rule in
`examples/invalid/index.json`.

Contents:

- `manifests/` — blog CORE, docs CORE+PAY, commerce CORE+ACT+PAY
- `views/` — signed semantic View example
- `policies/` — owner policy example
- `errors/` — RFC 9457 problem example
- `scenario-tickets/` — mandate, simulation, offer, and receipt for the canonical 50-ticket purchase
- `invalid/` — deliberately broken artifacts with expected `Ajar-Error-Code`

The signature values are deterministic placeholders for schema and semantic
validation. Cryptographic signing vectors are tracked separately from these
shape examples.
