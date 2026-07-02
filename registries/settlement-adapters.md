# Settlement Adapter Registry v1

Normative source: `docs/03-PROTOCOL-SPEC.md` sections 3, 7, and 8.3.

Ajar does not move money. A settlement adapter identifies the external payment
or accounting rail whose proof is bound into an Offer or Receipt.

| Adapter | Semantics | Proof reference |
|---|---|---|
| `x402` | HTTP 402 challenge/response settlement | Payment response or receipt id from the x402 flow |
| `ap2-card` | Card-network settlement through an AP2-compatible mandate | AP2 payment mandate or payment token reference |
| `mpp` | Machine-payment session or recurring settlement | Session id and settlement receipt |
| `offline-invoice` | Contracted invoice flow outside real-time payment rails | Invoice id and counterparty contract reference |
| `none` | No settlement required | Used only for zero-cost reads/actions |

Adapters MUST NOT weaken Ajar's mandate, offer, or receipt checks. If a payment
rail says payment succeeded but the Ajar commit binding is invalid, the Ajar
operation still fails.

New public adapters require an AEP. Private adapters MUST use
`x-<vendor>-<adapter>`.
