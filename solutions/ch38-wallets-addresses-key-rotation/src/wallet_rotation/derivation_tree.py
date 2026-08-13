"""BIP-32-style derivation tree over a parameterized signature primitive.

The chapter's running example walks a BIP-32 derivation path under
each of the six wallet candidates and reports which derivation
properties survive per primitive.

BIP-32 (per the original specification by Wuille, 2012) derives
child keys from a parent secret, a chain code, and an integer index
via HMAC-SHA-512. Two derivation modes:

- **Hardened.** The derivation function takes the parent SECRET, the
  chain code, and the index. Output bytes feed the child secret and
  the child chain code. The hardened mode is feasible for any
  primitive because the derivation operates on bytes alone.
- **Non-hardened.** The derivation function takes the parent PUBLIC
  key, the chain code, and the index. The output offsets a public
  key. A watcher with the parent public key (no parent secret) can
  derive child public keys. Non-hardened derivation requires that
  the primitive supports a public-key-only derivation map: a
  scalar-offset operation in the elliptic-curve case, or an
  equivalent hash-based offset for an Ed25519-like prime-order
  group.

The watch-only wallet property is equivalent to non-hardened
derivation: a wallet that holds only the parent public key can
derive child public keys for monitoring without ever holding the
parent secret.

The six-candidate set:

- ``ECDSA-secp256k1`` (legacy baseline) supports both modes.
  Non-hardened derivation works via scalar offset on the curve.
- ``ML-DSA-65`` per FIPS 204 supports hardened mode only. The
  signing key is a structured artifact (s_1, s_2, t, ...) without
  a public-key-only derivation map. Practical wallet designs over
  ML-DSA derive child seeds via HMAC and run keygen from each
  child seed; this is hardened-only.
- ``SLH-DSA-128s`` per FIPS 205 supports hardened mode only. Each
  signing operation traverses a hash hypertree from a fixed seed;
  child keys derive from a fresh seed via HMAC, never from a
  public-key-only operation.
- ``Ed25519+ML-DSA-65`` composite supports hardened mode only at
  the composite level. The Ed25519 component supports non-hardened
  derivation in isolation, but the ML-DSA component does not. A
  composite signature requires both halves; the composite as a
  whole is therefore hardened-only.
- ``XMSS-MT`` per RFC 8391 / NIST SP 800-208 supports hardened
  mode only. Derivation produces a fresh seed for each subtree;
  state management runs over the hypertree; no public-key-only
  derivation map exists.
- ``LMS`` per RFC 8554 / NIST SP 800-208 supports hardened mode
  only. Same rationale.

This module never instantiates a real signature scheme. It walks a
derivation PATH using HMAC-SHA-512 over a deterministic byte
representation and reports the structural properties surviving per
primitive. The point of the module is pedagogical: surface the
BIP-32 invariants that survive the move to post-quantum signing.
"""

import hmac
from hashlib import sha512
from typing import Dict, List, Tuple, TypedDict


class PrimitiveProperties(TypedDict):
    hardened: bool
    non_hardened: bool
    watch_only: bool
    rationale: str


PROPERTIES: Dict[str, PrimitiveProperties] = {
    "ECDSA-secp256k1": {
        "hardened": True,
        "non_hardened": True,
        "watch_only": True,
        "rationale": "scalar offset on the curve preserves a public-key-only derivation map",
    },
    "ML-DSA-65": {
        "hardened": True,
        "non_hardened": False,
        "watch_only": False,
        "rationale": "structured signing key without a public-key-only derivation map",
    },
    "SLH-DSA-128s": {
        "hardened": True,
        "non_hardened": False,
        "watch_only": False,
        "rationale": "hash hypertree derivation from a fresh seed at each subtree",
    },
    "Ed25519+ML-DSA-65": {
        "hardened": True,
        "non_hardened": False,
        "watch_only": False,
        "rationale": "composite is hardened-only because the ML-DSA component is hardened-only",
    },
    "XMSS-MT": {
        "hardened": True,
        "non_hardened": False,
        "watch_only": False,
        "rationale": "hypertree subtree derivation from a fresh seed per layer",
    },
    "LMS": {
        "hardened": True,
        "non_hardened": False,
        "watch_only": False,
        "rationale": "Merkle subtree derivation from a fresh seed per layer",
    },
}

PRIMITIVES: Tuple[str, ...] = tuple(PROPERTIES.keys())

HARDENED_OFFSET = 0x80000000
"""BIP-32 sets the high bit of the index to mark a hardened branch."""


def parse_path(path: str) -> List[Tuple[int, bool]]:
    """Parse a BIP-32 derivation path into a list of (index, hardened) tuples.

    Accepts the conventional notation ``"m/44'/0'/0'/0/0"``. The leading
    ``m`` denotes the master key. A trailing apostrophe marks a
    hardened branch.
    """
    assert path.startswith("m"), f"path must start with 'm': {path!r}"
    parts = path.split("/")[1:]  # drop the leading "m"
    out: List[Tuple[int, bool]] = []
    for raw in parts:
        if raw == "":
            continue
        hardened = raw.endswith("'")
        idx_str = raw[:-1] if hardened else raw
        idx = int(idx_str)
        assert 0 <= idx < HARDENED_OFFSET, f"index out of range: {raw!r}"
        out.append((idx, hardened))
    return out


def properties(primitive: str) -> PrimitiveProperties:
    """Return the BIP-32 property survival map for the candidate primitive."""
    assert primitive in PROPERTIES, f"unknown primitive: {primitive!r}"
    return PROPERTIES[primitive]


def derive_step(parent_secret: bytes, parent_chain_code: bytes, index: int, hardened: bool) -> Tuple[bytes, bytes]:
    """One step of BIP-32-style derivation using HMAC-SHA-512.

    Returns ``(child_secret, child_chain_code)`` where each is 32 bytes.

    Hardened mode hashes the parent secret, a 0x00 prefix byte, and
    the index with the hardened bit set, exactly per BIP-32 §3.

    Non-hardened mode is a pedagogical PLACEHOLDER for this module.
    Real BIP-32 non-hardened derivation hashes the SERIALIZED PARENT
    PUBLIC KEY plus the index, then offsets the parent public key on
    a primitive-specific group (scalar offset on secp256k1 for ECDSA).
    This module substitutes the parent secret as opaque bytes so the
    walk can continue past non-hardened steps without per-primitive
    public-key arithmetic. The bytes returned for non-hardened mode
    are NOT valid BIP-32 child keys; they exist only to keep the
    pedagogical walk's chain-code propagation structurally valid.
    The module's per-primitive ``properties()`` map and the per-step
    ``supported`` flag in ``derive()`` capture the actual derivation-
    survival decision the chapter describes.
    """
    assert len(parent_chain_code) == 32, "chain code must be 32 bytes"
    assert 0 <= index < HARDENED_OFFSET, "index must fit in 31 bits"
    if hardened:
        idx_bytes = (index | HARDENED_OFFSET).to_bytes(4, "big")
        data = b"\x00" + parent_secret + idx_bytes
    else:
        # Pedagogical placeholder. Real BIP-32 non-hardened derivation
        # hashes a 33-byte compressed parent public key plus the index;
        # the module substitutes parent_secret to keep the walk's chain
        # code propagation structurally valid past non-hardened steps.
        idx_bytes = index.to_bytes(4, "big")
        data = parent_secret + idx_bytes
    out = hmac.new(parent_chain_code, data, sha512).digest()
    return out[:32], out[32:]


def derive(primitive: str, master_seed: bytes, path: str) -> List[Dict[str, object]]:
    """Walk the derivation path under the candidate and return the chain.

    The first step expands the 64-byte master seed into the master
    secret and the master chain code per BIP-32. Each subsequent
    step applies one HMAC-SHA-512 derivation. The function flags
    any non-hardened step against a primitive that does not support
    non-hardened mode, but does NOT abort: the byte-level walk
    continues so the chapter's pedagogy can illustrate exactly
    where a wallet design has to switch to hardened-only.

    Returns a list of step records, one per derivation depth. The
    first record describes the master expansion; subsequent records
    describe each child step.
    """
    assert primitive in PROPERTIES, f"unknown primitive: {primitive!r}"
    assert len(master_seed) >= 16, "master seed must be at least 128 bits"

    master = hmac.new(b"Bitcoin seed", master_seed, sha512).digest()
    secret = master[:32]
    chain_code = master[32:]
    steps: List[Dict[str, object]] = [
        {
            "depth": 0,
            "kind": "master",
            "hardened": False,
            "supported": True,
            "secret_hex": secret.hex(),
            "chain_code_hex": chain_code.hex(),
        }
    ]

    parsed = parse_path(path)
    props = PROPERTIES[primitive]
    for depth, (idx, hardened) in enumerate(parsed, start=1):
        secret, chain_code = derive_step(secret, chain_code, idx, hardened)
        supported = hardened or props["non_hardened"]
        steps.append(
            {
                "depth": depth,
                "kind": "child",
                "index": idx,
                "hardened": hardened,
                "supported": supported,
                "secret_hex": secret.hex(),
                "chain_code_hex": chain_code.hex(),
            }
        )
    return steps


def watch_only_supported(primitive: str) -> bool:
    """Return whether a watch-only wallet is feasible under the primitive."""
    assert primitive in PROPERTIES, f"unknown primitive: {primitive!r}"
    return PROPERTIES[primitive]["watch_only"]


def evaluate(primitive: str) -> Dict[str, object]:
    """Combined property report for the candidate primitive.

    Returns a dict with the four pedagogical fields the chapter's
    inline Block 2 prints: the primitive name, the hardened-mode
    survival flag, the non-hardened-mode survival flag, and the
    watch-only wallet survival flag.
    """
    assert primitive in PROPERTIES, f"unknown primitive: {primitive!r}"
    props = PROPERTIES[primitive]
    return {
        "primitive": primitive,
        "hardened": props["hardened"],
        "non_hardened": props["non_hardened"],
        "watch_only": props["watch_only"],
        "rationale": props["rationale"],
    }
