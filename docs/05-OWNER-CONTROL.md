# 05 - Owner Control: Sovereignty & Policy Model

Ajar is not a central service that opens websites to agents. It is a standard and software stack that lets site owners decide what agents can read or do. This document defines the policy surface and the owner experience.

---

## 1. The principle

Internet infrastructure tends to last when owners keep control: Apache/nginx for hosting, Let's Encrypt for certificates, WordPress for publishing. Ajar follows the same model:

1. **The Owner Key is the root of all authority.** Nothing exists site-side without the owner's signature. The Gateway is inactive until the owner provisions keys and approves policy.
2. **Automation drafts; owners decide.** The Harvester, Extractor, Inducer, and Action Drafter can suggest content and actions, but owners approve what goes live.
3. **Safe by default.** A fresh install exposes nothing. First approval exposes read-only public content. Actions require explicit per-action opt-in.
4. **No runtime dependence on the project.** A Gateway keeps working if ajarprotocol.org disappears. Config is self-hosted, vendor-neutral, and exportable.
5. **Policy is configurable.** Owners can block everything, enable read-only access, approve actions manually, or allow automated commerce within signed constraints.

## 2. The five control axes

Owner Policy is a declarative document: versioned, diffable, and signable. It covers five areas:

### Axis 1 — Exposure (*what* is open)
- Content: include/exclude by path patterns, content type, CMS taxonomy; per-section license terms (read vs. train vs. quote); authenticated/personal areas excluded by default and require explicit per-tier override.
- Actions: each action individually enabled, wired, risk-classed, and signed. Draft actions live in an approval queue until the owner publishes them.

### Axis 2 — Audience (*who* may enter)
Tiers, each independently configurable per resource/action:

| Tier | Meaning |
|---|---|
| `anonymous` | Unsigned requests |
| `signed` | Valid RFC 9421 signature resolvable to any operator directory |
| `verified` | Signed + operator on a trust list the owner subscribes to (or self-curates) |
| `allowlist` | Explicit operator/principal identities the owner named |
| `contracted` | Allowlist + an active standing mandate/agreement on file |

The trust-list format, subscription mechanism, and verification semantics are not defined in v0.1; `verified`-tier interop across Gateways is deferred (see PHASE-0-REVIEW.md deferred questions).

Owners may also express *denylist* entries and per-operator overrides ("Operator X: read yes, actions no").

### Axis 3 — Economics (*at what price*)
- Per-resource-class and per-tier pricing: free / per-request / per-action / subscription pass; simulate-call pricing separately configurable.
- Settlement rails the owner accepts (x402, AP2-card, ...), payout configuration, and free-quota grants (e.g., "search is free, purchase carries fees, commercial crawlers pay per read").

### Axis 4 — Risk gates (*with what ceremony*)
Per risk class and per action, the owner chooses the execution ceremony. Floors from the spec §5.1 table can be raised, never lowered:

| Gate | Behavior |
|---|---|
| `auto` | Execute when protocol requirements met |
| `mandate` | Require a valid mandate with named scopes (floor for R2+) |
| `human_site` | Queue for a site-side human approval before commit |
| `threshold(x)` | `auto` below value/volume x, `human_site` above |
| `deny` | Action exists in manifest as visible-but-disabled, or is hidden entirely |

Plus operational limits: per-tier rate limits, concurrency caps, offer freeze windows, maintenance freezes ("no commits during deploy window").

### Axis 5 — Observability & accountability (*with what memory*)
- Append-only audit log of every agent interaction (who, what, mandate, outcome, revenue) with retention configuration.
- Receipt retention & export (regulatory formats a Phase 5 concern).
- Alerting: anomaly triggers (traffic spikes, repeated denials, simulate/commit divergence warnings), monitor subscriptions for the owner's own domain in transparency logs (catches impersonation).
- Kill switches: one command or toggle to suspend an action, a tier, or all agent access. The change takes effect immediately and is recorded in the log.

## 3. Illustrative policy sketch

```yaml
ajar_policy: 0.1
defaults: { audience: signed, price: "0", gate: auto }
content:
  - match: "/blog/**"        # public content, everyone reads free
    audience: anonymous
    license: { read: allow, train: deny }
  - match: "/docs/**"
    audience: anonymous
    price: { anonymous: "0.0005/req", signed: "0" }
  - match: "/account/**"     # never exposed
    expose: false
actions:
  search_trains:      { risk: R0, audience: anonymous, gate: auto }
  hold_seat:          { risk: R1, audience: signed,   gate: auto, ttl: PT15M }
  purchase_tickets:   { risk: R3, audience: verified, gate: threshold, threshold: { INR: 50000 },
                        mandate_scopes: [commerce.purchase.transport] }
  cancel_booking:     { risk: R2, audience: contracted, gate: human_site }
rates: { anonymous: 60/h, signed: 600/h, verified: 6000/h }
settlement: [x402]
audit: { retention: P2Y, alerts: [divergence, impersonation, spike] }
```

## 4. The owner journey (experience requirements)

1. **Install**: one command or plugin activation. Gateway crawls and drafts. Nothing is public yet.
2. **Review**: Console shows a coverage map ("94% of pages mapped, 3 templates need review"), a plain-language manifest summary ("Agents would be able to read your blog and product pages; nothing else"), and the draft action queue.
3. **Key ceremony**: guided owner-key generation, offline-key guidance, and operational key issuance.
4. **Approve and sign**: owner edits policy, signs it, and publishes the manifest. Logs are optional.
5. **Operate**: dashboard for traffic by tier/operator, revenue, denials, gated approvals, kill switches, and drift notifications.
6. **Evolve**: enable the first action, then metering, then standing contracts. Each step is explicit and reversible.

Hard UX requirements: every screen answers *"what exactly is exposed, to whom, at what price, with what ceremony?"*; every automated suggestion is labeled as a draft; every change is previewable and revertible; no dark patterns nudging owners toward more exposure.

## 5. What we deliberately delegate to owners (and why)

| Delegated entirely | Rationale |
|---|---|
| What to expose, hide, price | Only the owner knows their business; we'd be wrong at scale |
| Action wiring to real backends | Guessing write-endpoints is how disasters happen |
| Risk classification (within spec floors) | Owner bears the liability; owner sets the class. Misclassification shifts liability to them, which keeps classification honest |
| Trust-list curation for `verified` | A central "good agent" list would make us a gatekeeper |
| Hosting, uptime, scaling of their Gateway | Self-hosted sovereignty; we ship software, not dependence |

What we do NOT delegate: protocol floors (R2+ ceremonies can't be lowered), signature requirements, safe defaults, and the honesty of the Console (coverage/exposure reporting is not configurable into silence).

## 6. Positioning vs. proprietary owner-control products

CDN-integrated controls, such as per-crawler allow/block/charge and pay-per-use, validate owner demand. They mainly operate at the read/crawl layer and inside one vendor network. Ajar is the open, self-hosted counterpart for policy that extends from reading to actions, proof, and receipts. The two can run together: a site can use CDN crawl controls in front of an Ajar Gateway, and a CDN can offer a managed Ajar Gateway while the standard remains neutral.
