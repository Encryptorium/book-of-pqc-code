"""SHAKE wrappers and the ML-DSA hash derivations (FIPS 204 §3.6, §6, §7).

ML-DSA needs exactly two symmetric primitives: SHAKE256 as the all-purpose hash
H (variable output) and SHAKE128 for the matrix expansion (in sampling.py). Every
domain-separated derivation (the KeyGen seed split, tr, mu, rho'', c-tilde) is a
thin call to H on a specific byte string. The byte-exact values are pinned by the
ACVP keyGen/sigGen vectors; here we check the primitives against FIPS 202 known
answers and the derivations for length/determinism/sensitivity.
"""

from __future__ import annotations

import hashlib

from mldsa.hashes import (
    shake128,
    shake256,
    H,
    integer_to_bytes,
    expand_keygen_seed,
    crh,
    message_representative,
    mask_seed,
    commitment_hash,
)


def test_shake_matches_hashlib() -> None:
    for data in (b"", b"abc", bytes(range(200))):
        assert shake128(data, 64) == hashlib.shake_128(data).digest(64)
        assert shake256(data, 64) == hashlib.shake_256(data).digest(64)


def test_shake_known_answers() -> None:
    # FIPS 202 known-answer prefixes for the empty message.
    assert shake128(b"", 32).hex() == (
        "7f9c2ba4e88f827d616045507605853ed73b8093f6efbc88eb1a6eacfa66ef26"
    )
    assert shake256(b"", 32).hex() == (
        "46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f"
    )


def test_H_is_shake256() -> None:
    assert H(b"encryptorium", 137) == shake256(b"encryptorium", 137)


def test_integer_to_bytes_little_endian() -> None:
    assert integer_to_bytes(0, 1) == b"\x00"
    assert integer_to_bytes(4, 1) == b"\x04"
    assert integer_to_bytes(258, 2) == b"\x02\x01"  # 258 = 0x0102, little-endian
    assert integer_to_bytes(1, 4) == b"\x01\x00\x00\x00"


def test_expand_keygen_seed_split() -> None:
    xi = bytes(range(32))
    rho, rho_prime, K = expand_keygen_seed(xi, k=4, l=4)
    assert len(rho) == 32 and len(rho_prime) == 64 and len(K) == 32
    # Deterministic.
    assert expand_keygen_seed(xi, 4, 4) == (rho, rho_prime, K)
    # The (k, l) domain-separation bytes change the output (FINAL FIPS 204).
    assert expand_keygen_seed(xi, 6, 5) != (rho, rho_prime, K)
    # Concatenation is exactly H(xi || k || l, 128).
    raw = H(xi + integer_to_bytes(4, 1) + integer_to_bytes(4, 1), 128)
    assert rho + rho_prime + K == raw


def test_derivation_lengths_and_determinism() -> None:
    pk = bytes(range(256)) * 5
    tr = crh(pk)
    assert len(tr) == 64 and crh(pk) == tr

    mprime = b"the quick brown fox"
    mu = message_representative(tr, mprime)
    assert len(mu) == 64
    assert mu == H(tr + mprime, 64)
    assert message_representative(tr, b"other") != mu

    K = bytes(32)
    rnd = bytes(32)
    rho2 = mask_seed(K, rnd, mu)
    assert len(rho2) == 64
    assert rho2 == H(K + rnd + mu, 64)

    for clen in (32, 48, 64):
        c = commitment_hash(mu, b"w1-bytes", clen)
        assert len(c) == clen
        assert c == H(mu + b"w1-bytes", clen)
