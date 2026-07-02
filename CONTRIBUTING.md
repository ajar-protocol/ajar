# Contributing To Ajar

This repository contains the protocol specification and supporting artifacts.
Changes should be small, reviewable, and tied to a spec section, task, issue, or
AEP.

## Before Opening A Pull Request

- Read `README.md`, `docs/03-PROTOCOL-SPEC.md`, `GLOSSARY.md`, and
  `DECISIONS.md` for the area you are changing.
- Reference the relevant planning task, issue, AEP, or spec section.
- Keep the change focused. Separate editorial cleanup from normative behavior
  changes.
- Do not include secrets, real private keys, real mandates, private receipts, or
  customer data.
- Check license compatibility before adding dependencies, copied text, or
  generated artifacts.

## Protocol Change Rules

- Editorial fixes can use a normal pull request.
- Any change to a MUST, SHOULD, wire field, schema rule, registry entry, risk
  floor, signing rule, or compatibility rule needs matching updates to the spec,
  schemas, examples, vectors, and docs.
- New interoperability-affecting behavior goes through the AEP process in
  `AEPs/README.md`.
- ADRs in `DECISIONS.md` explain durable design choices. Update or supersede an
  ADR when a change alters the reasoning behind the protocol.

## Validation

Run the local checks before requesting review:

```bash
python3 -m pip install -r requirements-dev.txt
make validate
make phase0
```

For manifest-specific edits, also run:

```bash
make manifest-check
```

## Review Invariants

Reviewers should reject changes that break these invariants:

- Owner approval remains the root of exposure and action publication.
- Verification, parsing, and policy failures fail closed.
- Durable artifacts are signed with the canonical profile.
- R1+ actions keep the required SIMULATE, idempotency, and risk-floor behavior.
- R2/R3-equivalent fallback actions require explicit human confirmation.
- Owner-deployed software does not add undeclared telemetry.

## Sign-Off

Commits should include a Developer Certificate of Origin sign-off:

```bash
git commit -s
```
