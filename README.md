# ajar - The Ajar Protocol Specification

This repo contains the vendor-neutral Ajar Protocol specification. If a rule is not here, it is not part of the protocol.

Ajar is an owner-controlled semantic layer over HTTPS. It defines a signed Capability Manifest at `/.well-known/ajar.json`, semantic Views via content negotiation, typed Actions with risk classes R0-R3, SIMULATE dry runs, two-phase Offer/Commit with dual-signed Receipts, principal-signed Mandates, and 402-native metering with pluggable settlement.

## Why this matters

A normal website has pages for people and private routes for its own app. An
agent can try to use that surface like a person, but it breaks down quickly. It
may scrape stale HTML, hit a form that changes state, reuse a user's browser
session, or buy something without a clean record of who approved it.

Ajar gives the site an agent-facing contract. The owner publishes what agents
may read and which actions exist. Agents sign their requests. Users and
organizations sign mandates that say exactly what an agent may do. For risky
work, the site must first simulate the result, then issue a signed offer, then
accept a signed commit. Both sides keep the receipt.

The auth rule is intentionally strict: public data can be exposed without a user
session; account data needs a linked account and user authority; writes,
purchases, legal changes, and personal-data actions need the full mandate and
receipt flow.

## Contents

| Path | What |
|---|---|
| `docs/03-PROTOCOL-SPEC.md` | The normative spec (v0.1 draft). Start here as an implementer |
| `docs/02-ARCHITECTURE.md` | End-to-end system design + canonical walkthrough |
| `docs/04-SECURITY-MODEL.md` | Threat catalogue, mitigations, accepted residuals |
| `docs/05-OWNER-CONTROL.md` | Owner-control policy model |
| `docs/01-RESEARCH.md` | Prior-art landscape and the honest novelty delta |
| `GLOSSARY.md` | Canonical terminology |
| `DECISIONS.md` | ADRs 001–019: why everything is the way it is |
| `schemas/` | JSON Schemas for manifests, views, actions, mandates, offers, receipts, policies, errors, and simulations |
| `examples/` | Golden examples, valid + deliberately invalid |
| `registries/` | Scope registry, error codes, settlement adapters |
| `test-vectors/` | Seed conformance-vector data and MUST coverage |
| `PHASE-0-BASELINE.md` | Local readiness evidence for the v0.1 draft baseline |
| `PHASE-0-REVIEW.md` | Phase 0 task-to-evidence review and remaining exit gates |
| `CONTRIBUTING.md` | Contribution rules, validation commands, and review invariants |
| `AEPs/` | Ajar Enhancement Proposals |

## Reading order
Implementer: spec → schemas → examples → conformance suite. Newcomer: [`planning`](https://github.com/ajar-protocol/planning) first, then `docs/02-ARCHITECTURE.md`, then the spec. Reviewer: `docs/04-SECURITY-MODEL.md` + `DECISIONS.md`.

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
make validate
python3 tools/check_phase0.py
```

Expected result:

```text
Validated 14 valid examples, 8 invalid examples, 4 signing vectors, 2 HTTP signature vectors, 5 extension vectors, 6 manifest check vectors, 11 core vectors, 25 runtime vectors, and 12 scope vectors.
MUST coverage OK: 24 requirements mapped.
```

`make validate` runs schema/example/vector validation, local Markdown link
checks, and Markdown hygiene checks. The same checks run in the hosted
validation workflow at `.github/workflows/validate.yml`; `ci/validate.yml` is
kept as a reviewable template copy.

## Changing the protocol
Use AEPs; see `AEPs/README.md`. Anyone may propose changes, including independent implementers. Editorial fixes go by normal PR. Anything touching a MUST goes through an AEP.

See `CONTRIBUTING.md` before opening a pull request.

## Machine consumption
This repo is also structured for automated consumption: stable heading IDs, one concept per section, and individually citable MUSTs. It is the source material for the planned `ajar-docs-mcp` server and for the Ajar views served by ajarprotocol.org.

License: split CC-BY-4.0 / Apache-2.0. See `LICENSE.md`.
