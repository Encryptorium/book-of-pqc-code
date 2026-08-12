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
    if salt == b"":
        salt = b"\x00" * 32
    return hmac.new(salt, ikm, hashlib.sha256).digest()


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
    d = seed_mlkem_d if seed_mlkem_d is not None else os.urandom(32)
    z = seed_mlkem_z if seed_mlkem_z is not None else os.urandom(32)
    x_sk = seed_x25519 if seed_x25519 is not None else os.urandom(32)
    mlkem_ek, mlkem_dk = ml_kem_keygen_internal(ML_KEM_768, d, z)
    x_pk = x25519_base(x_sk)
    pk = mlkem_ek + x_pk
    sk = mlkem_dk + x_sk
    return pk, sk


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
    mlkem_ek, x_pk_peer = _split_pk(pk)
    m = seed_mlkem if seed_mlkem is not None else os.urandom(32)
    ss_mlkem, ct_mlkem = ml_kem_encaps_internal(ML_KEM_768, mlkem_ek, m)
    x_sk_e = (
        seed_x25519_ephemeral
        if seed_x25519_ephemeral is not None
        else os.urandom(32)
    )
    x_pk_e = x25519_base(x_sk_e)
    ss_x25519 = x25519_scalarmult(x_sk_e, x_pk_peer)
    ss = _combine(ss_mlkem, ss_x25519)
    ct = ct_mlkem + x_pk_e
    return ct, ss


def hybrid_kem_decaps(sk: bytes, ct: bytes) -> bytes:
    """Decapsulate to a 32-byte shared secret."""
    mlkem_dk, x_sk = _split_sk(sk)
    ct_mlkem, x_pk_e = _split_ct(ct)
    ss_mlkem = ml_kem_decaps_internal(ML_KEM_768, mlkem_dk, ct_mlkem)
    ss_x25519 = x25519_scalarmult(x_sk, x_pk_e)
    return _combine(ss_mlkem, ss_x25519)
