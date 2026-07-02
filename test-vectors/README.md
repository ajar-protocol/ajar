# /test-vectors

Executable seed conformance-vector data for the v0.1 draft.

These files document expected verdicts and spec clauses. `make validate`
executes the static and runtime vectors that can be checked inside this repo.
The future `conformance` repo can reuse the same vector ids and expected
verdicts when it adds implementation-facing network tests.

Files:

- `core-vectors.json` — manifest, offer, mandate, and receipt verdict examples
- `crypto-signing.json` — worked canonicalization and Ed25519 signing vectors
- `extension-vectors.json` — version/extension policy schema vectors
- `http-signature-vectors.json` — agent HTTP request signature vectors
- `http-request.json` — canonical request fixture used by HTTP signature vectors
- `manifest-check-vectors.json` — implementer-facing manifest checklist vectors
- `runtime-vectors.json` — executable decision vectors for HTTP surface, client sequencing, and fallback rules
- `scope-vectors.json` — executable mandate-scope matching and deny-override vectors
- `must-coverage.md` — initial mapping from normative MUSTs to vectors
