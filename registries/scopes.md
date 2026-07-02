# Scope Registry v1

Normative source: `docs/03-PROTOCOL-SPEC.md` sections 5 and 8.1.

A scope is a dotted permission string carried in a Mandate and required by an
Action. A scope grants the exact named scope and any child scope only when it
ends in `.*`.

## Matching Rules

Given a mandate scope `M` and an action-required scope `R`:

1. `M == R` matches.
2. `M` ending in `.*` matches every `R` consisting of `M`'s segments before `.*` followed by one or more additional segments.
3. Wildcards are suffix-only. `commerce.*.ticket` is invalid.
4. Any matching entry in `constraints.forbidden` overrides an allowed scope.
5. `x-<vendor>.*` scopes are private extensions and never match core scopes.

Matching is segment-wise, never a raw string prefix: `commerce.purchase.*` does
not match `commerce.purchaseextra.x`, and it does not match the bare parent
`commerce.purchase`.

Examples:

| Mandate scope | Required scope | Verdict |
|---|---|---|
| `commerce.purchase.*` | `commerce.purchase.transport` | allow |
| `commerce.purchase.*` | `commerce.purchase.transport.rail` | allow |
| `commerce.purchase.*` | `commerce.purchase` | deny |
| `commerce.purchase.transport` | `commerce.purchase.transport` | allow |
| `commerce.purchase.transport` | `commerce.purchase.event` | deny |
| `content.read.*` | `content.write.comment` | deny |
| `data.export.*` with forbidden `data.export.user` | `data.export.user` | deny |

## Core Scopes

| Scope | Semantics | Typical risk |
|---|---|---|
| `content.read.page` | Read a single semantic View for a content URL | R0 |
| `content.read.index` | Read View Index metadata and chunk hashes | R0 |
| `content.read.search` | Search declared site content | R0 |
| `content.read.product` | Read product or catalog facts | R0 |
| `content.read.price` | Read price and availability facts | R0 |
| `content.write.comment` | Create a user-visible comment or review | R2 |
| `content.write.draft` | Create a private draft owned by the principal | R1 |
| `commerce.cart.read` | Read cart state | R0 |
| `commerce.cart.modify` | Add, remove, or update cart items | R1 |
| `commerce.quote.create` | Generate a quote without reservation or charge | R0 |
| `commerce.hold.create` | Hold inventory temporarily | R1 |
| `commerce.purchase.transport` | Buy travel or transport inventory | R3 |
| `commerce.purchase.goods` | Buy physical or digital goods | R3 |
| `commerce.purchase.event` | Buy event tickets or admissions | R3 |
| `commerce.cancel.order` | Cancel an existing order | R2 |
| `commerce.refund.request` | Request refund or return workflow | R2 |
| `communication.message.send` | Send a message, email, or notification | R2 |
| `communication.subscription.modify` | Change mailing or alert subscriptions | R1 |
| `account.profile.read` | Read account profile data | R0 |
| `account.profile.update` | Update account profile fields | R2 |
| `account.auth.session` | Create or modify an authenticated session | R3 |
| `data.export.user` | Export principal-owned user data | R2 |
| `data.delete.user` | Delete principal-owned user data | R2 |
| `data.consent.modify` | Change data-sharing or training consent | R2 |

## Extension Procedure

New core scopes require an AEP. Private scopes MUST start with `x-<vendor>.`
and include a stable owner contact in the manifest or implementation docs.
