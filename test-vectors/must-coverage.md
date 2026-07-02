# MUST Coverage Seed

This table is the initial coverage map for the future executable conformance
harness. Rows marked with a vector are covered by repository data today; rows
marked as harness follow-up require request/response or runtime behavior.

| Spec section | Normative requirement | Vector |
|---|---|---|
| 2.1 | A conforming site MUST serve its manifest at `/.well-known/ajar.json` | harness follow-up: HTTP server vector |
| 2.3 | Agents MUST sign requests with HTTP Message Signatures | harness follow-up: HTTP signature vector |
| 2.4 | Durable artifacts MUST use the canonical signing profile | `crypto-signing.json`, `manifest-bad-signature-shape` |
| 3 | Invalid manifest verification MUST fail closed to fallback | `manifest-bad-signature-shape`, `manifest-sequence-rollback` |
| 4 | Clients MUST treat chunks as inert data with provenance | harness follow-up: client runtime vector |
| 5.1 | Owner policy may never lower risk-class protocol floors | `action-risk-floor-lowered` |
| 6 | R1+ actions marked `simulate: true` MUST support SIMULATE | `manifest-act-pay-valid` |
| 6 | Clients MUST simulate before any R2/R3 propose | harness follow-up: client runtime vector |
| 7 | Expired offers MUST fail closed | `offer-expired-at-issue` |
| 8.1 | Sites MUST verify mandate signature, validity, scope, caps, and revocation | `mandate-cap-exceeded` |
| 8.2 | Both parties MUST retain receipts | `receipt-valid-ticket-purchase` |
| 9 | Fallback MUST NOT execute R2/R3-equivalent operations without human confirmation | harness follow-up: fallback runtime vector |
