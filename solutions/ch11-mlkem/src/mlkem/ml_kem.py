"""ML-KEM's internal algorithms, from FIPS 203 §6.

ML-KEM lifts the IND-CPA K-PKE of §5 to IND-CCA2 via the Fujisaki-
Okamoto transform in its implicit-rejection form: a failed
re-encryption check returns a pseudorandom key rather than the
explicit failure symbol the traditional transform returns. In the
Hofheinz-Hovelmanns-Kiltz notation that is the "not-perp" family
rather than the "perp" one, and the m subscript applies as well,
because the shared secret is derived from the message and the
encapsulation key without the ciphertext. Three internal routines
accept explicit seeds so they can be matched byte-for-byte against
the NIST ACVP test vectors:

- ``ml_kem_keygen_internal(params, d, z)``: wraps ``K_PKE.KeyGen(d)``
  and packages the result with ``H(ek_PKE)`` and the rejection seed
  ``z``. Returns ``(ek, dk)``.
- ``ml_kem_encaps_internal(params, ek, m)``: derandomizes
  ``K_PKE.Encrypt`` from the message seed ``m``. The shared secret
  ``K`` and the coin seed ``r`` are the two 32-byte halves of
  ``G(m || H(ek))``, so encapsulation depends on both the message
  chosen by the encapsulator and the public key's commitment.
  Returns ``(K, c)``.
- ``ml_kem_decaps_internal(params, dk, c)``: decrypts the K-PKE
  layer, re-runs ``K_PKE.Encrypt`` with the recovered message and the
  re-derived coin seed, and compares the resulting ciphertext to the
  input. If they match, the shared secret is ``K'`` from the re-run.
  If they differ, the shared secret is the pseudorandom rejection
  value ``J(z || c)``, which depends on the rejection seed stored in
  ``dk`` and on the ciphertext itself.

The re-encryption check is what lifts K-PKE (IND-CPA) to ML-KEM
(IND-CCA2). A decryption oracle that would reveal the K-PKE secret
on adversarially tampered ciphertexts is closed off because any
ciphertext that does not match the re-encryption is mapped to a
pseudorandom output that leaks nothing about the secret.

FIPS 203 also defines "external" algorithms that generate ``d``,
``z``, and ``m`` from a random source; those are thin wrappers
around the internal routines below and are omitted from this
module because the test vectors take all seeds as inputs.
"""

from __future__ import annotations

from .params import MLKEMParams
from .hashes import H, G, J
from .k_pke import k_pke_keygen, k_pke_encrypt, k_pke_decrypt


def ml_kem_keygen_internal(
    params: MLKEMParams, d: bytes, z: bytes
) -> tuple[bytes, bytes]:
    """ML-KEM.KeyGen_internal (FIPS 203 Algorithm 16).

    Input: a 32-byte K-PKE seed ``d`` and a 32-byte rejection seed
    ``z``. Output: the encapsulation key ``ek`` and decapsulation key
    ``dk``. The ``ek`` is identical to ``ek_PKE``. The ``dk`` is
    ``dk_PKE || ek || H(ek) || z`` for a total length of
    ``768 k + 96`` bytes.
    """
    assert len(d) == 32, f"keygen_internal: d must be 32 bytes"
    assert len(z) == 32, f"keygen_internal: z must be 32 bytes"
    ek_pke, dk_pke = k_pke_keygen(params, d)
    ek = ek_pke
    dk = dk_pke + ek + H(ek) + z
    assert len(ek) == params.ek_len()
    assert len(dk) == params.dk_len()
    return ek, dk


def ml_kem_encaps_internal(
    params: MLKEMParams, ek: bytes, m: bytes
) -> tuple[bytes, bytes]:
    """ML-KEM.Encaps_internal (FIPS 203 Algorithm 17).

    Input: the 32-byte message seed ``m`` and the encapsulation key
    ``ek``. Output: ``(K, c)`` where ``K`` is the 32-byte shared
    secret and ``c`` is the ciphertext.

    The coin seed ``r`` for the K-PKE layer is derived from
    ``G(m || H(ek))``, coupling encapsulation to both the message and
    the public key commitment. ``K`` is the other 32-byte half of
    the same ``G`` output.
    """
    assert len(ek) == params.ek_len()
    assert len(m) == 32, f"encaps_internal: m must be 32 bytes"
    shared_secret, coin_seed = G(m + H(ek))
    ciphertext = k_pke_encrypt(params, ek, m, coin_seed)
    return shared_secret, ciphertext


def ml_kem_decaps_internal(
    params: MLKEMParams, dk: bytes, c: bytes
) -> bytes:
    """ML-KEM.Decaps_internal (FIPS 203 Algorithm 18).

    Input: the decapsulation key ``dk`` and a ciphertext ``c``.
    Output: the 32-byte shared secret.

    Steps:
      1. Unpack ``dk`` into ``dk_PKE``, ``ek``, ``h = H(ek)``, ``z``.
      2. Run ``K_PKE.Decrypt(dk_PKE, c)`` to recover a candidate
         message ``m'``.
      3. Recompute the coin seed ``r'`` and a candidate shared
         secret ``K'`` from ``G(m' || h)``.
      4. Re-encrypt: ``c' = K_PKE.Encrypt(ek, m', r')``.
      5. If ``c == c'``, return ``K'``.
      6. Otherwise return the rejection pseudorandom value
         ``J(z || c)``.

    The constant-time comparison is omitted because this module is
    pedagogical, not hardened. Chapter 28 covers the timing-channel
    hardening that belongs in a production implementation.
    """
    assert len(dk) == params.dk_len()
    assert len(c) == params.ct_len()
    k = params.k

    dk_pke_len = params.dk_pke_len()
    ek_len = params.ek_len()
    dk_pke = dk[:dk_pke_len]
    ek = dk[dk_pke_len : dk_pke_len + ek_len]
    h = dk[dk_pke_len + ek_len : dk_pke_len + ek_len + 32]
    z = dk[dk_pke_len + ek_len + 32 : dk_pke_len + ek_len + 64]

    m_prime = k_pke_decrypt(params, dk_pke, c)
    k_prime, r_prime = G(m_prime + h)
    k_bar = J(z + c)
    c_prime = k_pke_encrypt(params, ek, m_prime, r_prime)
    if c == c_prime:
        return k_prime
    return k_bar
