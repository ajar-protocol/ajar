# AEPs — Ajar Enhancement Proposals

The only way normative protocol changes happen. Anyone may submit one — independent Gateway/Kernel implementers explicitly included.

## Process
1. **Discuss** — open a GitHub Discussion; sanity-check the idea against `DECISIONS.md` and the [`planning`](https://github.com/ajar-protocol/planning) repo (does a healthy standard already own this? then propose a bridge instead).
2. **Draft** — PR adding `AEPs/AEP-XXXX-short-title.md` using the template below. Status: `draft`.
3. **Review** — maintainers + community; must address: spec text delta, schema delta, conformance vectors, security-model delta, backward compatibility, at least one implementation sketch.
4. **Accept/Reject** — accepted AEPs merge with status `accepted`; the spec/schema/vector changes land in the *same or linked* PRs. Rejected AEPs stay in the repo with rationale (rejections are documentation).
5. **Ship** — status `final` when released in a spec version.

## Template
```markdown
# AEP-XXXX: Title
- Status: draft | accepted | rejected | final
- Author(s): name/handle
- Created: YYYY-MM-DD
- Spec sections affected:
- Profiles affected: CORE | ACT | PAY | FED

## Motivation      (the gap; why bridging an existing standard doesn't cover it)
## Specification   (exact normative text changes; MUST/SHOULD language)
## Schemas         (JSON Schema deltas)
## Conformance     (new/changed vectors)
## Security        (threat-model delta per docs/04)
## Compatibility   (version impact per ADR/versioning policy)
## Reference sketch(es)
## Alternatives considered
```
Numbering: next integer; `AEP-0001` is reserved for ratifying spec v0.1 as published.
