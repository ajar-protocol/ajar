# 03 — The Ajar Protocol — Draft Specification v0.1

*Status: DRAFT for implementation feedback. Normative keywords (MUST/SHOULD/MAY) per RFC 2119. This spec defines **semantics over HTTPS** — no new wire protocol. All JSON examples are illustrative; extracted JSON Schemas will live in `/schemas` once frozen (Phase 0, task T0.4).*

---

## 1. Scope & design rules

Ajar defines how a website declares itself to agents (Manifest), serves meaning (Views), exposes operations (Actions) with rehearsal (SIMULATE) and staged execution (Offers/Commits), under delegated authority (Mandates), producing accountability artifacts (Receipts), with owner-declared economics (Metering).

Design rules:
1. **HTTP is the transport.** Extension points used: `.well-known`, content negotiation, headers, status 402, RFC 9421 Message Signatures. No new methods (middlebox safety) — new semantics ride headers and sub-resources.
2. **Signatures over trust.** Every durable artifact is signed; canonicalization via JCS (RFC 8785); keys are Ed25519 unless profile-negotiated.
3. **Partial compliance is honest compliance** via profiles: `CORE` (read), `ACT` (actions), `PAY` (metering), `FED` (transparency). A manifest declares which profiles it implements.
4. **Extensibility:** every object carries `ajar_version` (semver); unknown fields MUST be ignored; extensions use `x-<vendor>-` prefixes; breaking changes bump major version; clients negotiate via the manifest's `supported_versions`.

## 2. Discovery & identity

### 2.1 Location
A conforming site MUST serve its manifest at:
```
https://<domain>/.well-known/ajar.json
```
Sites MAY advertise it in HTML (`<link rel="ajar-manifest">`) and via HTTP header (`Link: </.well-known/ajar.json>; rel="ajar-manifest"`) for crawler bootstrap.

### 2.2 Owner keys
- The **Owner Key** (Ed25519) is the site's root of authority. Its public half appears in the manifest AND MUST be provable against the domain via at least one of: DNS TXT record (`_ajar.<domain>`), or the TLS-served manifest itself plus transparency-log history (trust-on-first-use hardened by logs).
- Owner keys SHOULD be kept offline; day-to-day signing uses **Operational Keys** certified by the Owner Key with scoped validity (`content-signing`, `offer-signing`) and expiry. Revocation = signed revocation entry published to logs + removal from manifest.

### 2.3 Agent identity
Agents MUST sign requests with HTTP Message Signatures (RFC 9421, `tag="ajar"`), interoperable with Web Bot Auth: `Signature-Agent` points to the operator's key directory (`/.well-known/http-message-signatures-directory`). Anonymous access is at the owner's policy discretion (tier `anonymous`).

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
  "policy_summary": {                                 // public face of Owner Policy (06-OWNER-CONTROL)
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

Verification rule (Client): valid owner signature → domain binding proof → not expired → sequence ≥ last seen → (FED) log inclusion proof. Fail any ⇒ treat site as manifest-less (fallback rules, §9).

## 4. Views (Profile CORE)

- **Same-URL negotiation:** a request with `Accept: application/ajar+json` (rich chunked view) or `Accept: text/markdown` (plain view) to any content URL returns the semantic representation; browsers get HTML untouched.
- **Chunking:** views are arrays of chunks `{ id, type, content, hash, links[] }` with **stable ids** across re-renders. Per-chunk `hash` enables diff sync: client sends `If-None-Match` with the view ETag; server MAY return only changed chunks (`206`-style partial view object).
- **Signing:** each view response carries `Ajar-Content-Signature` (operational key over the chunk hash list) so intermediaries cannot tamper.
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
- **Faithful prediction.** Response = `{ predicted_output, resolved_effects, total_cost, validity_window, warnings[] }` with effects fully resolved to concrete values (e.g., exact price incl. taxes).
- **Binding-ish honesty:** predictions are not offers, but systematic material divergence between simulation and subsequent offers/commits constitutes misrepresentation (liability §8.4).
- Clients (Kernel) MUST simulate before any R2/R3 propose, and MUST re-check the *simulation result* — not the model's belief — against the mandate.

## 7. Two-phase execution: Offer → Commit

For `execution: two_phase`:

1. **Propose:** `POST <endpoint>` with `Ajar-Mode: propose` + input + mandate reference → site returns a signed **Offer**:
   `{ offer_id, action_id, input_hash, resolved_effects, total_cost, expires_at, signature(site) }` (freeze window: owner-configured, default 10 min).
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
  "constraints": { "domains_allow": ["*.examplerail.example"], "risk_max": "R3",
                   "forbidden": ["commerce.cancel.*"] },
  "valid_from": "2026-07-01T00:00:00Z",
  "valid_until": "2026-07-31T23:59:59Z",
  "delegation": { "chain": ["<UCAN-compatible proof chain, optional>"], "sub_delegation": false },
  "revocation": { "endpoint": "https://principal.example/ajar/revocations", "cached_ttl": "PT10M" },
  "signature": { "...": "principal signature over JCS(mandate)" }
}
```
- Scope names use a dotted registry (Phase 0 defines the core registry: `content.*`, `commerce.*`, `communication.*`, `account.*`, `data.*`).
- **Standing mandates** (org↔org, e.g., recurring invoices) are ordinary mandates with recurrence constraints (`caps.per_period`) and long validity — the machinery is identical.
- Sites MUST verify: signature, validity window, scope ⊇ action requirement, caps ≥ resolved cost, revocation check (best effort within `cached_ttl`).

### 8.2 Receipt object
Dual-signed record: `{ receipt_id, offer (embedded), mandate_hash, result_summary, executed_at, site_signature, agent_signature }`. Both parties MUST retain receipts (site: per policy retention; kernel: Receipt Vault). Receipts are the atoms of dispute resolution and regulatory audit.

### 8.3 Payments binding (Profile PAY)
Ajar does not move money. `metering` + Offer `total_cost` bind to a **settlement adapter**: `x402` (402 challenge/response, stablecoin), `ap2-card` (AP2 mandate → card rails), or vendor adapters. Settlement proof references the `receipt_id`.

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
| Metering | `402` + `Ajar-Price` / settlement-adapter headers (x402-compatible) |
| Signatures | RFC 9421 `Signature`/`Signature-Input` (`tag="ajar"`), `Ajar-Content-Signature` on views |
| Errors | RFC 9457 problem+json with `Ajar-Error-Code` registry (Phase 0 task T0.6) |

## 11. Conformance

- **Gateway/CORE:** valid signed manifest; negotiated signed views; chunk diff.
- **Gateway/ACT:** risk classes enforced per §5.1 table; SIMULATE fidelity; two-phase integrity; mandate verification; receipts.
- **Client:** verification pipeline (§3); simulate-before-commit; deterministic mandate enforcement; receipt retention; fallback rules (§9).
- A conformance test suite is a Phase-0/1 deliverable (task T0.7 / T1.10) — implementations claim compliance only against it.

## 12. Open questions (tracked in DECISIONS.md)

- OQ-1: manifest size limits & sharding for huge sites (per-section sub-manifests?).
- OQ-2: revocation transport — pull endpoint vs. log-embedded revocations vs. both.
- OQ-3: SIMULATE for actions with inherently uncertain outcomes (auctions, inventory races) — probabilistic effect syntax?
- OQ-4: privacy-preserving discovery (query patterns leak intent to Index nodes; OPRF/PSI options).
- OQ-5: scope-registry governance once external parties adopt.
