# AGENTS.md - Spec Repository Contract

The org-wide `.github/AGENTS.md` and `.github/ENGINEERING.md` bind fully here.
This file adds the Ajar spec repository contract.

## Mission

This repo is the single source of truth for Ajar.
Changes here ripple into every implementation, conformance run, docs index, website page, and adoption tool.
The review bar is the highest in the org.

## Spec-change discipline

Normative changes require a complete same-PR update.
Normative changes include changes to:

- MUST
- SHOULD
- wire fields, headers, error codes, and scopes
- risk floors
- signing rules
- canonicalization
- compatibility behavior
- profile requirements
- registry values

The same PR MUST update all affected artifacts:

- schemas
- examples and fixtures
- conformance vectors
- `test-vectors/must-coverage.json` and `test-vectors/must-coverage.md`
- README and `tools/check_phase0.py` expected counts
- `GLOSSARY.md` when names or concepts change
- `DECISIONS.md` when design reasoning changes

Mirror the org `.github/CONTRIBUTING.md` `spec-change` rule.
Every spec-change PR cites the affected spec section.
No new MUST lands without a vector.
No behavior-changing edit is editorial.

## Crypto-change discipline

Canonicalization and signature behavior are the highest-risk surface.
Spec section 2.4, `tools/signing_profile.py`, and `test-vectors/crypto-signing.json` are the canonicalization/signature surface.
Any change there is `crypto-change`.
`crypto-change` work requires a dedicated human-reviewed PR.
Never bundle `crypto-change` with unrelated edits.
Never update signing vectors without explaining the canonical bytes change.
Never change canonicalization because a fixture is inconvenient.

## Registries

Registries are append-mostly.
Error codes MUST NOT be renumbered.
Error codes MUST NOT be repurposed.
Scopes MUST NOT be renamed casually.
Settlement adapter identifiers MUST NOT be repurposed.
New codes, scopes, adapters, or public extensions that affect interoperability require the AEP process under spec section 13.
Private extensions use the `x-<vendor>-` and `x-<vendor>.` rules in section 13.

## Wording rules

RFC-2119 terms are deliberate and uppercase; do not add MUST, SHOULD, MAY, MUST NOT, or SHOULD NOT casually.
Use one name per concept from `GLOSSARY.md`.
Do not introduce synonyms for protocol nouns.
Do not abbreviate protocol nouns.
Examples must use the same names as schemas and registries.
Anchors and heading IDs are stable API because the website and `ajar-docs-mcp` depend on headings.
Renaming a heading is a breaking change for consumers.
If a heading rename is necessary, do it deliberately and check `ajar-website` and `ajar-docs-mcp` in the same PR or linked PRs.

## Validation

Validation is binding.
Run `make validate && make phase0` before any PR.
For manifest-specific edits, also run `make manifest-check`.

Vector counts in `README.md` and `tools/check_phase0.py` MUST match the actual validation output.
`must-coverage` mappings MUST stay current.
Validation failures are blockers, not follow-up work.

## Never do this

- Never make silent normative edits while claiming style cleanup.
- Never add a MUST without a vector.
- Never change schemas without examples and vectors when behavior changes.
- Never renumber or repurpose registry values.
- Never delete a deferred-question row without an ADR resolving it.
- Never change canonicalization or signatures outside a dedicated `crypto-change` PR.
- Never rename headings without checking website and docs MCP consumers.
- Never let implementation convenience override the spec contract.
