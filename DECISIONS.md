# DECISIONS — Architecture Decision Records (ADRs)

*Every consequential choice, with the reasoning, so future contributors understand **why** — and know what evidence would justify revisiting. Format: Context → Decision → Consequences. Status: proposed | accepted | superseded.*

---

## ADR-001 — Semantic layer over HTTP; no new wire protocol
**Status:** accepted
**Context:** New protocols historically win only when the substrate can't express the need (WebSocket: full-duplex; QUIC: HoL blocking). Everything Ajar needs has HTTP extension points (.well-known, negotiation, 402, RFC 9421). Backward compatibility is a hard requirement.
**Decision:** Ajar is defined as HTTP semantics: headers (`Ajar-Mode`, `Ajar-Content-Signature`...), sub-resources, and signed JSON objects. No new methods (middlebox safety), no new transport.
**Consequences:** Instant compatibility with all web infrastructure; constrained to HTTP's request/response shape (streaming/push deferred to future profile if ever needed).
**Revisit if:** a capability emerges that provably cannot ride HTTP semantics.

## ADR-002 — Owner sovereignty as the root architecture
**Status:** accepted
**Context:** Layers that scaled handed owners software + control (Apache, Let's Encrypt, WordPress); central conversion (AMP) was rejected. Existing owner controls (CDN crawl products) are proprietary and read-only. We cannot and should not do the web's work centrally.
**Decision:** Self-hosted Gateway; Owner Key signs everything; automation drafts, owners decide; no runtime dependence on the project; safe defaults (nothing → read-only → explicit per-action opt-in).
**Consequences:** Slower per-site onboarding than a central service, but the only path that scales, earns owner trust, and survives us. Defines docs/05 in full.

## ADR-003 — The model is untrusted; enforcement is deterministic
**Status:** accepted
**Context:** Prompt injection makes any model hijackable by page content. Research (PCAS/CaMeL-class) shows deterministic reference monitors reach near-zero violations where prompt guardrails cannot. Emerging regulation demands provable oversight.
**Decision:** All authority checks live in the Kernel's Policy Monitor (pure code); model output is proposals only; keys never in model context; site content crosses a Taint Boundary as inert data; Monitor checks *simulation results*, not model narratives.
**Consequences:** A fully hijacked model cannot exceed mandate scope. Costs: engineering the Monitor well; residual in-scope manipulation risk (documented, 04-SECURITY §6).

## ADR-004 — SIMULATE + R0–R3 risk taxonomy as protocol primitives
**Status:** accepted
**Context:** The largest class of agent disasters is acting on misunderstanding. Precedents (DB `EXPLAIN`, `eth_call`, AP2 cart preview) exist but no web-protocol dry-run primitive was found anywhere (01-RESEARCH §3). Uniform risk classes make permissions, ceremonies, and liability computable.
**Decision:** Every R1+ action MUST support zero-side-effect SIMULATE with faithful resolved effects; R2/R3 MUST use two-phase Offer/Commit; the risk table sets non-lowerable floors.
**Consequences:** Sites bear simulate-fidelity engineering; in exchange, agents rehearse consequence-free and liability for misrepresentation is provable. This is the project's strongest novel claim — protect its integrity (no "approximate" SIMULATE).

## ADR-005 — Mandates generalized beyond payments; liability as arithmetic
**Status:** accepted
**Context:** AP2 proves signed mandates for purchases; UCAN provides delegation-chain cryptography; nothing covers *all* action types or resolves fault mechanically. "Who owns it when it goes wrong" is the adoption blocker for real transactions.
**Decision:** One Mandate object (UCAN-compatible chains) for every consequential action: scopes, caps, expiry, revocation; dual-signed Receipts; normative liability rules (spec §8.4). Standing Mandates cover org↔org recurring flows.
**Consequences:** Disputes become artifact evaluation; requires the scope registry to be well-governed (OQ-5) and revocation latency accepted (TTL-bounded).

## ADR-006 — Late binding; the Index is discovery-only
**Status:** accepted
**Context:** Pre-connecting integrations (N×M) is the flaw that caps MCP at web scale; central registries become gatekeepers and single points of failure; CT logs prove federated tamper-evidence works.
**Decision:** discover → verify → bind → act → disconnect. Manifests published to federated transparency logs; Index nodes serve semantic search; Clients ALWAYS re-fetch and verify at origin. Index results are candidates, never facts.
**Consequences:** A poisoned index wastes time, never forges a site; discovery omission remains a residual (multi-node queries). We run only reference infrastructure.

## ADR-007 — Same-URL content negotiation (no shadow site)
**Status:** accepted
**Context:** Duplicate `.md` mirrors cause drift, SEO duplication, and split truth. Negotiation is proven in the wild at scale.
**Decision:** Views are negotiated representations of the *same URLs* humans use; chunked, stable-ID'd, signed.
**Consequences:** Gateway must integrate at a point where it can answer for content URLs (proxy/plugin/edge — all supported shapes).

## ADR-008 — Build-time LLM only; serving is deterministic
**Status:** accepted
**Context:** Per-request LLM extraction is slow, costly, non-deterministic, and un-auditable. Template clustering makes build-time induction scale with templates, not pages.
**Decision:** LLMs label samples and emit extraction rules/config at build time (Inducer); the serve path is pure deterministic code; drift detection triggers re-induction.
**Consequences:** Cheap, fast, auditable serving; a hard tail of sites needs owner-side integration instead (tracked in the planning repo roadmap).

## ADR-009 — Implementation language: Rust core
**Status:** accepted
**Context:** Owner self-hosting favors single static binaries; precedent (agentgateway, Plasmate, Vercel agent-browser) is Rust; memory safety matters in TCB components (Signer, Monitor).
**Decision:** Rust for Gateway core, Kernel, log/index reference implementations; ecosystem-native for plugins (PHP for WordPress, TS for edge workers); FFI/embedding for framework adapters.
**Consequences:** Steeper contribution curve than TS/Python — mitigated by thin native adapters, clear examples, and a small trusted core.

## ADR-010 — Fallback rendering behind a CDP interface (engine-pluggable)
**Status:** accepted
**Context:** Lightpanda is fast/light but beta-coverage and AGPL-3.0; Chromium is heavy but complete and permissively licensed. Linking AGPL into Apache-2.0 deliverables is unacceptable.
**Decision:** Kernel Fallback Engine speaks CDP to an *external process*; Lightpanda and Chromium are interchangeable runtime choices (process isolation, not linking). Default documented per platform; auto-fallback Lightpanda→Chromium on coverage failure.
**Consequences:** License-clean, future-proof against engine churn; small orchestration overhead.

## ADR-011 — Licensing: CC-BY-4.0 (spec/docs), Apache-2.0 (code)
**Status:** accepted
**Context:** Maximize adoption incl. commercial embedding (CDNs, hosts offering managed Gateways is a *win*); patent grant matters for protocol code; spec must be freely implementable.
**Decision:** As titled. Contributor DCO; no CLA initially.
**Consequences:** Others may build proprietary forks. That is acceptable because the standard and conformance suite are the durable shared assets.

## ADR-012 — Governance path to a neutral foundation
**Status:** accepted
**Context:** Standards owned by one party get routed around; the venue consolidating agent protocols is W3C CG / Linux Foundation orbit. Future-proofing = the standard outlives the founders.
**Decision:** From v0.1, spec is written venue-ready (IP-clean, RFC-2119 style); Phase 5 formally lodges governance externally; trademark/badge policy separates the *name* from the *code*.
**Consequences:** We trade unilateral control for survivability — the point of the project.

## ADR-013 — Consensual fallback only (no adversarial scraping)
**Status:** accepted
**Context:** The Client could try to "work everywhere" by bypassing bot defenses; that would undermine the owner trust the whole project depends on, and the web's defaults are moving against non-consensual automation.
**Decision:** Fallback honors robots/AIPREF/402, signs requests, flags output `unverified`, never performs R2/R3-equivalents without per-operation human confirmation (spec §9).
**Consequences:** Some sites are simply unavailable to fallback — correct behavior, and the Gateway is the remedy.

## ADR-014 — No telemetry in owner-deployed software
**Status:** accepted
**Context:** Sovereignty claim is hollow if the software phones home; enterprise/regulated adopters require it anyway.
**Decision:** Gateway/Kernel emit owner-local metrics/logs only; any network reporting (e.g., log publication) is explicit, documented protocol behavior the owner configured.
**Consequences:** We lose easy usage analytics; adoption measured via opt-in directory/badge instead.

---

## Open questions (paired with spec §12)
OQ-1 manifest sharding · OQ-2 revocation transport · OQ-3 probabilistic SIMULATE · OQ-4 private discovery · OQ-5 scope-registry governance. Owner: assign at Phase-0 T0.10.

## ADR-015 — Project name: Ajar Protocol
**Status:** accepted
**Context:** "AgentWeb Protocol" collided with existing projects. Naming research across the door/gate space (Postern, Sallyport, Dwarpal, Torana, Threshold, etc.) found collisions everywhere; "Ajar" — a door deliberately left partly open, exactly as far as the owner chooses — is the project's meaning in one word, and "Ajar Protocol" / `ajar-protocol` org is clean and searchable.
**Decision:** Project and protocol are named **Ajar**. Wire identifiers: `/.well-known/ajar.json`, `application/ajar+json`, `Ajar-*` headers, `ajar_version`, signature `tag="ajar"`, GitHub org `ajar-protocol`.
**Consequences:** Continue trademark/domain checks before broad launch; the word "ajar" alone is used by unrelated small projects — always brand as "Ajar Protocol".

## ADR-016 — E-commerce as the beachhead vertical
**Status:** accepted
**Context:** Adoption needs one vertical where value is immediate and measurable. E-commerce has: urgent agent traffic, existing structured data (products, prices, schema.org), platform concentration (WooCommerce via WordPress; Shopify), a clear R0→R3 ladder (browse → cart → checkout), and adjacent protocols (ACP/UCP) that Ajar can work alongside.
**Decision:** First-class integration repos `ajar-woocommerce` and `ajar-shopify` ship alongside the reference Gateway; the conformance pilot set over-weights commerce sites; demos include a storefront.
**Consequences:** Docs/blog verticals remain supported (they're the easiest CORE targets and our own demo), but engineering priority and case studies lead with commerce.

## ADR-017 — Adoption tooling is a deliverable: the Ajar Docs MCP server
**Status:** accepted
**Context:** In 2026, protocols are adopted through developer tools as much as through human reading. If a coding tool inside any company's repo can query the Ajar spec, schemas, examples, and implementation checklists through MCP, integrating Ajar becomes straightforward. This is HTTP-style adoption strategy: make the compliant path easy to follow.
**Decision:** `ajar-docs-mcp` is a first-class repo: an MCP server exposing the spec as structured resources and task-oriented tools (spec search, section retrieval, manifest checklist, conformance-vector lookup). It ships as soon as the spec freezes (Phase 0 exit).
**Consequences:** Docs must stay machine-consumable (stable heading IDs, one-concept-per-section discipline). The spec repo is this MCP's data source — another reason spec quality gates everything. And ajarprotocol.org itself must serve Ajar views: we are our own first conformant site.

## ADR-018 — Gateway stack mechanics
**Status:** accepted
**Context:** ADR-009 fixed Rust for the Gateway core and deferred stack mechanics to Phase-1 kickoff (tracked as `ajar-gateway` issue #15). The Gateway architecture contract (`ajar-gateway/AGENTS.md`) fixes module boundaries, a single signing module, typed registry-mapped errors, a license allowlist, and a serve path with bounded resources; the stack must make those rules enforceable by tooling rather than review vigilance.
**Decision:** Pinned stable Rust via `rust-toolchain.toml` (MSRV = stable at kickoff). Cargo workspace with one crate per bounded module (`signer`, `policy-engine`, `serving`, `harvester`, `extractor`, `inducer`, `store`, `ajar-gateway` binary) so the crate graph enforces dependency direction. HTTP stack: tokio + axum + tower. TLS: rustls (no OpenSSL). Crypto: ed25519-dalek plus an RFC 8785 JCS implementation, confined to the `signer` crate. Serialization: serde/serde_json. Errors: thiserror-typed per crate; `anyhow` forbidden in library crates. Conventions: rustfmt default config; clippy with `-D warnings` (suppressions need inline justification); `cargo test`; cargo-deny in CI enforcing the license allowlist and security advisories; `#![forbid(unsafe_code)]` in every crate, with any future signer exception requiring its own documented justification and human review.
**Consequences:** The single-audited-crypto-module rule, the dependency-direction rule, and the license policy become compile-time or CI failures instead of review conventions. Contributors get a fully conventional Rust setup with no bespoke tooling to learn. Framework choice (axum) is an edge concern behind the Serving Layer boundary and can be revisited without touching core crates.

## ADR-019 — Gateway distribution: engine plus platform adapters
**Status:** accepted
**Context:** Most sites will adopt Ajar through platform-native channels: Shopify apps, WordPress plugins, Laravel composer packages, and edge workers, not by operating a raw server. The Gateway must therefore be an embeddable engine with stable integration seams, and integration smoothness is a first-class product goal.
**Decision:** Three distribution tiers are supported and conformance-equal. Direct: a binary or Docker reverse proxy for owners and operators who want that shape explicitly. Sidecar plus contracts: the primary platform-plugin path, where the adapter generates prepared content into the content-store contract (`ajar-gateway/docs/CONTENT-STORE.md`), manages config, triggers hot reload through the admin control API, and in Phase 3 binds Actions through an HTTP callback contract. The engine owns all protocol ceremony: signing, floors, offer and commit, receipts, and error codes. The adapter owns platform integration and business logic only. Adapter teams do not need Rust. Embedded library: Gateway crates consumed natively, Rust today and C-ABI/FFI adapters later per ADR-009, with callback traits for Actions. Protocol ceremony is never implemented by the integrator and has no opt-out.
**Consequences:** The store contract, control API, and callback contract become versioned public interfaces governed by the spec-change discipline. Platform repos such as `ajar-woocommerce`, `ajar-shopify`, and future Laravel or other adapters are thin adapters. "Easy to integrate" never means "able to skip ceremony".
