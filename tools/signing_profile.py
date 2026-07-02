#!/usr/bin/env python3
"""Ajar signing-profile helper for draft vectors.

This implements the v0.1 canonicalization rule for the JSON shapes in this
repo and a compact Ed25519 signer/verifier using only the Python standard
library. It is intended for reproducible spec vectors, not production key
management.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import sys
from pathlib import Path


Q = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, Q - 2, Q) % Q
I = pow(2, (Q - 1) // 4, Q)


def xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(D * y * y + 1, Q - 2, Q)
    x = pow(xx, (Q + 3) // 8, Q)
    if (x * x - xx) % Q != 0:
        x = (x * I) % Q
    if x & 1:
        x = Q - x
    return x


B = (xrecover(4 * pow(5, Q - 2, Q) % Q), 4 * pow(5, Q - 2, Q) % Q)


def point_add(p: tuple[int, int], q: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = p
    x2, y2 = q
    den_x = pow(1 + D * x1 * x2 * y1 * y2, Q - 2, Q)
    den_y = pow(1 - D * x1 * x2 * y1 * y2, Q - 2, Q)
    x3 = (x1 * y2 + x2 * y1) * den_x % Q
    y3 = (y1 * y2 + x1 * x2) * den_y % Q
    return x3, y3


def scalar_mult(point: tuple[int, int], scalar: int) -> tuple[int, int]:
    result = (0, 1)
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        scalar >>= 1
    return result


def encode_point(point: tuple[int, int]) -> bytes:
    x, y = point
    bits = y | ((x & 1) << 255)
    return bits.to_bytes(32, "little")


def decode_point(data: bytes) -> tuple[int, int]:
    if len(data) != 32:
        raise ValueError("Ed25519 public keys and R values must be 32 bytes")
    y = int.from_bytes(data, "little") & ((1 << 255) - 1)
    x = xrecover(y)
    if (x & 1) != (data[31] >> 7):
        x = Q - x
    if not is_on_curve((x, y)):
        raise ValueError("point is not on the Ed25519 curve")
    return x, y


def is_on_curve(point: tuple[int, int]) -> bool:
    x, y = point
    return (-x * x + y * y - 1 - D * x * x * y * y) % Q == 0


def secret_expand(seed: bytes) -> tuple[int, bytes]:
    if len(seed) != 32:
        raise ValueError("Ed25519 seed must be 32 bytes")
    digest = hashlib.sha512(seed).digest()
    scalar = int.from_bytes(digest[:32], "little")
    scalar &= (1 << 254) - 8
    scalar |= 1 << 254
    return scalar, digest[32:]


def public_key(seed: bytes) -> bytes:
    scalar, _prefix = secret_expand(seed)
    return encode_point(scalar_mult(B, scalar))


def ed25519_sign(seed: bytes, message: bytes) -> bytes:
    scalar, prefix = secret_expand(seed)
    public = public_key(seed)
    r = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % L
    encoded_r = encode_point(scalar_mult(B, r))
    k = int.from_bytes(hashlib.sha512(encoded_r + public + message).digest(), "little") % L
    s = (r + k * scalar) % L
    return encoded_r + s.to_bytes(32, "little")


def ed25519_verify(public: bytes, message: bytes, signature: bytes) -> bool:
    if len(public) != 32 or len(signature) != 64:
        return False
    try:
        decoded_r = decode_point(signature[:32])
        decoded_a = decode_point(public)
    except ValueError:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= L:
        return False
    k = int.from_bytes(hashlib.sha512(signature[:32] + public + message).digest(), "little") % L
    return scalar_mult(B, s) == point_add(decoded_r, scalar_mult(decoded_a, k))


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def unb64url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def signing_payload(artifact: dict, artifact_type: str) -> dict:
    payload = copy.deepcopy(artifact)
    if artifact_type in {"manifest", "mandate", "offer"}:
        payload.pop("signature", None)
    elif artifact_type == "receipt":
        payload.pop("site_signature", None)
        payload.pop("agent_signature", None)
    else:
        raise ValueError(f"unknown artifact type: {artifact_type}")
    return payload


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def command_public_key(args: argparse.Namespace) -> int:
    seed = bytes.fromhex(args.seed_hex)
    print(b64url(public_key(seed)))
    return 0


def command_sign(args: argparse.Namespace) -> int:
    seed = bytes.fromhex(args.seed_hex)
    artifact = load_json(args.artifact)
    payload = signing_payload(artifact, args.type)
    canonical = canonical_json_bytes(payload)
    signature = ed25519_sign(seed, canonical)
    vector = {
        "artifact_type": args.type,
        "artifact": str(args.artifact),
        "seed_hex": args.seed_hex,
        "public_key_b64url": b64url(public_key(seed)),
        "canonical_utf8": canonical.decode("utf-8"),
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_b64url": b64url(signature),
        "signature_valid": ed25519_verify(public_key(seed), canonical, signature),
    }
    print(json.dumps(vector, indent=2, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    public = unb64url(args.public_key)
    signature = unb64url(args.signature)
    artifact = load_json(args.artifact)
    canonical = canonical_json_bytes(signing_payload(artifact, args.type))
    if ed25519_verify(public, canonical, signature):
        print("signature-ok")
        return 0
    print("signature-failed", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ajar draft signing-profile helper")
    subcommands = parser.add_subparsers(dest="command", required=True)

    public = subcommands.add_parser("public-key")
    public.add_argument("seed_hex")
    public.set_defaults(func=command_public_key)

    sign = subcommands.add_parser("sign")
    sign.add_argument("--type", required=True, choices=["manifest", "mandate", "offer", "receipt"])
    sign.add_argument("--seed-hex", required=True)
    sign.add_argument("artifact", type=Path)
    sign.set_defaults(func=command_sign)

    verify = subcommands.add_parser("verify")
    verify.add_argument("--type", required=True, choices=["manifest", "mandate", "offer", "receipt"])
    verify.add_argument("--public-key", required=True)
    verify.add_argument("--signature", required=True)
    verify.add_argument("artifact", type=Path)
    verify.set_defaults(func=command_verify)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
