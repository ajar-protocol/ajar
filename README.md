# ajar - The Ajar Protocol Specification

This repo contains the vendor-neutral Ajar Protocol specification. If a rule is not here, it is not part of the protocol.

Ajar is an owner-controlled semantic layer over HTTPS. It defines a signed Capability Manifest at `/.well-known/ajar.json`, semantic Views via content negotiation, typed Actions with risk classes R0-R3, SIMULATE dry runs, two-phase Offer/Commit with dual-signed Receipts, principal-signed Mandates, and 402-native metering with pluggable settlement.

## Contents

| Path | What |
|---|---|
| `docs/03-PROTOCOL-SPEC.md` | The normative spec (v0.1 draft). Start here as an implementer |
| `docs/02-ARCHITECTURE.md` | End-to-end system design + canonical walkthrough |
| `docs/04-SECURITY-MODEL.md` | Threat catalogue, mitigations, accepted residuals |
| `docs/06-OWNER-CONTROL.md` | Owner-control policy model |
| `docs/01-RESEARCH.md` | Prior-art landscape and the honest novelty delta |
| `GLOSSARY.md` | Canonical terminology |
| `DECISIONS.md` | ADRs 001–017: why everything is the way it is |
| `schemas/` | JSON Schemas for manifests, views, actions, mandates, offers, receipts, policies, errors, and simulations |
| `examples/` | Golden examples, valid + deliberately invalid |
| `registries/` | Scope registry, error codes, settlement adapters |
| `test-vectors/` | Seed conformance-vector data and MUST coverage |
| `AEPs/` | Ajar Enhancement Proposals |

## Reading order
Implementer: spec → schemas → examples → conformance suite. Newcomer: [`planning`](https://github.com/ajar-protocol/planning) first, then `docs/02-ARCHITECTURE.md`, then the spec. Reviewer: `docs/04-SECURITY-MODEL.md` + `DECISIONS.md`.

## Validation

```bash
python -m pip install jsonschema
python tools/validate_examples.py
```

Expected result:

```text
Validated 10 valid examples, 5 invalid examples, 4 signing vectors, 10 core vectors, 6 runtime vectors, and 10 scope vectors.
```

CI runs the same validation for every push and pull request.

The workflow template is in `ci/validate.yml`. Copy it to
`.github/workflows/validate.yml` once the publishing account has workflow
permission enabled.

## Changing the protocol
Use AEPs; see `AEPs/README.md`. Anyone may propose changes, including independent implementers. Editorial fixes go by normal PR. Anything touching a MUST goes through an AEP.

## Machine consumption
This repo is also structured for automated consumption: stable heading IDs, one concept per section, and individually citable MUSTs. It is the source material for the planned `ajar-docs-mcp` server and for the Ajar views served by ajarprotocol.org.

License: split CC-BY-4.0 / Apache-2.0. See `LICENSE.md`.
