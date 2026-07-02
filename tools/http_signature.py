#!/usr/bin/env python3
"""Minimal Ajar HTTP Message Signature vector helper.

This is a constrained RFC 9421-style helper for spec vectors. It covers the
components Ajar requires for the v0.1 request-signing example.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from signing_profile import b64url, ed25519_sign, ed25519_verify, public_key, unb64url


DEFAULT_COVERED = ["@method", "@target-uri", "signature-agent", "ajar-date"]


def component_value(request: dict, component: str) -> str:
    if component == "@method":
        return request["method"].upper()
    if component == "@target-uri":
        return request["target_uri"]
    headers = {key.lower(): value for key, value in request.get("headers", {}).items()}
    if component in headers:
        return headers[component]
    raise KeyError(f"covered component not present in request: {component}")


def signature_params(covered: list[str], created: int, keyid: str, tag: str = "ajar") -> str:
    covered_value = " ".join(f'"{component}"' for component in covered)
    return f"({covered_value});created={created};keyid=\"{keyid}\";tag=\"{tag}\";alg=\"ed25519\""


def signature_base(request: dict, covered: list[str], created: int, keyid: str, tag: str = "ajar") -> bytes:
    params = signature_params(covered, created, keyid, tag)
    lines = [f'"{component}": {component_value(request, component)}' for component in covered]
    lines.append(f'"@signature-params": {params}')
    return "\n".join(lines).encode("utf-8")


def sign_request(request: dict, seed: bytes, covered: list[str], created: int, keyid: str, tag: str = "ajar") -> dict:
    base = signature_base(request, covered, created, keyid, tag)
    signature = ed25519_sign(seed, base)
    return {
        "signature_input": f"ajar={signature_params(covered, created, keyid, tag)}",
        "signature": f"ajar=:{b64url(signature)}:",
        "signature_base": base.decode("utf-8"),
        "signature_b64url": b64url(signature),
        "public_key_b64url": b64url(public_key(seed)),
    }


def verify_request(request: dict, public_key_b64url: str, signature_b64url: str, covered: list[str], created: int, keyid: str, tag: str = "ajar") -> bool:
    base = signature_base(request, covered, created, keyid, tag)
    return ed25519_verify(unb64url(public_key_b64url), base, unb64url(signature_b64url))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def command_sign(args: argparse.Namespace) -> int:
    request = load_json(args.request)
    result = sign_request(request, bytes.fromhex(args.seed_hex), args.covered, args.created, args.keyid)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    request = load_json(args.request)
    if verify_request(request, args.public_key, args.signature, args.covered, args.created, args.keyid):
        print("http-signature-ok")
        return 0
    print("http-signature-failed", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ajar HTTP signature vector helper")
    subcommands = parser.add_subparsers(dest="command", required=True)

    sign = subcommands.add_parser("sign")
    sign.add_argument("--seed-hex", required=True)
    sign.add_argument("--created", type=int, required=True)
    sign.add_argument("--keyid", required=True)
    sign.add_argument("--covered", action="append", default=DEFAULT_COVERED)
    sign.add_argument("request", type=Path)
    sign.set_defaults(func=command_sign)

    verify = subcommands.add_parser("verify")
    verify.add_argument("--public-key", required=True)
    verify.add_argument("--signature", required=True)
    verify.add_argument("--created", type=int, required=True)
    verify.add_argument("--keyid", required=True)
    verify.add_argument("--covered", action="append", default=DEFAULT_COVERED)
    verify.add_argument("request", type=Path)
    verify.set_defaults(func=command_verify)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
