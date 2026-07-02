# 02 — Architecture: End-to-End System Design

*How the four Ajar components fit together, what flows between them, and the reasoning behind every structural choice.*

---

## 1. The core inversion

Today: servers send **presentation** (HTML); machines reverse-engineer meaning from it.
Ajar: servers publish **signed meaning** (manifest + semantic views + typed actions); presentation becomes one rendering among others.

And the connection model inverts too. Agents never "integrate" with sites (the fatal N×M flaw of pre-connecting MCP servers). They **late-bind**:

```
discover → verify → bind → (simulate → act → receipt) → disconnect
```

— exactly how a browser visits a billion websites without installing any of them.

## 2. System overview

```
                        ┌──────────────────────────────┐
                        │       THE INDEX (federated)  │
                        │  transparency logs + semantic │
                        │  capability search nodes      │
                        └───────▲──────────────┬───────┘
                    publish/    │              │  query: "who can sell
                    prove       │              │  refundable train tickets?"
                                │              ▼
┌───────────────┐   deploys  ┌─┴────────────────┐        ┌──────────────────────┐
│  SITE OWNER   ├───────────►│   THE GATEWAY    │◄──────►│  THE CLIENT / KERNEL │
│ (root of      │  reviews,  │ (self-hosted at  │  Ajar   │ (runs beside the     │
│  authority)   │  signs,    │  the site)       │ over   │  agent model)        │
└───────────────┘  configures│                  │ HTTPS  └──────────┬───────────┘
                             │ manifest ▪ views │                   │ scoped by
                             │ actions ▪ policy │                   │ mandate
                             │ metering ▪ logs  │            ┌──────┴────────┐
                             └────────┬─────────┘            │   PRINCIPAL   │
                                      │ wraps                │ (human / org) │
                             ┌────────▼─────────┐            └───────────────┘
                             │  EXISTING WEBSITE │  ← untouched; humans keep
                             │  (HTML/CMS/APIs)  │    browsing it normally
                             └───────────────────┘
```

Trust triangle: **Principal → (mandate) → Agent → (signed requests) → Site**, with the Site's manifest signed by the **Owner key** and logged in transparency logs. Every consequential exchange produces dual-signed **receipts**.

## 3. Component architecture

### 3.1 The Gateway (site-side; the flagship)

**Deployment shapes (all first-class):** standalone reverse proxy (binary/Docker in front of the site, nginx-style), CMS plugin (WordPress/Shopify — reads the source of truth directly), edge/CDN worker, or native library for greenfield sites.

**Internal modules:**

| Module | Responsibility |
|---|---|
| Harvester | Tier-1 structure recovery: CMS/DB access, sitemaps, RSS, JSON-LD/schema.org, OpenGraph, OpenAPI specs |
| Extractor | Tier-2 deterministic extraction: crawl-once, boilerplate stripping, HTML→semantic-markdown, **template clustering** (rules per template, not per page) |
| Inducer | Tier-3 build-time LLM assist: labels fields on sample pages per template, **emits deterministic extraction rules + draft manifest text** (LLM output is config, never a serving-path component) |
| Action Drafter | Derives *candidate* actions from forms/APIs/OpenAPI. Drafts only — never published without owner approval |
| Policy Engine | Evaluates the Owner Policy (see `05-OWNER-CONTROL.md`) on every request: audience tier, pricing, rate limits, risk gates |
| Signer | Manages owner keys; signs manifest, content chunks, offers, receipts; publishes to transparency logs |
| Serving Layer | Content negotiation on the *same URLs* (browser→HTML, agent→semantic view); chunk-addressed diffs; SIMULATE + propose/commit endpoints; 402 metering |
| Freshness | CMS event hooks where available; content-hash diffing elsewhere; drift detection → re-induction |
| Console | Owner UI: coverage report, template review, action approval queue, policy editing, audit log, revenue |

**Request path (agent-facing), simplified:**
`verify agent signature → resolve audience tier → policy check → (402 if metered) → risk gate → serve view / simulate / propose / commit → sign receipt → log`

### 3.2 The Client / Kernel (agent-side)

The defining property: **the model is untrusted.** Prompt injection means any webpage may try to hijack the model. Therefore the Kernel is a deterministic wrapper — the model *proposes*, the Kernel *disposes*. Analogy: the browser sandbox protected your OS from websites; the Kernel protects your **authority** from websites and from the model's own mistakes.

**Internal modules:**

| Module | Responsibility |
|---|---|
| Resolver | `.well-known` fetch, Index queries, manifest signature + transparency-log verification, caching |
| Mandate Store | Holds the principal's signed mandates; hardware/OS keystore for principal keys where available |
| Policy Monitor | Deterministic pre-action check of every proposed call against mandate scope, budget, risk class. **Not bypassable by model output** |
| Simulator | Drives SIMULATE before any R2/R3 action; available for any R1+ action |
| Executor | Signed HTTP (RFC 9421); idempotency keys; propose/commit state machine; payment rail adapters |
| Taint Boundary | All site-originated content enters the model as inert, provenance-tagged data; only manifest-declared schemas are executable |
| Receipt Vault | Append-only local log of mandates presented, simulations, commits, receipts — the audit trail |
| Fallback Engine | For manifest-less sites: headless render (CDP-compatible engine) → semantic compression → same internal representation, flagged `unverified`. Respects robots/AIPREF/402 signals |

**Distribution:** a library/sidecar embeddable in any agent framework (MCP-client-compatible), plus a CLI reference agent.

### 3.3 The Index (network; last to build)

- **Transparency logs:** append-only Merkle logs (CT-style) of manifest publications/updates/revocations. Multiple independent operators. Sites publish; monitors watch for conflicting or fraudulent entries.
- **Search nodes:** crawl the logs, embed manifest capability descriptions, serve semantic queries ("bulk refundable train tickets, Mumbai–Delhi, < ₹3000") returning candidate manifests + log proofs.
- **Trust rule:** the Index is *never* trusted for content — only for discovery. The Client always re-fetches the manifest from the origin domain and verifies signature + log inclusion. A poisoned index can waste an agent's time, never forge a site.
- Federation: anyone runs a node; nodes gossip log references; we operate one reference node only.

### 3.4 The Spec

The contract all three implement. Layered profiles so implementations can be partial but honest:

- **Profile CORE** — manifest + signed semantic content (read-only). Phase 1.
- **Profile ACT** — typed actions, SIMULATE, propose/commit, receipts. Phase 3.
- **Profile PAY** — metering, settlement adapter interface. Phase 4.
- **Profile FED** — transparency logging + index interop. Phase 4.

## 4. End-to-end walkthrough (the canonical scenario)

*A company agent must buy 50 refundable train tickets from a vendor it has never seen.*

1. **Mandate issued (offline, once).** Finance head signs: "travel purchases ≤ ₹2,00,000 this month, transport vendors only, no cancellations, expires on the 31st."
2. **Discover.** Kernel queries an Index node → candidate manifests + inclusion proofs.
3. **Verify.** Kernel fetches each manifest from its origin, checks owner signature and transparency-log inclusion. Impersonators fail here.
4. **Read.** Semantic views fetched (negotiated, chunk-addressed); model reasons over inert, provenance-tagged content.
5. **Simulate.** `search_trains` (R0) freely; then SIMULATE `purchase_tickets` (R3) → predicted: ₹1,84,500, 50 seats, refundable 48h. Kernel checks the *prediction* against the mandate. Misunderstandings die here, consequence-free.
6. **Propose.** Gateway returns a signed offer, frozen 10 minutes. Owner policy may require human approval on the site side; mandate policy may require it on the principal side.
7. **Commit.** Kernel countersigns offer + mandate; Gateway executes against the real backend; both parties store the dual-signed receipt. Payment settles via the manifest-declared rail (x402/AP2/card adapter).
8. **Accountability.** Over-mandate spend → agent operator liable (signatures prove overreach). Within mandate → principal liable. Simulation misrepresented reality → site liable. Disputes are adjudicated from receipts, mostly automatically.

## 5. Data model (canonical objects)

All are canonical JSON (JCS/RFC 8785) signed structures; full schemas in `03-PROTOCOL-SPEC.md`:

- **Manifest** — site identity, keys, views, actions, policy summary, pricing, versioning.
- **View** — chunked semantic content with stable anchors + per-chunk hashes.
- **Action** — JSON-Schema I/O, risk class, preconditions, effects declaration, SIMULATE support, endpoint binding.
- **Mandate** — issuer (principal), subject (agent), scope, caps, expiry, delegation chain (UCAN-compatible).
- **Offer** — site-signed frozen proposal (the "propose" artifact).
- **Receipt** — dual-signed record binding mandate + offer + result.
- **Policy** — owner configuration (audience tiers, pricing, gates); see `05-OWNER-CONTROL.md`.

## 6. Architectural invariants

1. Owner key signs everything site-side; Gateway is inert without it.
2. Kernel enforcement is deterministic code; model output can never widen its own permissions.
3. Same-URL principle: agents and humans share URLs; representation is negotiated, never forked into a shadow site.
4. Index is discovery-only; origin verification is mandatory.
5. Every R2/R3 effect has a dual-signed receipt or it didn't happen.
6. Fallback mode is consensual: honors robots/AIPREF/402; output flagged `unverified`.
7. All formats carry `ajar_version` + extension namespaces (`x-*` prefixes per spec §13).

## 7. Technology direction (recommendation, finalize per ADR at build time)

- Gateway & Kernel core: **Rust** (matches agentgateway/Plasmate precedent; single static binary matters for owner self-hosting) with an embedded-friendly FFI; CMS plugins in native ecosystems (PHP for WordPress).
- Signing: Ed25519 via RFC 9421; JCS canonicalization.
- Fallback rendering: CDP interface so Lightpanda *or* Chromium is pluggable (avoids AGPL entanglement and beta-coverage risk — ADR-010).
- Index: log = CT-style Merkle (Trillian-class); search = pluggable embedding backend.
- LLM use: build-time only (Inducer), provider-pluggable, never in the serving path.
