# 03 — The Ajar Protocol — Draft Specification v0.1

*Status: DRAFT for implementation feedback. Normative keywords (MUST/SHOULD/MAY) per RFC 2119. This spec defines **semantics over HTTPS** — no new wire protocol. JSON Schemas live in `/schemas`, golden examples in `/examples`, registries in `/registries`, and seed conformance vectors in `/test-vectors`.*

---

## 1. Scope & design rules

Ajar defines how a website declares itself to agents (Manifest), serves meaning (Views), exposes operations (Actions) with rehearsal (SIMULATE) and staged execution (Offers/Commits), under delegated authority (Mandates), producing accountability artifacts (Receipts), with owner-declared economics (Metering).

Design rules:
1. **HTTP is the transport.** Extension points used: `.well-known`, content negotiation, headers, status 402, RFC 9421 Message Signatures. No new methods (middlebox safety) — new semantics ride headers and sub-resources.
2. **Signatures over trust.** Every durable artifact is signed; canonicalization via JCS (RFC 8785); keys are Ed25519 unless profile-negotiated.
3. **Partial compliance is honest compliance** via profiles: `CORE` (read), `ACT` (actions), `PAY` (metering), `FED` (transparency). A manifest declares which profiles it implements.
4. **Extensibility:** every object carries `ajar_version` (semver); unknown fields MUST be ignored per the extension policy in §13; breaking changes bump major version; clients negotiate via the manifest's `supported_versions`.

## 2. Discovery & identity

### 2.1 Location
A conforming site MUST serve its manifest at:
```
https://<domain>/.well-known/ajar.json
```
Sites MAY advertise it in HTML (`<link rel="ajar-manifest">`) and via HTTP header (`Link: </.well-known/ajar.json>; rel="ajar-manifest"`) for crawler bootstrap.

### 2.2 Owner keys
- The **Owner Key** (Ed25519) is the site's root of authority. Its public half appears in the manifest AND MUST be provable against the domain via at least one of: DNS TXT record (`_ajar.<domain>`), or the TLS-served manifest itself plus transparency-log history (trust-on-first-use hardened by logs).
- Owner keys SHOULD be kept offline; day-to-day signing uses **Operational Keys** certified by the Owner Key with scoped validity (`content-signing`, `offer-signing`, `receipt-signing`) and expiry. Revocation = signed revocation entry published to logs + removal from manifest.

### 2.3 Agent identity
Agents MUST sign requests with HTTP Message Signatures (RFC 9421, `tag="ajar"`), interoperable with Web Bot Auth: `Signature-Agent` points to the operator's key directory (`/.well-known/http-message-signatures-directory`). `Ajar-Date` is an RFC 3339 request timestamp; it MUST be included in the signature base; receivers MUST reject requests older than the freshness window they advertise. Anonymous access is at the owner's policy discretion (tier `anonymous`).

### 2.4 Canonicalization and signatures

Durable Ajar artifacts are signed as canonical JSON:

1. Remove the artifact's signature field before signing: `signature` for Manifest, Mandate, Offer, and View; `site_signature` and `agent_signature` for Receipt.
2. Serialize the remaining JSON with JCS (RFC 8785), UTF-8, no insignificant whitespace, and lexicographically sorted object keys.
3. Sign the exact canonical bytes with Ed25519.
4. Encode public keys and signatures as base64url without padding.
5. Store the signer key id in `kid`. Verifiers MUST resolve `kid` from the relevant owner, operational, principal, or agent key directory before accepting the signature.

Embedded signatures are part of the transmitted artifact but never part of the bytes signed by that same signature. Nested signed objects, such as an Offer embedded in a Receipt, retain their own signatures as data when the parent object is canonicalized.

Worked Manifest, Mandate, Offer, and Receipt signing vectors live in `test-vectors/crypto-signing.json`. `tools/signing_profile.py` reproduces the canonical bytes, SHA-256 digest, public key, signature, and verification result from only the Python standard library.

## 3. The Capability Manifest

```jsonc
{
  "ajar_version": "0.1",
  "supported_versions": ["0.1"],
  "profiles": ["CORE", "ACT", "PAY"],
  "site": {
    "name": "ExampleRail",
    "domain": "examplerail.example",
    "description": "Intercity train ticketing for India",
    "languages": ["en", "hi"],
    "legal_entity": "ExampleRail Pvt Ltd",          // optional but recommended
    "contact": "agents@examplerail.example"
  },
  "keys": {
    "owner": { "kty": "OKP", "crv": "Ed25519", "x": "<base64url>", "kid": "owner-2026" },
    "operational": [ { "...": "certified key objects with scope + expiry" } ]
  },
  "views": {
    "negotiation": ["application/ajar+json", "text/markdown"],
    "index": "/ajar/views/index",                // machine sitemap: chunk map + hashes
    "chunking": { "stable_ids": true, "diff": "etag-per-chunk" },
    "license": { "read": "allowed", "train": "denied", "terms": "/ajar/license" }
  },
  "actions": [ /* Action objects — §5 */ ],
  "policy_summary": {                                 // public face of Owner Policy (05-OWNER-CONTROL)
    "audience_tiers": ["anonymous", "signed", "verified"],
    "rate_limits": { "anonymous": "60/h", "signed": "600/h" },
    "requires_mandate_from_risk": "R2"
  },
  "metering": {                                       // PAY profile
    "currency": "USD",
    "read": { "anonymous": "0.001/req", "signed": "0" },
    "settlement": ["x402", "ap2-card"],
    "endpoint_402": true
  },
  "federation": {                                     // FED profile
    "logs": ["https://log1.ajar-example.org", "https://log2.example"],
    "latest_sth": "<signed tree head reference>"
  },
  "issued_at": "2026-07-02T00:00:00Z",
  "expires_at": "2026-10-01T00:00:00Z",               // manifests MUST expire (max 180d)
  "sequence": 42,                                     // monotonic; replay/rollback protection
  "signature": { "alg": "Ed25519", "kid": "owner-2026", "sig": "<base64url over JCS(manifest)>" }
}
```

Manifest lifetime is capped at 180 days. Verifiers MUST reject manifests whose `expires_at` is more than 180 days after `issued_at`.

Verification rule (Client): valid owner signature → domain binding proof → not expired → lifetime ≤ 180 days → sequence ≥ last seen → (FED) log inclusion proof. Fail any ⇒ treat site as manifest-less (fallback rules, §9).

## 4. Views (Profile CORE)

- **Same-URL negotiation:** a request with `Accept: application/ajar+json` (rich chunked view) or `Accept: text/markdown` (plain view) to any content URL returns the semantic representation; browsers get HTML untouched.
- **View object:** the `application/ajar+json` response is `{ ajar_version, url, content_type, etag, chunks[], signature }`. Each chunk is `{ id, type, content, hash, links[] }`; chunk `type` is one of `heading`, `paragraph`, `list`, `table`, `product`, `action_hint`, or `metadata`.
- **Chunking:** views use **stable ids** across re-renders. Every chunk carries `hash`; the view response carries a view-level `etag`. A client revalidates with `If-None-Match: <view etag>`; on match the server returns 304; on mismatch the server returns the full view object, and the client diffs locally by chunk `hash`.
- **Signing:** the embedded `signature` is the operational content-signing key over the canonical view object. `Ajar-Content-Signature` carries the same signature value as a header for streaming/proxy use.
- **Provenance:** every chunk is data, never instructions. Clients MUST tag chunks with origin and treat them as inert in model context (see 04-SECURITY-MODEL).

## 5. Actions (Profile ACT)

```jsonc
{
  "id": "purchase_tickets",
  "title": "Purchase train tickets",
  "risk": "R3",                                  // R0 | R1 | R2 | R3 — §5.1
  "input_schema":  { "$ref": "json-schema for parameters" },
  "output_schema": { "$ref": "json-schema for result" },
  "effects": [                                    // machine-readable consequence declaration
    { "type": "financial.charge", "currency": "INR", "max": "computed" },
    { "type": "resource.create", "resource": "booking", "reversible_until": "P2D" }
  ],
  "preconditions": ["seat_availability"],
  "simulate": true,                               // MUST be true for R1+ (§6)
  "execution": "two_phase",                       // "direct" allowed only for R0/R1
  "idempotency": "required",                      // Idempotency-Key header, R1+ MUST
  "requires": { "tier": "verified", "mandate_scopes": ["commerce.purchase.transport"] },
  "pricing": { "per_call": "0", "settlement_on_commit": true },
  "endpoint": "/ajar/actions/purchase_tickets",
  "transport": "ajar-http"                         // or "mcp" | "webmcp" binding
}
```

### 5.1 Risk classes (normative taxonomy)

| Class | Definition | Examples | Minimum protocol requirements |
|---|---|---|---|
| **R0** | Pure read; no state change | search, fetch, quote | none |
| **R1** | Reversible write | cart add, seat hold, draft | idempotency key; SIMULATE support |
| **R2** | Irreversible or hard-to-reverse write | send message, delete, submit filing | SIMULATE + two-phase + dual receipts + mandate |
| **R3** | Financial / legal effect | payment, purchase, contract | all R2 requirements + settlement binding + amount caps checked against mandate |

Owners assign the class; misclassification shifts liability to the site (§8.4). Owner Policy may *raise* requirements per action (e.g., human approval on R2), never lower below this table.

## 6. SIMULATE — the rehearsal primitive

Every action with `simulate: true` MUST accept the same input at:
```
POST <action.endpoint>   +  header  Ajar-Mode: simulate
```
(Equivalently `.../simulate` sub-resource; both MUST behave identically.)

Requirements:
- **Zero side effects.** No state change, no charge, no reservation. Rate limiting/metering MAY apply to the simulate call itself.
- **Faithful prediction.** Response = `{ ajar_version, type, action_id, predicted_output, resolved_effects, total_cost, validity_window: { valid_until }, warnings[] }` with effects fully resolved to concrete values (e.g., exact price incl. taxes).
- **Binding-ish honesty:** predictions are not offers. An Offer materially diverges from a simulation when, for the same canonical input within the simulation's `validity_window`, the offer's `resolved_effects` differ or its `total_cost` exceeds the simulated `total_cost`. Kernels MUST reject materially diverged offers (AJAR-SIMULATE-DIVERGED). Repeated material divergence constitutes misrepresentation (§8.4).
- Clients (Kernel) MUST simulate before any R2/R3 propose, and MUST re-check the *simulation result* — not the model's belief — against the mandate.

## 7. Two-phase execution: Offer → Commit

For `execution: two_phase`:

1. **Propose:** `POST <endpoint>` with `Ajar-Mode: propose` + input + mandate reference → site returns a signed **Offer**:
   `{ ajar_version, type, offer_id, action_id, input_hash, resolved_effects, total_cost, issued_at, expires_at, single_use?, signature }` (freeze window: owner-configured, default 10 min). When `single_use` is true or omitted, committing the same `offer_id` twice MUST fail with AJAR-OFFER-REPLAY.
2. **Commit:** `POST <endpoint>` with `Ajar-Mode: commit` + `{ offer_id, mandate, agent_signature over (offer_hash ‖ mandate_hash) }` → site executes and returns a **Receipt**.
3. Either side may **abort**; expired offers are void; commit of an expired/never-issued offer MUST fail closed.

## 8. Mandates & Receipts

### 8.1 Mandate object
```jsonc
{
  "ajar_version": "0.1",
  "type": "mandate",
  "id": "urn:uuid:...",
  "issuer": { "kind": "principal", "key": { "...": "principal pubkey / DID" } },
  "subject": { "kind": "agent", "operator": "https://agentco.example", "key": { "..." : "" } },
  "scopes": ["commerce.purchase.transport", "content.read.*"],
  "caps": { "per_tx": { "INR": 200000 }, "total": { "INR": 200000 }, "count": 5 },
  "constraints": { "domains_allow": ["examplerail.example", "*.examplerail.example"], "risk_max": "R3",
                   "forbidden": ["commerce.cancel.*"] },
  "valid_from": "2026-07-01T00:00:00Z",
  "valid_until": "2026-07-31T23:59:59Z",
  "delegation": { "chain": ["<UCAN-compatible proof chain, optional>"], "sub_delegation": false },
  "revocation": { "endpoint": "https://principal.example/ajar/revocations", "cached_ttl": "PT10M" },
  "signature": { "...": "principal signature over JCS(mandate)" }
}
```
- Scope names use the dotted registry in `registries/scopes.md`. A mandate scope covers an action requirement by exact match or segment-wise suffix wildcard match: `M.*` matches scopes with `M`'s segments plus one or more additional segments, so `commerce.purchase.*` covers `commerce.purchase.transport` but not `commerce.purchase` or `commerce.purchaseextra.x`. Entries in `constraints.forbidden` override allowed scopes unconditionally.
- `domains_allow` entries are exact hostnames or `*.<domain>` wildcards; `*.<domain>` matches any subdomain but not the apex.
- **Standing mandates** (org↔org, e.g., recurring invoices) are ordinary mandates with recurrence constraints (`caps.per_period`) and long validity — the machinery is identical.
- Sites MUST verify: signature, validity window, scope ⊇ action requirement, caps ≥ resolved cost, revocation status. Revocation status may be cached up to `cached_ttl`; within that window a failed refresh MAY rely on the cache. With no cached status fresh within `cached_ttl`, the site MUST fail closed with AJAR-MANDATE-REVOKED.

### 8.2 Receipt object
Dual-signed record: `{ receipt_id, offer (embedded), mandate_hash, result_summary, executed_at, site_signature, agent_signature }`. Both parties MUST retain receipts (site: per policy retention; kernel: Receipt Vault). Receipts are the atoms of dispute resolution and regulatory audit.

### 8.3 Payments binding (Profile PAY)
Ajar does not move money. `metering` + Offer `total_cost` bind to a **settlement adapter**: `x402` (402 challenge/response, stablecoin), `ap2-card` (AP2 mandate → card rails), or vendor adapters. Settlement proof references the `receipt_id`.

`Ajar-Price: <decimal amount> <ISO-4217 currency>` is an advisory price quote on 402 responses and offer-bearing responses; the signed Offer's `total_cost` is authoritative.

### 8.4 Liability resolution (normative intent)
- Action outside mandate scope/caps → **agent operator** liable (signatures prove overreach; site is safe iff it verified correctly).
- Within mandate, principal regrets → **principal** liable (they signed).
- Simulation/offer materially misrepresented effects, or risk class understated → **site** liable (its signed declarations prove it).
- Site failed to verify a mandate it was required to verify → **site** liable for resulting overreach.

## 9. Fallback interaction (manifest-less sites)

Clients MAY interact with non-Ajar sites via rendering/extraction, but MUST: honor robots.txt / AIPREF signals and 402 challenges; identify themselves via signed requests; flag all derived content `unverified`; and MUST NOT execute R2/R3-equivalent operations without explicit human confirmation per operation. Fallback is a transition path, not a peer mode.

## 10. HTTP surface summary

| Element | Convention |
|---|---|
| Manifest | `GET /.well-known/ajar.json` |
| View | `GET <any content URL>` + `Accept: application/ajar+json \| text/markdown` |
| View index | `GET <manifest.views.index>` |
| Action | `POST <action.endpoint>` + `Ajar-Mode: simulate \| propose \| commit` (absent = direct, R0/R1 only) |
| Idempotency | `Idempotency-Key: <uuid>` (R1+ MUST) |
| Request timestamp | `Ajar-Date: <RFC 3339 timestamp>` signed in the HTTP Message Signature base |
| Metering | `402` + `Ajar-Price` / settlement-adapter headers (x402-compatible) |
| Signatures | RFC 9421 `Signature`/`Signature-Input` (`tag="ajar"`), `Ajar-Content-Signature` on views |
| Errors | RFC 9457 problem+json with the `Ajar-Error-Code` registry in `registries/error-codes.md` |

## 11. Conformance

- **Gateway/CORE:** valid signed manifest; negotiated signed views; chunk diff.
- **Gateway/ACT:** risk classes enforced per §5.1 table; SIMULATE fidelity; two-phase integrity; mandate verification; receipts.
- **Client:** verification pipeline (§3); simulate-before-commit; deterministic mandate enforcement; receipt retention; fallback rules (§9).
- Executable seed vectors live in `/test-vectors` and are checked by `tools/validate_examples.py`. A future standalone conformance repo will turn these data vectors into a public implementation harness.

## 12. Open questions (tracked in DECISIONS.md)

- OQ-1: manifest size limits & sharding for huge sites (per-section sub-manifests?).
- OQ-2: revocation transport — pull endpoint vs. log-embedded revocations vs. both.
- OQ-3: SIMULATE for actions with inherently uncertain outcomes (auctions, inventory races) — probabilistic effect syntax?
- OQ-4: privacy-preserving discovery (query patterns leak intent to Index nodes; OPRF/PSI options).
- OQ-5: scope-registry governance once external parties adopt.

## 13. Version and extension policy

- `ajar_version` uses semantic versioning. `0.1` is the first implementation draft.
- Compatible additions MAY add optional fields, registry entries, examples, or non-required schema properties.
- Breaking changes MUST bump the major version and include a migration note.
- Unknown fields MUST be ignored unless they appear in an object position where the schema has `additionalProperties: false`.
- Private extension fields and settlement adapters MUST use `x-<vendor>-` prefixes. Private scopes MUST use `x-<vendor>.` prefixes because `.` is the scope segment separator.
- Public extensions that affect interoperability MUST go through the AEP process.

Compatible example: adding optional `federation.monitors[]` to a FED manifest while old clients continue to verify signatures and use `federation.logs`.

Breaking example: changing Offer `total_cost.amount` from a decimal string to a number would require a major version bump and a migration note because it changes canonical bytes and validation behavior.
