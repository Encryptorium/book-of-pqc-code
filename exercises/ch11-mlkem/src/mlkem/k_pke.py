"""K-PKE, the IND-CPA public-key encryption underlying ML-KEM.

K-PKE is Regev public-key encryption from Chapter 10, moved over to
Module-LWE, with centered binomial noise and compression on the
ciphertext. It is specified in FIPS 203 §5 as three algorithms:

- ``K_PKE.KeyGen(d)`` (Algorithm 13): given a 32-byte seed ``d``,
  return the encryption key ``ek_PKE`` and decryption key ``dk_PKE``.
- ``K_PKE.Encrypt(ek_PKE, m, r)`` (Algorithm 14): given ``ek_PKE``,
  a 32-byte message ``m``, and a 32-byte coin seed ``r``, return the
  ciphertext ``c``.
- ``K_PKE.Decrypt(dk_PKE, c)`` (Algorithm 15): given ``dk_PKE`` and a
  ciphertext, return the decrypted 32-byte message.

The math is unchanged from Chapter 10's Regev construction:
``(A, t = A s + e)`` is the public key, ``(u = A^T r + e_1,
v = t^T r + e_2 + Decompress(m))`` is the ciphertext (using
FIPS 203 §5.2 names ``e_1`` for the vector error and ``e_2``
for the scalar error), and ``Decrypt(dk, c) = Compress_1(
v - s^T u)`` exploits the secret-cancellation identity. The differences relative to Chapter 10:

- The secret ``s`` and errors live in the module ``R_q^k`` rather than
  in ``Z_q^n``.
- Every polynomial multiplication runs in the NTT domain.
- The error distributions are centered binomial ``CBD_eta_1`` for
  the secret and long-term error, and ``CBD_eta_2`` for the
  encryption randomness.
- The ciphertext is compressed: ``u`` is packed at width ``d_u``,
  ``v`` is packed at width ``d_v``.

FIPS 203 distinguishes the matrix ``A_hat`` used in KeyGen from the
``A_hat`` used in Encrypt by swapping the ``(i, j)`` byte order in
the XOF seed. The effect is that Encrypt's matrix is KeyGen's
transposed, so that the plain ``sum_j A_hat[i][j] * r_hat[j]``
evaluates to ``A^T r`` (from KeyGen's perspective) without an
explicit transpose.
"""

from __future__ import annotations

import numpy as np

from .params import MLKEMParams
from .hashes import G
from .sampling import sample_matrix_ntt, sample_poly_cbd
from .ntt import ntt, inverse_ntt, multiply_ntts, N, Q
from .compress import (
    compress,
    decompress,
    message_to_poly,
    poly_to_message,
)
from .serialize import (
    byte_encode_vector,
    byte_decode_vector,
    byte_encode_d,
    byte_decode_d,
)


def _matrix_vector_ntt(
    a_hat: np.ndarray, v_hat: np.ndarray
) -> np.ndarray:
    """Compute ``a_hat @ v_hat`` in the NTT domain.

    Input shapes: ``a_hat`` is ``(k, k, N)``, ``v_hat`` is ``(k, N)``.
    Output shape: ``(k, N)``. Each row of the result is the sum of
    ``multiply_ntts(a_hat[i][j], v_hat[j])`` over ``j``, which in the
    standard ring representation is the dot product of the row of
    polynomials with the vector of polynomials.
    """
    k = a_hat.shape[0]
    assert a_hat.shape == (k, k, N)
    assert v_hat.shape == (k, N)
    out = np.zeros((k, N), dtype=np.int64)
    for i in range(k):
        acc = np.zeros(N, dtype=np.int64)
        for j in range(k):
            prod = multiply_ntts(a_hat[i, j], v_hat[j])
            acc = (acc + prod) % Q
        out[i] = acc
    return out


def _vector_dot_ntt(u_hat: np.ndarray, v_hat: np.ndarray) -> np.ndarray:
    """Compute the length-N polynomial ``sum_i multiply_ntts(u_hat[i], v_hat[i])``.

    Both inputs are length-$k$ vectors of NTT-domain polynomials,
    shape ``(k, N)``. The output is a single NTT-domain polynomial of
    shape ``(N,)``, the dot product in the module.
    """
    k = u_hat.shape[0]
    assert u_hat.shape == (k, N)
    assert v_hat.shape == (k, N)
    out = np.zeros(N, dtype=np.int64)
    for i in range(k):
        out = (out + multiply_ntts(u_hat[i], v_hat[i])) % Q
    return out


def _ntt_vector(v: np.ndarray) -> np.ndarray:
    """Apply ``ntt`` to each row of a length-$k$ vector of polynomials."""
    return np.stack([ntt(row) for row in v], axis=0)


def _inverse_ntt_vector(v_hat: np.ndarray) -> np.ndarray:
    """Apply ``inverse_ntt`` to each row of a length-$k$ vector."""
    return np.stack([inverse_ntt(row) for row in v_hat], axis=0)


def k_pke_keygen(
    params: MLKEMParams, d: bytes
) -> tuple[bytes, bytes]:
    """K-PKE.KeyGen (FIPS 203 Algorithm 13).

    Input: a 32-byte seed ``d``.
    Output: ``(ek_PKE, dk_PKE)`` with

    - ``ek_PKE`` of length ``384 k + 32`` bytes: the NTT-domain public
      vector ``t_hat = A_hat s_hat + e_hat`` encoded at $d = 12$,
      followed by the 32-byte seed ``rho`` used to expand the matrix.
    - ``dk_PKE`` of length ``384 k`` bytes: the NTT-domain secret
      vector ``s_hat`` encoded at $d = 12$.

    Matches the FIPS 203 pseudocode variable names and call order
    literally so the NIST ACVP test vectors load without ambiguity.
    """
    # EXERCISE: implement this function.
    #
    # Assert d is 32 bytes. Split G(d + bytes([k])) into (rho, sigma), the
    # matrix seed and the noise seed. Expand A_hat from rho with
    # sample_matrix_ntt at transpose=False. Draw the secret rows with
    # sample_poly_cbd(eta_1, sigma, nonce) at nonces 0 through k-1 and the
    # error rows at nonces k through 2k-1, so the two vectors never share a
    # draw. Move both into the NTT domain row by row, set t_hat = A_hat
    # s_hat + e_hat modulo q, and return (byte_encode_vector(t_hat, 12) +
    # rho, byte_encode_vector(s_hat, 12)). Both keys are stored in the NTT
    # domain because every later multiplication happens there.
    #
    # Reference: Chapter 11, 'K-PKE.KeyGen' (FIPS 203 Algorithm 13)
    #
    # Proved by:
    #   tests/ch11/test_k_pke_roundtrip.py
    #   tests/ch11/test_vectors.py
    raise NotImplementedError("exercise: k_pke_keygen")


def k_pke_encrypt(
    params: MLKEMParams, ek_pke: bytes, m: bytes, r: bytes
) -> bytes:
    """K-PKE.Encrypt (FIPS 203 Algorithm 14).

    Input:

    - ``ek_PKE`` of length ``384 k + 32`` bytes.
    - ``m`` of length 32 bytes (the plaintext message).
    - ``r`` of length 32 bytes (the coin seed / encryption randomness
      seed, supplied derandomized by the ML-KEM wrapper or uniformly
      random in a standalone K-PKE use).

    Output: ``c`` of length ``32 (d_u k + d_v)`` bytes.
    """
    # EXERCISE: implement this function.
    #
    # Split ek_PKE into its first 384 k bytes, decoded to t_hat at d = 12,
    # and the trailing 32-byte rho. Expand the matrix from rho with
    # transpose=True so the plain row product below evaluates to A^T y. From
    # the coin seed r draw the ephemeral vector with CBD_{eta_1} at nonces 0
    # through k-1, the vector error e1 with CBD_{eta_2} at nonces k through
    # 2k-1, and the scalar error e2 with CBD_{eta_2} at nonce 2k. NTT the
    # ephemeral vector, then u is the inverse NTT of the matrix-vector
    # product plus e1, row by row, and v is the inverse NTT of the dot
    # product of t_hat with it, plus e2, plus message_to_poly(m). Compress u
    # at d_u and v at d_v, encode each, concatenate. Nothing here draws
    # randomness of its own: the same (ek, m, r) must give the same bytes,
    # which is what the re-encryption check inside Decaps depends on.
    #
    # Reference: Chapter 11, 'K-PKE.Encrypt' (FIPS 203 Algorithm 14)
    #
    # Proved by:
    #   tests/ch11/test_k_pke_roundtrip.py
    #   tests/ch11/test_vectors.py
    raise NotImplementedError("exercise: k_pke_encrypt")


def k_pke_decrypt(
    params: MLKEMParams, dk_pke: bytes, ciphertext: bytes
) -> bytes:
    """K-PKE.Decrypt (FIPS 203 Algorithm 15).

    Input: ``dk_PKE`` of length ``384 k`` bytes and ``c`` of length
    ``32 (d_u k + d_v)`` bytes. Output: the decrypted 32-byte message.
    """
    # EXERCISE: implement this function.
    #
    # Split the ciphertext at 32 * d_u * k bytes; decode and decompress the
    # first part into u at width d_u and the second into the scalar v at
    # width d_v, and decode s_hat from dk_PKE at d = 12. Bring u into the
    # NTT domain, take its slot-wise dot product with s_hat, bring that back
    # to the coefficient domain, and set w = v minus it, modulo q. Return
    # poly_to_message(w). The secret-cancellation identity from Chapter 10
    # leaves w equal to the encoded message plus the Module-LWE and
    # compression noise, so compressing at d = 1 reads the message back
    # whenever that noise stayed inside the decoding region.
    #
    # Reference: Chapter 11, 'K-PKE.Decrypt' (FIPS 203 Algorithm 15)
    #
    # Proved by:
    #   tests/ch11/test_k_pke_roundtrip.py
    #   tests/ch11/test_vectors.py
    raise NotImplementedError("exercise: k_pke_decrypt")
