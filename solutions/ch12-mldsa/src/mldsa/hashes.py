"""Symmetric primitives and hash derivations for ML-DSA (FIPS 204 §3.7, §6, §7).

ML-DSA uses only the Keccak family: SHAKE256 is the general hash ``H`` (called with
whatever output length a step needs) and SHAKE128 is the extendable output used to
grow the public matrix A (see ``sampling.ExpandA``). There is no separate G/PRF/J
zoo as in ML-KEM; every derivation below is one call to ``H`` on a specific,
domain-separated byte string.

The derivations, all straight from FIPS 204:

* KeyGen splits ``H(xi || k || l, 128)`` into (rho, rho', K). The one-byte k and l
  suffixes are the domain separation added in the *final* standard (they were absent
  from the initial public draft), so a key generated under the draft differs.
* ``tr = H(pk, 64)`` binds the verifier's transcript to the whole public key.
* ``mu = H(tr || M', 64)`` is the message representative actually signed.
* ``rho'' = H(K || rnd || mu, 64)`` seeds the per-attempt mask y; ``rnd`` is 32 bytes,
  all-zero in the deterministic variant and random in the hedged variant.
* ``c-tilde = H(mu || w1Encode(w1), lambda/4)`` is the Fiat-Shamir challenge seed.
"""

from __future__ import annotations

import hashlib


def shake128(data: bytes, outlen: int) -> bytes:
    """SHAKE128 XOF squeezed to ``outlen`` bytes."""
    return hashlib.shake_128(data).digest(outlen)


def shake256(data: bytes, outlen: int) -> bytes:
    """SHAKE256 XOF squeezed to ``outlen`` bytes."""
    return hashlib.shake_256(data).digest(outlen)


def H(data: bytes, outlen: int) -> bytes:
    """FIPS 204's H: SHAKE256 with a caller-chosen output length."""
    return shake256(data, outlen)


def integer_to_bytes(x: int, length: int) -> bytes:
    """FIPS 204 IntegerToBytes: the little-endian ``length``-byte encoding of x."""
    assert x >= 0, f"integer_to_bytes: x must be non-negative, got {x}"
    return x.to_bytes(length, "little")


def expand_keygen_seed(xi: bytes, k: int, l: int) -> tuple[bytes, bytes, bytes]:
    """FIPS 204 Algorithm 6, step 1: (rho, rho', K) = H(xi || k || l, 128)."""
    assert len(xi) == 32, f"expand_keygen_seed: xi must be 32 bytes, got {len(xi)}"
    raw = H(xi + integer_to_bytes(k, 1) + integer_to_bytes(l, 1), 128)
    return raw[:32], raw[32:96], raw[96:128]


def crh(pk: bytes) -> bytes:
    """FIPS 204: tr = H(pk, 64), the collision-resistant hash of the public key."""
    return H(pk, 64)


def message_representative(tr: bytes, m_prime: bytes) -> bytes:
    """FIPS 204: mu = H(tr || M', 64)."""
    assert len(tr) == 64, f"message_representative: tr must be 64 bytes, got {len(tr)}"
    return H(tr + m_prime, 64)


def mask_seed(K: bytes, rnd: bytes, mu: bytes) -> bytes:
    """FIPS 204: rho'' = H(K || rnd || mu, 64)."""
    assert len(K) == 32, f"mask_seed: K must be 32 bytes, got {len(K)}"
    assert len(rnd) == 32, f"mask_seed: rnd must be 32 bytes, got {len(rnd)}"
    assert len(mu) == 64, f"mask_seed: mu must be 64 bytes, got {len(mu)}"
    return H(K + rnd + mu, 64)


def commitment_hash(mu: bytes, w1_bytes: bytes, c_tilde_len: int) -> bytes:
    """FIPS 204: c-tilde = H(mu || w1Encode(w1), lambda/4)."""
    assert len(mu) == 64, f"commitment_hash: mu must be 64 bytes, got {len(mu)}"
    return H(mu + w1_bytes, c_tilde_len)
