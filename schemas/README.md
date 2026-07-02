# /schemas

Formal JSON Schemas (2020-12) extracted from `docs/03-PROTOCOL-SPEC.md` — the machine-checkable form of the spec.

**Status: empty by design.** Populated in Phase 0, task **T0.4**, only after the spec review pass (T0.1) closes. Do not author schemas before the prose spec stabilizes; the spec is the source of truth and schemas must cite its section numbers.

Planned files: `manifest.schema.json`, `view.schema.json`, `action.schema.json`, `mandate.schema.json`, `offer.schema.json`, `receipt.schema.json`, `policy.schema.json`, `error.schema.json`.

CI (set up in T0.9) validates everything in `/examples` against these schemas on every commit.
