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
    assert len(d) == 32, f"k_pke_keygen: d must be 32 bytes, got {len(d)}"
    k = params.k
    eta_1 = params.eta_1

    # Step 1: (rho, sigma) = G(d || {k as one byte}).
    rho, sigma = G(d + bytes([k]))

    # Step 2: sample A_hat in the NTT domain from rho with KeyGen
    # byte order (rho || j || i per FIPS 203 Algorithm 13).
    a_hat = sample_matrix_ntt(rho, k, transpose=False)

    # Step 3: sample secret s and error e from CBD_eta_1 with sigma.
    s = np.zeros((k, N), dtype=np.int64)
    for i in range(k):
        s[i] = sample_poly_cbd(eta_1, sigma, nonce=i)
    e = np.zeros((k, N), dtype=np.int64)
    for i in range(k):
        e[i] = sample_poly_cbd(eta_1, sigma, nonce=k + i)

    # Step 4: transform s and e into the NTT domain.
    s_hat = _ntt_vector(s)
    e_hat = _ntt_vector(e)

    # Step 5: t_hat = A_hat * s_hat + e_hat (all in NTT domain).
    t_hat = _matrix_vector_ntt(a_hat, s_hat)
    t_hat = (t_hat + e_hat) % Q

    # Step 6: serialize ek and dk.
    ek_pke = byte_encode_vector(t_hat, 12) + rho
    dk_pke = byte_encode_vector(s_hat, 12)
    assert len(ek_pke) == params.ek_len(), (
        f"ek_pke length {len(ek_pke)} != {params.ek_len()}"
    )
    assert len(dk_pke) == params.dk_pke_len(), (
        f"dk_pke length {len(dk_pke)} != {params.dk_pke_len()}"
    )
    return ek_pke, dk_pke


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
    assert len(ek_pke) == params.ek_len()
    assert len(m) == 32, f"k_pke_encrypt: m must be 32 bytes"
    assert len(r) == 32, f"k_pke_encrypt: r must be 32 bytes"
    k = params.k
    eta_1 = params.eta_1
    eta_2 = params.eta_2
    d_u = params.d_u
    d_v = params.d_v

    # Step 1: decode ek_PKE into t_hat and rho.
    t_hat_bytes = ek_pke[: 384 * k]
    rho = ek_pke[384 * k :]
    t_hat = byte_decode_vector(t_hat_bytes, 12, k)

    # Step 2: expand A_hat in the Encrypt byte order (rho || i || j).
    # This is the transpose of KeyGen's matrix, so the plain matrix-
    # vector product below evaluates to A^T r (KeyGen perspective).
    a_hat = sample_matrix_ntt(rho, k, transpose=True)

    # Step 3: sample r_hat, e1, e2 from seed r.
    r_vec = np.zeros((k, N), dtype=np.int64)
    for i in range(k):
        r_vec[i] = sample_poly_cbd(eta_1, r, nonce=i)
    e1 = np.zeros((k, N), dtype=np.int64)
    for i in range(k):
        e1[i] = sample_poly_cbd(eta_2, r, nonce=k + i)
    e2 = sample_poly_cbd(eta_2, r, nonce=2 * k)

    # Step 4: transform r into the NTT domain.
    r_hat = _ntt_vector(r_vec)

    # Step 5: u = InvNTT(A_hat_transpose * r_hat) + e1.
    u_hat = _matrix_vector_ntt(a_hat, r_hat)
    u = _inverse_ntt_vector(u_hat)
    u = (u + e1) % Q

    # Step 6: v = InvNTT(t_hat dot r_hat) + e2 + Decompress_1(m).
    t_r_hat = _vector_dot_ntt(t_hat, r_hat)
    t_r = inverse_ntt(t_r_hat)
    v = (t_r + e2 + message_to_poly(m)) % Q

    # Step 7: compress and serialize.
    u_comp = compress(u, d_u)
    v_comp = compress(v, d_v)
    c1 = byte_encode_vector(u_comp, d_u)
    c2 = byte_encode_d(v_comp, d_v)
    ciphertext = c1 + c2
    assert len(ciphertext) == params.ct_len(), (
        f"k_pke_encrypt: ct length {len(ciphertext)} != {params.ct_len()}"
    )
    return ciphertext


def k_pke_decrypt(
    params: MLKEMParams, dk_pke: bytes, ciphertext: bytes
) -> bytes:
    """K-PKE.Decrypt (FIPS 203 Algorithm 15).

    Input: ``dk_PKE`` of length ``384 k`` bytes and ``c`` of length
    ``32 (d_u k + d_v)`` bytes. Output: the decrypted 32-byte message.
    """
    assert len(dk_pke) == params.dk_pke_len()
    assert len(ciphertext) == params.ct_len()
    k = params.k
    d_u = params.d_u
    d_v = params.d_v

    c1 = ciphertext[: 32 * d_u * k]
    c2 = ciphertext[32 * d_u * k :]
    u_comp = byte_decode_vector(c1, d_u, k)
    v_comp = byte_decode_d(c2, d_v)
    u = decompress(u_comp, d_u)
    v = decompress(v_comp, d_v)

    s_hat = byte_decode_vector(dk_pke, 12, k)

    # Decryption: v - s^T * u, where the multiplication is in R_q.
    # Bring u into the NTT domain, dot with s_hat, bring back, subtract.
    u_hat = _ntt_vector(u)
    sum_hat = _vector_dot_ntt(s_hat, u_hat)
    sum_poly = inverse_ntt(sum_hat)
    w = (v - sum_poly) % Q

    return poly_to_message(w)
