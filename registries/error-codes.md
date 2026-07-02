# Error Code Registry v1

Normative source: `docs/03-PROTOCOL-SPEC.md` sections 2, 3, 6, 7, 8, and 10.

Ajar errors use RFC 9457 `application/problem+json` and include:

- `type`: stable URI for the class of error
- `title`: short human-readable label
- `status`: HTTP status
- `detail`: implementation-specific explanation
- `ajar_error_code`: stable code from this registry
- `spec_section`: optional spec pointer

Servers SHOULD also send the `Ajar-Error-Code` HTTP header with the same value.

Most codes are returned by Sites in Problem responses and the `Ajar-Error-Code`
header. Some codes are emitted by the client Kernel in local logs/receipts and
never appear on the wire from a site; version/extension negotiation codes may be
emitted by either side.

| Code | Status | Meaning |
|---|---:|---|
| `AJAR-SCHEMA-INVALID` | 400 | Object fails schema validation |
| `AJAR-VERIFY-BAD-SIGNATURE` | 401 | Signature is absent, malformed, or does not verify |
| `AJAR-VERIFY-UNKNOWN-KID` | 401 | Referenced key id cannot be resolved |
| `AJAR-VERIFY-DOMAIN-BINDING` | 401 | Owner key is not bound to the requested domain |
| `AJAR-VERIFY-EXPIRED` | 401 | Manifest, mandate, offer, or key is expired |
| `AJAR-VERIFY-ROLLBACK` | 409 | Manifest sequence is lower than last accepted sequence |
| `AJAR-MANIFEST-LOCATION` | 409 | Manifest served from a path other than `/.well-known/ajar.json` |
| `AJAR-POLICY-TIER-REQUIRED` | 403 | Required audience tier is not met |
| `AJAR-POLICY-DENIED` | 403 | Owner policy denies this URL, View, or Action |
| `AJAR-POLICY-RATE-LIMITED` | 429 | Owner policy rate limit exceeded |
| `AJAR-MANDATE-MISSING` | 403 | Required mandate was not provided |
| `AJAR-MANDATE-SCOPE` | 403 | Mandate scopes do not cover the requested action |
| `AJAR-MANDATE-CAP` | 403 | Resolved cost or count exceeds mandate caps |
| `AJAR-MANDATE-REVOKED` | 403 | Mandate is revoked, or no revocation status fresh within `cached_ttl` could be obtained |
| `AJAR-ACTION-RISK-FLOOR` | 409 | Action attempts to lower required ceremony below risk floor |
| `AJAR-SIMULATE-REQUIRED` | 409 | Required SIMULATE step is missing |
| `AJAR-SIMULATE-DIVERGED` | 409 | Offer materially diverges from the simulation result; see spec §6 |
| `AJAR-VERSION-BREAKING` | 409 | Breaking change did not bump the major version (site or kernel emitted) |
| `AJAR-AEP-REQUIRED` | 409 | Interoperability-affecting public extension did not follow the AEP process (site or kernel emitted) |
| `AJAR-OFFER-NOT-FOUND` | 404 | Offer id was never issued or is not visible to caller |
| `AJAR-OFFER-EXPIRED` | 409 | Commit attempted after offer expiry |
| `AJAR-OFFER-REPLAY` | 409 | Offer has already been committed or aborted |
| `AJAR-COMMIT-BAD-BINDING` | 401 | Commit signature does not bind offer and mandate hashes |
| `AJAR-CLIENT-PROVENANCE` | 409 | Client failed to preserve provenance-tagged inert View chunks (kernel emitted) |
| `AJAR-METERING-PAYMENT-REQUIRED` | 402 | Payment or settlement proof is required |
| `AJAR-METERING-SETTLEMENT-FAILED` | 402 | Settlement adapter rejected the proof |
| `AJAR-FALLBACK-HUMAN-REQUIRED` | 409 | Manifest-less R2/R3-equivalent operation requires explicit human confirmation (kernel emitted) |

## Problem Example

```json
{
  "type": "https://spec.ajarprotocol.org/problems/mandate-cap",
  "title": "Mandate cap exceeded",
  "status": 403,
  "detail": "Offer total INR 250000 exceeds mandate per_tx cap INR 100000.",
  "ajar_error_code": "AJAR-MANDATE-CAP",
  "spec_section": "8.1"
}
```
