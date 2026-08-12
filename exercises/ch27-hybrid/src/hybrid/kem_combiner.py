"""X25519MLKEM768 hybrid KEM (RFC 10024).

Combines X25519 and ML-KEM-768 into a single KEM whose shared secret
is the HKDF-SHA256 output over ``ss_mlkem || ss_x25519`` plus a fixed
label. The wire format follows the TLS 1.3 Named Group codepoint
0x11EC:

- ``ClientHello`` keyshare: ``mlkem_ek || x25519_pk``, total 1216 bytes.
- ``ServerHello`` keyshare: ``mlkem_ct || x25519_pk_server``, total
  1120 bytes.

The security argument is Bindel/Brendel/Fischlin/Goncalves/Stebila
2019: if HKDF-SHA256 is a secure dual-PRF and at least one of X25519
or ML-KEM-768 is IND-CCA, the hybrid is IND-CCA.

Public API:

- ``hybrid_kem_keygen() -> (pk, sk)``: generate a hybrid keypair.
- ``hybrid_kem_encaps(pk) -> (ct, ss)``: encapsulate to ``pk``,
  returning ciphertext and 32-byte shared secret.
- ``hybrid_kem_decaps(sk, ct) -> ss``: decapsulate to 32-byte shared
  secret.

ML-KEM-768 is imported from ``solutions/ch11-mlkem/src/mlkem``. A pytest
``conftest.py`` adds that path to ``sys.path`` for tests; runtime
users of this module must ensure the same.
"""

import hashlib
import hmac
import os
import sys
from pathlib import Path

from .x25519 import x25519_base, x25519_scalarmult


_MLKEM_SRC = Path(__file__).resolve().parents[3] / "ch11-mlkem" / "src"
if str(_MLKEM_SRC) not in sys.path:
    sys.path.insert(0, str(_MLKEM_SRC))

from mlkem import (  # noqa: E402  (path manipulation above)
    ML_KEM_768,
    ml_kem_decaps_internal,
    ml_kem_encaps_internal,
    ml_kem_keygen_internal,
)


X25519MLKEM768_NAMED_GROUP = 0x11EC

_X25519_PK_BYTES = 32
_X25519_SK_BYTES = 32
_X25519_SS_BYTES = 32
_MLKEM768_EK_BYTES = 1184
_MLKEM768_DK_BYTES = 2400
_MLKEM768_CT_BYTES = 1088
_MLKEM768_SS_BYTES = 32

X25519MLKEM768_PK_BYTES = _MLKEM768_EK_BYTES + _X25519_PK_BYTES
X25519MLKEM768_CT_BYTES = _MLKEM768_CT_BYTES + _X25519_PK_BYTES
X25519MLKEM768_SS_BYTES = 32

_HKDF_LABEL = b"tls13 x25519_mlkem768"


def _hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    # EXERCISE: implement this function.
    #
    # HKDF-Extract is one HMAC-SHA256 call keyed by the salt over the input
    # keying material. An empty salt becomes 32 zero bytes, which is the RFC
    # 5869 default for a hash with a 32-byte output. Note which argument is
    # the HMAC key: the salt keys the MAC and the secret is the message, not
    # the other way round.
    #
    # Reference: Chapter 27, 'An X25519MLKEM768 handshake'
    #
    # Proved by:
    #   tests/ch27/test_hybrid_kem_roundtrip.py
    #   tests/ch27/test_hybrid_kem_kdf_consistency.py
    raise NotImplementedError("exercise: _hkdf_extract")


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    out = b""
    t = b""
    counter = 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        out += t
        counter += 1
    return out[:length]


def _combine(ss_mlkem: bytes, ss_x25519: bytes) -> bytes:
    ikm = ss_mlkem + ss_x25519
    prk = _hkdf_extract(b"", ikm)
    return _hkdf_expand(prk, _HKDF_LABEL, X25519MLKEM768_SS_BYTES)


def hybrid_kem_keygen(
    seed_mlkem_d: bytes | None = None,
    seed_mlkem_z: bytes | None = None,
    seed_x25519: bytes | None = None,
) -> tuple[bytes, bytes]:
    """Generate an X25519MLKEM768 keypair.

    Returns ``(pk, sk)`` where ``pk = mlkem_ek || x25519_pk`` (wire
    format per RFC 10024 Section 4.1) and ``sk = mlkem_dk ||
    x25519_sk``.
    """
    # EXERCISE: implement this function.
    #
    # Generate both component keypairs and concatenate each half in wire
    # order. Default any seed left as None to os.urandom(32); the seeds are
    # parameters only so tests can pin the output. Run ML-KEM-768 keygen on
    # (d, z) and X25519 base-point multiplication on the third seed, then
    # return pk = mlkem_ek || x25519_pk (1184 + 32 = 1216 bytes) and sk =
    # mlkem_dk || x25519_sk (2400 + 32 bytes).
    #
    # Reference: Chapter 27, 'The X25519MLKEM768 hybrid KEM'
    #
    # Proved by:
    #   tests/ch27/test_hybrid_kem_roundtrip.py
    #   tests/ch27/test_hybrid_kem_kdf_consistency.py
    raise NotImplementedError("exercise: hybrid_kem_keygen")


def _split_pk(pk: bytes) -> tuple[bytes, bytes]:
    if len(pk) != X25519MLKEM768_PK_BYTES:
        raise ValueError(f"pk must be {X25519MLKEM768_PK_BYTES} bytes")
    return pk[:_MLKEM768_EK_BYTES], pk[_MLKEM768_EK_BYTES:]


def _split_sk(sk: bytes) -> tuple[bytes, bytes]:
    if len(sk) != _MLKEM768_DK_BYTES + _X25519_SK_BYTES:
        raise ValueError("sk has wrong length")
    return sk[:_MLKEM768_DK_BYTES], sk[_MLKEM768_DK_BYTES:]


def _split_ct(ct: bytes) -> tuple[bytes, bytes]:
    if len(ct) != X25519MLKEM768_CT_BYTES:
        raise ValueError(f"ct must be {X25519MLKEM768_CT_BYTES} bytes")
    return ct[:_MLKEM768_CT_BYTES], ct[_MLKEM768_CT_BYTES:]


def hybrid_kem_encaps(
    pk: bytes,
    seed_mlkem: bytes | None = None,
    seed_x25519_ephemeral: bytes | None = None,
) -> tuple[bytes, bytes]:
    """Encapsulate to ``pk``. Returns ``(ciphertext, shared_secret)``.

    The ciphertext is ``mlkem_ct || x25519_pk_ephemeral`` per the TLS
    1.3 X25519MLKEM768 wire format; the shared secret is 32 bytes.
    """
    # EXERCISE: implement this function.
    #
    # Split the peer public key into its ML-KEM and X25519 halves, then run
    # both encapsulations. ML-KEM-768 encapsulation under a 32-byte message
    # seed yields a 32-byte secret and a 1088-byte ciphertext. For the
    # classical half, draw a fresh ephemeral scalar, publish its base-point
    # multiple, and take the shared secret as that scalar against the peer's
    # X25519 public key. Combine the two secrets and return (mlkem_ct ||
    # x25519_pk_ephemeral, shared_secret), 1120 bytes of ciphertext and 32
    # bytes of key. The ephemeral public key travels in the ciphertext
    # because the peer needs it to reproduce the same X25519 output.
    #
    # Reference: Chapter 27, 'The X25519MLKEM768 hybrid KEM'
    #
    # Proved by:
    #   tests/ch27/test_hybrid_kem_roundtrip.py
    #   tests/ch27/test_hybrid_kem_kdf_consistency.py
    raise NotImplementedError("exercise: hybrid_kem_encaps")


def hybrid_kem_decaps(sk: bytes, ct: bytes) -> bytes:
    """Decapsulate to a 32-byte shared secret."""
    # EXERCISE: implement this function.
    #
    # The mirror of encaps. Split the secret key and the ciphertext at their
    # fixed offsets, recover the ML-KEM secret by decapsulating the
    # 1088-byte ciphertext under the decapsulation key, recover the X25519
    # secret by multiplying the stored scalar against the sender's ephemeral
    # public key, and run the same combiner. ML-KEM decapsulation never
    # reports failure, so a tampered ciphertext yields a different shared
    # secret rather than an error; the round-trip test checks for a
    # mismatch, not an exception.
    #
    # Reference: Chapter 27, 'The X25519MLKEM768 hybrid KEM'
    #
    # Proved by:
    #   tests/ch27/test_hybrid_kem_roundtrip.py
    raise NotImplementedError("exercise: hybrid_kem_decaps")
