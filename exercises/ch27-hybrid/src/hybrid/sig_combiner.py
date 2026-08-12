"""ML-DSA-65+Ed25519 explicit-composite signature (AND-mode).

Construction per draft-ietf-lamps-pq-composite-sigs-19 (April 2026),
algorithm id ``id-MLDSA65-Ed25519-SHA512`` (Section 6, OID
1.3.6.1.5.5.7.6.48). The serialized composite signature is
``mldsa_sig || ed_sig`` per Section 4.3; verify returns True only
when both component signatures validate (AND-mode). The serialized
composite public key is ``mldsa_pk || ed_pk``. OR-mode is out of
scope: the transition-period threat model assumes an attacker may
break one component but not both simultaneously.

The signing input is a composite message representative

    M' = Prefix || Label || len(ctx) || ctx || PH(M)

per Section 2.2, where Prefix is the 32-byte ASCII constant
``CompositeAlgorithmSignatures2025``, Label is the algorithm-specific
string ``COMPSIG-MLDSA65-Ed25519-SHA512``, ctx is an application
context of at most 255 bytes, and PH is SHA-512 for this combination.
Both signers receive M' (ML-DSA additionally binds Label as its
context).

Public API:

- ``composite_sig_keygen(seed_ed, seed_mldsa) -> (pk, sk)``.
- ``composite_sig_sign(sk, message, ctx=b'') -> bytes``: produce a
  composite signature of ``MLDSA65_SIG_BYTES + 64`` bytes.
- ``composite_sig_verify(pk, message, signature, ctx=b'') -> bool``:
  AND-mode verification.

ML-DSA-65 is stubbed (see ``mldsa_stub.py``) by choice, not by absence:
``solutions/ch12-mldsa`` ships the real FIPS 204 implementation and can
be swapped in. The combiner semantics, the serialization order, and the
message representative M' are real; only the underlying ML-DSA
signature scheme is a placeholder.
"""

import hashlib

from .ed25519 import ed25519_keygen, ed25519_sign, ed25519_verify
from .mldsa_stub import (
    MLDSA65_PK_BYTES,
    MLDSA65_SIG_BYTES,
    MLDSA65_SK_BYTES,
    mldsa65_keygen_stub,
    mldsa65_sign_stub,
    mldsa65_verify_stub,
)


_ED_PK_BYTES = 32
_ED_SK_BYTES = 32
_ED_SIG_BYTES = 64

COMPOSITE_PK_BYTES = MLDSA65_PK_BYTES + _ED_PK_BYTES
COMPOSITE_SK_BYTES = MLDSA65_SK_BYTES + _ED_SK_BYTES
COMPOSITE_SIG_BYTES = MLDSA65_SIG_BYTES + _ED_SIG_BYTES

_PREFIX = b"CompositeAlgorithmSignatures2025"
_LABEL = b"COMPSIG-MLDSA65-Ed25519-SHA512"


def _message_representative(message: bytes, ctx: bytes) -> bytes:
    """Build M' = Prefix || Label || len(ctx) || ctx || SHA-512(message)."""
    # EXERCISE: implement this function.
    #
    # Build M' = Prefix || Label || len(ctx) || ctx || SHA-512(message) from
    # the two module constants. The context length is a single byte, so a
    # ctx longer than 255 bytes cannot be encoded and must raise ValueError.
    # Both component signers receive M' rather than the raw message:
    # prefixing the algorithm-specific label is what stops a signature made
    # under one composite combination being replayed under another.
    #
    # Reference: draft-ietf-lamps-pq-composite-sigs-19 Section 2.2, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: _message_representative")


def composite_sig_keygen(
    seed_ed: bytes,
    seed_mldsa: bytes,
) -> tuple[bytes, bytes]:
    """Derive an explicit-composite keypair from two 32-byte seeds.

    Returns ``(pk, sk)`` where ``pk = mldsa_pk || ed_pk`` and
    ``sk = mldsa_sk || ed_seed`` per the LAMPS draft serialization
    order.
    """
    # EXERCISE: implement this function.
    #
    # Derive each component keypair from its own 32-byte seed and
    # concatenate with the post-quantum half first: pk = mldsa_pk || ed_pk
    # (1952 + 32) and sk = mldsa_sk || ed_seed (4032 + 32). Two independent
    # seeds, not one split in half. Section 3.1 of the draft forbids reusing
    # either component key in a standalone or differently-combined context,
    # so these keys are dedicated to this composite identifier.
    #
    # Reference: draft-ietf-lamps-pq-composite-sigs-19 Section 3.1, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: composite_sig_keygen")


def _split_pk(pk: bytes) -> tuple[bytes, bytes]:
    if len(pk) != COMPOSITE_PK_BYTES:
        raise ValueError(f"composite pk must be {COMPOSITE_PK_BYTES} bytes")
    return pk[:MLDSA65_PK_BYTES], pk[MLDSA65_PK_BYTES:]


def _split_sk(sk: bytes) -> tuple[bytes, bytes]:
    if len(sk) != COMPOSITE_SK_BYTES:
        raise ValueError(f"composite sk must be {COMPOSITE_SK_BYTES} bytes")
    return sk[:MLDSA65_SK_BYTES], sk[MLDSA65_SK_BYTES:]


def _split_sig(sig: bytes) -> tuple[bytes, bytes]:
    if len(sig) != COMPOSITE_SIG_BYTES:
        raise ValueError(f"composite sig must be {COMPOSITE_SIG_BYTES} bytes")
    return sig[:MLDSA65_SIG_BYTES], sig[MLDSA65_SIG_BYTES:]


def composite_sig_sign(sk: bytes, message: bytes, ctx: bytes = b"") -> bytes:
    """Produce an AND-mode composite signature over ``message``.

    Returns ``mldsa_sig || ed_sig`` per draft-19 Section 4.3.
    """
    # EXERCISE: implement this function.
    #
    # Split the composite secret key, build M' once, sign it with both
    # components, and return mldsa_sig || ed_sig. The ML-DSA signature comes
    # first, so the 3373-byte result splits at byte 3309. Both signers see
    # the same M', which is what binds the two halves to one message.
    #
    # Reference: draft-ietf-lamps-pq-composite-sigs-19 Section 4.3, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: composite_sig_sign")


def composite_sig_verify(
    pk: bytes, message: bytes, signature: bytes, ctx: bytes = b""
) -> bool:
    """Return True iff BOTH component signatures verify.

    Wrong-sized ``pk`` or ``signature`` inputs raise ``ValueError``
    from the split helpers. Toy-code convention: bad lengths are a
    caller bug and should crash loudly, not silently return False.
    """
    # EXERCISE: implement this function.
    #
    # AND-mode: split the public key and the signature at their fixed
    # offsets, rebuild M', run both component verifiers, and return True
    # only when both returned True. Compute both results before combining
    # them rather than letting Python's `and` short-circuit past the second
    # verifier. Let the split helpers raise ValueError on a wrong-sized
    # input instead of catching it and returning False; a mis-sized
    # signature is a caller bug, and swallowing it hides the difference
    # between a malformed input and a genuine forgery attempt.
    #
    # Reference: draft-ietf-lamps-pq-composite-sigs-19 Section 4.3, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: composite_sig_verify")
