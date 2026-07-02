# /test-vectors

Seed conformance-vector data for the v0.1 draft.

These files are data, not an executable harness. They document expected
verdicts and spec clauses so the future `conformance` repo can turn them into
tests without rediscovering coverage.

Files:

- `core-vectors.json` — manifest, offer, mandate, and receipt verdict examples
- `crypto-signing.json` — worked canonicalization and Ed25519 signing vectors
- `must-coverage.md` — initial mapping from normative MUSTs to vectors
