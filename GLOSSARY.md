# GLOSSARY — Canonical Terminology

*One name per concept, used identically across spec, docs, code, and UI. If you need a new term, add it here in the same PR.*

| Term | Definition |
|---|---|
| **Ajar** | Ajar Protocol — the semantic layer over HTTPS defined in `docs/03-PROTOCOL-SPEC.md`. Not a new wire protocol. |
| **Profile** | A named conformance subset of Ajar: `CORE` (read), `ACT` (actions), `PAY` (metering), `FED` (transparency/discovery). |
| **Manifest** (Capability Manifest) | The signed declaration at `/.well-known/ajar.json`: site identity, keys, Views, Actions, policy summary, metering, federation refs. |
| **Owner** | The party with authority over a site. Root of all site-side authority. |
| **Owner Key** | The site's root Ed25519 keypair; signs the Manifest and certifies Operational Keys. Kept offline where possible. |
| **Operational Key** | Owner-certified, scoped, expiring key for day-to-day signing (content, offers). |
| **Gateway** | Self-hosted site-side software: converts, serves, enforces Owner Policy, signs, meters, and logs. |
| **View** | The semantic representation of a content URL, served via content negotiation from the same URL as the human HTML. Composed of Chunks. |
| **Chunk** | Addressable unit of a View with a stable ID and content hash; unit of diff sync and provenance tagging. |
| **View Index** | Machine sitemap: chunk map + hashes + change hints, for full/incremental sync planning. |
| **Action** | A typed, owner-published operation: schemas, risk class, effects, endpoint, execution mode. |
| **Risk class (R0–R3)** | Normative effect taxonomy: R0 read, R1 reversible write, R2 irreversible write, R3 financial/legal. Sets protocol floors. |
| **Effects** | Machine-readable consequence declaration on an Action (and resolved concretely in SIMULATE/Offers). |
| **SIMULATE** | Mandatory dry-run mode for R1+ Actions: identical input, zero side effects, faithful resolved prediction. |
| **Two-phase execution** | Propose → Commit ceremony required for R2/R3. |
| **Offer** | Site-signed frozen proposal produced by Propose: resolved effects, total cost, expiry. Single-use. |
| **Commit** | Agent's countersigned acceptance of an Offer (over offer‖mandate), triggering execution. |
| **Receipt** | Dual-signed record binding Mandate + Offer + result. The atom of accountability and dispute resolution. |
| **Principal** | The human/organization on whose behalf an agent acts; issues Mandates. |
| **Agent** | The acting software system: model + Kernel + operator infrastructure. |
| **Agent operator** | The party running the agent (may equal the Principal). Identified via signed requests. |
| **Kernel** (Client/Kernel) | Agent-side runtime: Resolver, Taint Boundary, Policy Monitor, Simulator, Executor, Receipt Vault, Fallback Engine. The model is outside its trust boundary. |
| **Mandate** | Principal-signed, scoped, time-boxed, capped authorization carried by an agent. UCAN-compatible delegation chains. |
| **Standing Mandate** | A Mandate with recurrence caps and long validity — the org↔org contract primitive (e.g., recurring invoices). |
| **Scope** | Dotted permission name from the registry (e.g., `commerce.purchase.transport`). |
| **Policy Monitor** | The Kernel's deterministic pre-action enforcement: proposal × mandate × simulation → allow/deny/escalate. Not bypassable by model output. |
| **Taint Boundary** | Kernel mechanism ensuring site content enters the model as provenance-tagged inert data. |
| **Receipt Vault** | Kernel's append-only local store of verdicts, artifacts, and receipts — the agent-side audit trail. |
| **Fallback Engine** | Kernel module for manifest-less sites: consensual headless rendering + extraction, output flagged `unverified`. |
| **Owner Policy** | The owner's declarative configuration across five axes: exposure, audience, economics, risk gates, observability. |
| **Tier** | Audience level: `anonymous`, `signed`, `verified`, `allowlist`, `contracted`. |
| **Gate** | Execution ceremony setting per action: `auto`, `mandate`, `human_site`, `threshold(x)`, `deny`. |
| **Console** | The Gateway's owner UI: coverage, policy, approval queue, audit, kill switches, revenue. |
| **Harvester / Extractor / Inducer / Action Drafter** | Conversion pipeline tiers: source tapping / deterministic extraction (template clustering) / build-time LLM rule induction / action candidate drafting. |
| **Template clustering** | Grouping pages by DOM structural signature so extraction rules scale with templates (~5–20/site), not pages. |
| **Drift detection** | Continuous comparison of rendered pages vs. Views; triggers re-induction and owner alerts. |
| **Transparency Log** | Append-only Merkle log of manifest publications/updates/revocations (CT-style). |
| **Monitor (federation)** | Service watching logs for impersonation/anomalies; alerts owners. (Distinct from Policy Monitor.) |
| **Index / Search Node** | Federated service crawling logs and serving semantic capability search; discovery-only, never trusted for content. |
| **Inclusion proof / STH** | Merkle proof of a manifest's log membership / Signed Tree Head. |
| **Late binding** | The connection model: discover → verify → bind → act → disconnect, per task. No pre-integration. |
| **Settlement adapter** | Pluggable payment-rail binding (x402, AP2-card, ...) referenced from metering and receipts. |
| **Conformance suite** | The executable tests + vectors that define what "implements Ajar" means. Claims are valid only against it. |
| **TOFU** | Trust-on-first-use — the accepted first-contact window for non-FED sites, hardened by log history. |
