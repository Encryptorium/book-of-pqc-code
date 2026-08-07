"""The SHA-3 auxiliary functions H, G, PRF, XOF per FIPS 203 §4.1.

FIPS 203 names four auxiliary functions, all built on the Keccak
permutation exposed by Python's ``hashlib``:

- ``H``: SHA3-256, used to hash the encapsulation key ek and other
  32-byte values into 32-byte digests.
- ``G``: SHA3-512, used to derive a pair (K, r) of 32-byte values from
  the concatenation of the message m and H(ek) inside ML-KEM.Encaps.
- ``PRF``: SHAKE-256, used with a one-byte domain separator to expand
  a 32-byte seed into the byte string consumed by the centered binomial
  sampler CBD_eta.
- ``XOF``: SHAKE-128, used with a two-byte (i, j) domain separator to
  expand a 32-byte seed into the byte stream consumed by the rejection
  sampler that draws a matrix entry of A from uniform over R_q.

These are the only places the standard lets you pick a primitive. The
chapter treats SHA-3 as an opaque oracle; the internals of the Keccak
permutation live in the parent encryptorium repo's hash chapter, not
in Chapter 11.

No error handling on degenerate input. Byte-string inputs must have
the correct length; mismatched lengths crash the assertion and
produce a clear failure message.
"""

from __future__ import annotations

import hashlib


def H(data: bytes) -> bytes:
    """SHA3-256 applied to ``data``, returning 32 bytes (FIPS 203 §4.1).

    Used inside ML-KEM.KeyGen to hash the encapsulation key ek into a
    32-byte commitment stored inside dk, and inside ML-KEM.Decaps to
    recompute the same commitment for the FO re-encryption check.
    """
    return hashlib.sha3_256(data).digest()


def G(data: bytes) -> tuple[bytes, bytes]:
    """SHA3-512 applied to ``data``, returning ``(K, r)`` of 32 bytes each.

    FIPS 203 §4.1 defines G as SHA3-512 and names the two 32-byte halves
    of its output as a shared secret K and a coin seed r. Inside
    ML-KEM.Encaps the input is ``m || H(ek)``, so G couples the
    randomness r used for K-PKE.Encrypt to both the message m and the
    encapsulation key ek.
    """
    digest = hashlib.sha3_512(data).digest()
    assert len(digest) == 64, (
        f"G: SHA3-512 digest length must be 64, got {len(digest)}"
    )
    return digest[:32], digest[32:]


def PRF(eta: int, seed: bytes, nonce: int) -> bytes:
    """PRF_eta(seed, nonce) = SHAKE-256(seed || nonce)[:64 * eta].

    FIPS 203 §4.1 defines the pseudorandom function family
    ``PRF_eta(s, b) = SHAKE256(s || b, 64 * eta)``, used to expand a
    32-byte seed and a one-byte nonce into ``64 * eta`` bytes of CBD
    sampler input. The nonce acts as a domain separator so the same
    seed produces independent-looking output for different nonce
    values.
    """
    # EXERCISE: implement this function.
    #
    # Assert eta is 2 or 3, the seed is 32 bytes, and the nonce fits in a
    # single byte. Absorb seed || bytes([nonce]) into SHAKE-256 and squeeze
    # exactly 64 * eta bytes, which is the input length cbd_eta expects. The
    # one-byte nonce is the domain separator that keeps the per-row draws
    # from one sigma independent-looking.
    #
    # Reference: Chapter 11, 'Hash primitives: H, G, PRF, XOF, J' (FIPS 203 §4.1)
    #
    # Proved by:
    #   tests/ch11/test_hashes.py
    raise NotImplementedError("exercise: PRF")


def J(data: bytes) -> bytes:
    """SHAKE-256 applied to ``data``, truncated to 32 bytes (FIPS 203 §4.1).

    Used only inside ``ML-KEM.Decaps`` to derive the pseudorandom
    rejection key $\\bar{K} = J(z \\| c)$ that is returned when the
    re-encryption check fails. This is the implicit-rejection branch
    of the Fujisaki-Okamoto transform: instead of signalling a
    malformed ciphertext (which would leak information), Decaps
    returns a shared secret that depends pseudorandomly on the
    ciphertext and on the rejection seed $z$ stored inside ``dk``.
    """
    return hashlib.shake_256(data).digest(32)


def XOF(seed: bytes, outlen: int) -> bytes:
    """XOF(seed) = SHAKE-128(seed)[:outlen] (FIPS 203 §4.1).

    Exposed as a thin pedagogical wrapper around SHAKE-128 for use by
    chapter code blocks that want a one-line XOF call. The production
    rejection sampler inside ``sampling.sample_ntt`` does not call
    this wrapper; it instantiates ``hashlib.shake_128`` directly so
    it can request more output on demand when the initial squeeze
    under-produces. Both paths emit the same bytes for the same
    input, so the wrapper is correct when the caller asks for a
    fixed-length prefix up front.
    """
    assert outlen >= 0, f"XOF: outlen must be nonnegative, got {outlen}"
    shake = hashlib.shake_128()
    shake.update(seed)
    return shake.digest(outlen)
