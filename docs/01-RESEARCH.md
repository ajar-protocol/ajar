# 01 - Research: Prior Art and Positioning

Snapshot date: July 2026. This document records the research that shaped Ajar: what already exists, what Ajar reuses, and what appears to be new. Re-verify claims before citing externally; this field changes quickly.

---

## 1. Executive summary

No single project appears to cover the complete owner-controlled agentic-web stack. Individual pieces are being addressed by active projects, funded initiatives, and earlier drafts. Three gaps remain unresolved:

1. **Discovery is the bottleneck.** Most protocols assume the agent already found the site.
2. **Persistent identity/authority is under-specified.** Payment protocols assume authorization exists but do not establish the full chain.
3. **Policy enforcement must live in infrastructure, not prompts.** This is widely acknowledged, but not standardized.

Ajar's working thesis: a signed site manifest, SIMULATE plus risk classes, generalized mandates with liability semantics, a deterministic client kernel, and federated search over site capabilities belong in one protocol surface.

## 2. The protocol landscape (mid-2026)

### 2.1 Connectivity layer
- **MCP (Model Context Protocol)** — Anthropic, Nov 2024. De facto agent-to-tool standard; 110M+ monthly downloads; official Registry; date-versioned spec. *Ajar stance: adopt as the tool wire format and collaborate with its ecosystem.*
- **A2A (Agent2Agent)** — Google → Linux Foundation; v1.0 April 2026; 150+ orgs; signed agent cards, multi-tenancy. Agent↔agent, not agent↔site. *Adopt for org↔org phases.*
- **ANP (Agent Network Protocol)** — github.com/agent-network-protocol. Explicitly "the HTTP of the Agentic Web": did:wba identity, meta-protocol negotiation, JSON-LD Agent Description (`ad.json`), AgentConnect SDK, W3C white paper. Closest philosophical match to Ajar; limited global adoption (~300★ SDK); agent-centric rather than site/owner-centric. *Study deeply; interop target.*
- **WebMCP** — W3C Web Machine Learning CG (webmachinelearning/webmcp); pages act as in-page MCP servers exposing client-side tools; shipped in Chrome Canary Feb 2026; Draft CG Report (not a standard) as of June 2026. *Adopt as an optional action transport for interactive sites; our manifest can point at WebMCP tools.*
- **Others:** IBM ACP, AGNTCY (Cisco/LF: OASF schema + Agent Directory), Eclipse LMOS, Fetch.ai Agent Chat Protocol, Agora (meta-protocol research).

### 2.2 Content / readability layer (largely solved; do not rebuild)
- **llms.txt** (llmstxt.org) — adopted by >10% of major domains by early 2026; content index only, no actions, unsigned.
- **Cloudflare "Markdown for Agents"** (Feb 2026) — `Accept: text/markdown` content negotiation; ~80% token reduction; Cloudflare-only.
- **Mintlify / Evil Martians / Vercel Agent Readability Spec** — content negotiation, `.md` mirrors, headers advertising doc indexes; Vercel spec defines 15 site-wide + 23 per-page checks.
- **NLWeb** — Microsoft (open source); natural-language endpoint per site leveraging schema.org; each instance is an MCP server; WordPress/Yoast Schema Aggregation (Mar 2026).
- **The Semantic Web (2001) — the cautionary tale.** Failed on incentives: no consumers for markup, human-authored ontologies. Both conditions have now flipped: agents with purchasing power exist, and LLMs can auto-generate the structured views. See §5.

### 2.3 Manifest / declaration layer (fragmented)
- **wild-card-ai/agents-json** — most serious `agents.json`: OpenAPI-based, adds *flows* (multi-call outcome contracts) and *links*, proposed at `/.well-known/agents.json`, deliberately stateless. Unsigned; API-centric; stalled.
- **jmilinovich/agents.json**, **lando22/agents.json** — early drafts (site interaction declarations; UI-interaction focus).
- **A2A Agent Cards, MCP Server Cards (SEP-1649), NANDA AgentFacts, agent-permissions.json, robots.txt, sitemap.xml, llms.txt, UCP feeds** — a site being "agent-ready" in 2026 means maintaining ~9 unsigned, uncoordinated files. Readiness checkers (agent-ready.dev) audit all of them. None are cryptographically signed at the site level; none unify content + actions + policy + pricing.

### 2.4 Discovery / registry layer
- **MIT Project NANDA** — "Quilt of Registries"; lean index resolving to signed JSON-LD AgentFacts; sub-second revocation; hosted at 15 universities; community designs include transparency logs with inclusion proofs. Registers *agents*, not site capabilities.
- **agentfacts.ai** — commercial: cryptographic identity + transparency logs for agents; `/.well-known/agentfacts.json`; adapters for UCP/TAP/A2A/ERC-8004.
- **MCP Registry** (official metaregistry), **AGNTCY ADS**, **Microsoft Entra Agent ID**, **ANS (Agent Name Service)**.
- **ERC-8004 "Trustless Agents"** — Ethereum standard (MetaMask/EF/Google/Coinbase co-authors): on-chain Identity (ERC-721), Reputation, and Validation registries; extends A2A with a trust layer.
- **Gap:** all register agents; none do CT-style transparency + *semantic capability search* over **website** manifests at web scale.

### 2.5 Identity, authorization & delegation layer
- **Web Bot Auth** (IETF drafts, Cloudflare) — RFC 9421 HTTP Message Signatures + Ed25519 + `Signature-Agent` header + `/.well-known/http-message-signatures-directory`. Major agent and platform operators already sign requests. *Adopt for agent identity on the wire.*
- **UCAN** (ucan-wg/spec) — trustless, user-originated capability delegation: verifiable, delegable capability chains over DIDs; the delegation chain is by definition a provenance log; revocation supported. **This is the mandate cryptography, already specified.** Barely adopted in the AI agent world. *Adopt/adapt as mandate chain format.*
- **AP2 (Agent Payments Protocol)** — Google; Apache-2.0; v0.2 Apr 2026; Python/TS/Kotlin/Go reference code; cryptographically signed *mandates* (intent/cart) proving a human authorized a purchase; 60+ partners (Mastercard, PayPal, Adyen, AmEx, Coinbase...). Known limits (self-acknowledged): mandates bind to the **user's** key, not the agent's; agent identity unsolved; revocation delicate; untested at card-network volume. Payments-only.
- **Visa TAP** (Oct 2025, with Cloudflare) — signs agent identity into HTTP headers, verified against Visa's directory. **Mastercard Agent Pay** — similar. **GNAP, OAuth 2.1 extensions** — IETF delegation work.

### 2.6 Payments / economics layer (active; integrate first)
- **x402** — Coinbase; HTTP 402 + stablecoins (USDC on Base/Solana); 165M transactions, ~$50M volume, 69k active agents by Apr 2026; donated to Linux Foundation (x402 Foundation, Apr 2026). AWS Bedrock AgentCore Payments (May 2026) handles x402 natively.
- **ACP (Agentic Commerce Protocol)** — commerce protocol based on shared payment tokens; earlier assistant-hosted checkout surfaces retired in Mar 2026 while the protocol continued with a merchant-hosted checkout direction.
- **UCP (Universal Commerce Protocol)** — Google/Shopify, Jan 2026; 20+ launch partners (Target, Walmart, Best Buy, Mastercard, Visa...); full commerce journey; AP2 as its payment layer; merchant stays Merchant of Record.
- **MPP (Machine Payments Protocol)** — Stripe/Tempo, Mar 2026; x402-backward-compatible; adds sessions/streaming/recurring across stablecoins, cards, bank transfers.
- Consensus view: these **compose by layer**. Ajar's manifest declares pricing; settlement plugs into any of these rails.

### 2.7 Enforcement / kernel layer (more research than deployed product)
- Academic action-boundary systems: **PCAS** (deterministic reference monitor; compliance 48%→93%, zero violations in instrumented runs), **AgentSpec**, **Progent**, **Conseca**, **FORGE**, **VIGIL**, **GuardAgent**, **ShieldAgent**.
- Data/control separation vs. prompt injection: **CaMeL** (Google DeepMind), IFC-based agents, AgentArmor.
- Practitioner middleware: **NeMo Guardrails**, **Guardrails AI**, OPA/Rego gateways, **MI9**, **SAFi**; TEE attestation work (Proof-of-Guardrail, Phala ERC-8004 TEE agent).
- Regulatory driver: **EU AI Act high-risk requirements effective Aug 2, 2026** (transparency documentation, human oversight, auditability; penalties to 7% global revenue). NIST CAISI AI Agent Standards Initiative (Feb 2026).
- **Gap:** no standardized, protocol-level open client. All are prototypes or enterprise middleware.

### 2.8 Gateways & converters (validated pattern; APIs only)
- **agentgateway** (Linux Foundation; Rust) — converts OpenAPI specs into MCP tools automatically; MCP/A2A native; OPA policy; enterprise-grade.
- **Unla, ContextForge MCP Gateway, Docker MCP Gateway, Higress openapi-to-mcp, Speakeasy/FastAPI-MCP/RapidMCP** — API→MCP conversion is proven, commodity tech.
- **Gap:** everyone converts **APIs**. Nobody converts **websites** into signed manifest + semantic views + owner-approved typed actions.

### 2.9 Browsers & extraction (our fallback substrate)
- **Lightpanda** — open-source headless browser from scratch in Zig; CDP-compatible (Puppeteer/Playwright drop-in); ~11x faster / ~9x lighter than headless Chrome; ~21k★; beta (partial Web API coverage); AGPL-3.0 (license implications — see DECISIONS ADR-010). *Candidate fallback engine.*
- **Plasmate** — Rust, Apache-2.0; compiles HTML to a "Semantic Object Model" with 17.5x token compression; MCP tools. *Proof that client-side semantic compression works.*
- **Firecrawl, Crawl4AI, Jina Reader, ScrapeGraphAI, LLM Scraper** — HTML→markdown/structured extraction, proven at scale.
- **Vercel agent-browser** (~35k★, Rust CLI), **Browser Use, Stagehand, Skyvern, Steel, Browserbase** — agent browser automation; accessibility-tree targeting.

### 2.10 Owner-control layer (active, but mostly proprietary)
- **Cloudflare AI Crawl Control**: per-crawler allow/block/charge; customizable 402 responses (>1B/day already served); **July 1, 2026**: three-class traffic controls (Search / Agent / Training) with **Sept 15, 2026 defaults blocking Training+Agent on ad-bearing pages** for new domains; Pay Per Crawl to "Pay Per Use"; Monetization Gateway waitlist (charge for any page/dataset/API/MCP tool, settling via x402); Human Native acquisition (Jan 2026) to paid data marketplace.
- **RSL (Really Simple Licensing)** — coalition (Reddit, Yahoo, Medium, O'Reilly); XML licensing vocabulary; CDN-agnostic.
- **IETF AIPREF WG** — standardizing machine-readable AI content preferences (robots.txt evolution).
- **Interpretation:** owner-controlled access is becoming normal. Most shipping products are read/crawl-layer only and tied to a vendor network. Ajar's target is the open, self-hosted layer for reading, actions, transactions, and owner policy.

## 3. The novelty delta (be honest, always)

| Ajar element | Closest prior art | What's genuinely new |
|---|---|---|
| Signed site Capability Manifest | agents.json variants, llms.txt, agent cards | Unification of content+actions+policy+pricing; site-key signing; owner as root of authority |
| Capability transparency + semantic search | NANDA quilt, agentfacts.ai, CT logs | Applied to *site capabilities*; federated semantic search over declared actions |
| SIMULATE + R0–R3 effect taxonomy | DB `EXPLAIN`, `eth_call`, AP2 cart preview | Nothing found anywhere as a web-protocol primitive. Strongest novel claim |
| Generalized mandates + liability semantics | AP2 (payments), UCAN (crypto), Visa TAP | Mandates over *all* action types; mechanical liability resolution; standing mandates for org↔org |
| Agent Kernel (deterministic enforcement client) | PCAS/CaMeL/AgentSpec (research), OPA gateways | A standardized, protocol-level open reference client |
| Website→agent Gateway | agentgateway (APIs only), Cloudflare (proprietary, read-only) | Websites, not APIs; self-hosted; includes actions with owner approval |

## 4. Repos to study before implementation (required reading)

1. `modelcontextprotocol/*` — tool wire format we emit.
2. `wild-card-ai/agents-json` — where OpenAPI-based site manifests stopped short.
3. `ucan-wg/spec` — delegation chain cryptography for mandates.
4. `google-agentic-commerce/AP2` — mandate structures, VC usage, known limits.
5. `webmachinelearning/webmcp` — in-page action transport; manifest interop target.
6. `agentgateway` (agentgateway.dev) — OpenAPI→MCP conversion + policy architecture.
7. `agent-network-protocol/*` — ANP agent descriptions + did:wba.
8. `lightpanda-io/browser`, Plasmate, `firecrawl` / `crawl4ai` — fallback + extraction substrate.
9. `erc-8004/erc-8004-contracts` — decentralized trust registries (optional interop).
10. IETF: RFC 9421, Web Bot Auth drafts, AIPREF WG.

## 5. Why now (vs. the Semantic Web's failure)

The Semantic Web (2001) failed because publishers had no immediate consumers for markup, and humans had to author ontologies. The current conditions are different:
1. **Consumers exist.** Agents can act and purchase today.
2. **Authoring can be automated.** LLMs can help generate structured views from existing sites; the Gateway automates the bootstrap.
3. **Money attaches.** 402-native metering can turn machine traffic into revenue.
4. **Defaults are changing.** The web is moving toward "agents blocked unless the owner decides" (Sept 2026), so owners need explicit controls.
5. **Regulation demands auditability.** EU AI Act auditability pressure (Aug 2026) points toward receipts and mandate trails.

Standards spread when the compliant path is easy to implement. The Gateway is designed around that constraint.

## 6. Standing risks to monitor

- **Cloudflare** extends its proprietary stack from read-layer to action-layer before our open one matures. (Mitigation: ship Phase 1 fast; court non-Cloudflare hosting/CMS ecosystems; remain the neutral standard Cloudflare itself could adopt.)
- **W3C AI Agent Protocol CG / WebMCP** standardizes an overlapping manifest. (Mitigation: participate early; design for interop; our owner-policy + mandate + SIMULATE layers remain complementary.)
- **MCP spec drift** — track date-versioned releases; pin versions in Gateway/Client.
- **Payment-protocol shakeout** (ACP retreat already happened once) — keep settlement pluggable, never hard-bind one rail.
