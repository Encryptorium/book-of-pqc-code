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
    # EXERCISE: implement this function.
    #
    # Assert the path starts with 'm', then split on '/' and drop that first
    # element. Skip empty components so a bare 'm' yields the empty list and
    # a trailing slash is harmless. A component ending in an apostrophe is
    # hardened: strip the apostrophe before int() and record the flag
    # alongside the index. Assert the parsed index is below HARDENED_OFFSET;
    # the hardened bit is set by derive_step, not carried in the number, so
    # an index at or above 2**31 is a malformed path rather than a hardened
    # branch.
    #
    # Reference: Chapter 38, 'BIP-32 derivation, hardened versus non-hardened, watch-only'
    #
    # Proved by:
    #   tests/ch38/test_derivation_tree.py
    raise NotImplementedError("exercise: parse_path")


def properties(primitive: str) -> PrimitiveProperties:
    """Return the BIP-32 property survival map for the candidate primitive."""
    # EXERCISE: implement this function.
    #
    # Assert the primitive is in PROPERTIES and return its row. The table is
    # the chapter's survival map: ECDSA-secp256k1 alone carries non_hardened
    # and watch_only True, because a child public key is the parent point
    # plus t*G. Every post-quantum row is hardened-only, including the
    # composite, whose ML-DSA half forces the whole composite hardened-only
    # even though Ed25519 in isolation would not.
    #
    # Reference: Chapter 38, 'BIP-32 derivation, hardened versus non-hardened, watch-only'
    #
    # Proved by:
    #   tests/ch38/test_derivation_tree.py
    raise NotImplementedError("exercise: properties")


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
    # EXERCISE: implement this function.
    #
    # Expand the master seed once with HMAC-SHA-512 keyed on the literal
    # b'Bitcoin seed', splitting the digest into the master secret and
    # master chain code, and emit that as a depth-0 record with kind
    # 'master', hardened False, supported True. Then walk parse_path,
    # calling derive_step at each level and carrying the new secret and
    # chain code forward, appending a depth-numbered record with kind
    # 'child' and the step's index. A step is supported when it is hardened
    # or when the primitive's non_hardened property holds; record the flag
    # but do not abort on an unsupported step, because the point of the walk
    # is to show exactly which levels of m/44'/0'/0'/0/0 break rather than
    # to refuse to run. Both byte fields are recorded as hex.
    #
    # Reference: Chapter 38, 'Design the derivation tree'
    #
    # Proved by:
    #   tests/ch38/test_derivation_tree.py
    raise NotImplementedError("exercise: derive")


def watch_only_supported(primitive: str) -> bool:
    """Return whether a watch-only wallet is feasible under the primitive."""
    # EXERCISE: implement this function.
    #
    # Return the primitive's watch_only flag after the membership assert.
    # The flag tracks non_hardened exactly, because the two are the same
    # property seen from either end: a watcher holding only the parent
    # public key can derive child public keys precisely when a
    # public-key-only derivation map exists. ECDSA-secp256k1 is the only
    # True row, which is why the chapter treats the open-ended watch-only
    # wallet as a casualty of the migration.
    #
    # Reference: Chapter 38, 'BIP-32 derivation, hardened versus non-hardened, watch-only'
    #
    # Proved by:
    #   tests/ch38/test_derivation_tree.py
    raise NotImplementedError("exercise: watch_only_supported")


def evaluate(primitive: str) -> Dict[str, object]:
    """Combined property report for the candidate primitive.

    Returns a dict with the four pedagogical fields the chapter's
    inline Block 2 prints: the primitive name, the hardened-mode
    survival flag, the non-hardened-mode survival flag, and the
    watch-only wallet survival flag.
    """
    # EXERCISE: implement this function.
    #
    # Assemble the report the chapter's per-primitive summary prints:
    # primitive, hardened, non_hardened, watch_only, rationale. Read the row
    # out of PROPERTIES once and copy the four fields across rather than
    # calling the three accessors, so the report is one table lookup.
    #
    # Reference: Chapter 38, 'BIP-32 derivation, hardened versus non-hardened, watch-only'
    #
    # Proved by:
    #   tests/ch38/test_derivation_tree.py
    raise NotImplementedError("exercise: evaluate")
