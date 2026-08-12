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
    if len(ctx) > 255:
        raise ValueError("composite ctx must be at most 255 bytes")
    ph = hashlib.sha512(message).digest()
    return _PREFIX + _LABEL + bytes([len(ctx)]) + ctx + ph


def composite_sig_keygen(
    seed_ed: bytes,
    seed_mldsa: bytes,
) -> tuple[bytes, bytes]:
    """Derive an explicit-composite keypair from two 32-byte seeds.

    Returns ``(pk, sk)`` where ``pk = mldsa_pk || ed_pk`` and
    ``sk = mldsa_sk || ed_seed`` per the LAMPS draft serialization
    order.
    """
    ed_pk, ed_sk = ed25519_keygen(seed_ed)
    mldsa_pk, mldsa_sk = mldsa65_keygen_stub(seed_mldsa)
    return mldsa_pk + ed_pk, mldsa_sk + ed_sk


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
    mldsa_sk, ed_sk = _split_sk(sk)
    m_prime = _message_representative(message, ctx)
    mldsa_sig = mldsa65_sign_stub(mldsa_sk, m_prime)
    ed_sig = ed25519_sign(ed_sk, m_prime)
    return mldsa_sig + ed_sig


def composite_sig_verify(
    pk: bytes, message: bytes, signature: bytes, ctx: bytes = b""
) -> bool:
    """Return True iff BOTH component signatures verify.

    Wrong-sized ``pk`` or ``signature`` inputs raise ``ValueError``
    from the split helpers. Toy-code convention: bad lengths are a
    caller bug and should crash loudly, not silently return False.
    """
    mldsa_pk, ed_pk = _split_pk(pk)
    mldsa_sig, ed_sig = _split_sig(signature)
    m_prime = _message_representative(message, ctx)
    mldsa_ok = mldsa65_verify_stub(mldsa_pk, m_prime, mldsa_sig)
    ed_ok = ed25519_verify(ed_pk, m_prime, ed_sig)
    return mldsa_ok and ed_ok
