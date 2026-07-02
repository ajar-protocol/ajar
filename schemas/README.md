# /schemas

Formal JSON Schemas (2020-12) extracted from `docs/03-PROTOCOL-SPEC.md` — the machine-checkable form of the spec.

Status: initial v0.1 draft schemas are present and validated against `/examples`.

Files:

- `common.schema.json`
- `manifest.schema.json`
- `view.schema.json`
- `action.schema.json`
- `mandate.schema.json`
- `offer.schema.json`
- `receipt.schema.json`
- `policy.schema.json`
- `error.schema.json`
- `simulation.schema.json`

Run:

```bash
python -m pip install jsonschema
python tools/validate_examples.py
```
