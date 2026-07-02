# /examples

Golden examples — the living documentation of Ajar objects.

**Status: empty by design.** Populated in Phase 0, task **T0.5**, after schemas (T0.4) exist.

Planned contents:
- `manifests/` — three archetypes: blog (CORE), docs site (CORE+PAY), commerce (CORE+ACT+PAY)
- `scenario-tickets/` — the canonical 50-ticket walkthrough: mandate → simulation → offer → commit → receipt chain
- `invalid/` — deliberately broken artifacts (bad signature, expired offer, over-cap commit, sequence rollback), each documenting the rule it violates and the expected `Ajar-Error-Code`

Rule: every example is either validated by CI (valid set) or asserted to fail for its documented reason (invalid set). Examples that drift from the spec are bugs.
