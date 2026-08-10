"""ML-DSA KeyGen / Sign / Verify (FIPS 204 Algorithms 2-3, 6-8).

This module assembles the pieces from the other modules into the three ML-DSA
operations. As with ``ch11-mlkem``, the flagship functions are the *internal*
(explicit-seed / explicit-rnd) variants that the ACVP vectors exercise directly:

* ``ml_dsa_keygen_internal(params, xi)`` -> (pk, sk)          [Algorithm 6]
* ``ml_dsa_sign_internal(params, sk, M', rnd)`` -> sigma       [Algorithm 7]
* ``ml_dsa_verify_internal(params, pk, M', sigma)`` -> bool    [Algorithm 8]

Sign is a Fiat-Shamir-*with-aborts* loop: it samples a fresh mask y, forms the
commitment, derives the challenge, and either accepts or restarts if the response
z or the low-order remainder r0 is too large, or the hint would exceed its budget.
The counter kappa advances by l per attempt so each ExpandMask call reads a fresh
block of sub-seeds.

The two thin *external* wrappers ``ml_dsa_sign`` / ``ml_dsa_verify`` add the
FIPS 204 context framing M' = (0, |ctx|, ctx, M) that a deploying application
actually calls (pure, no pre-hash). Following the book's pedagogical stance, the
verifier's c-tilde comparison is a plain ``==`` (constant-time hardening is a
deployment concern discussed later, not part of this reference).
"""

from __future__ import annotations

import numpy as np

from .params import ML_DSA_Q as Q, ML_DSA_D as D, MLDSAParams
from .ntt import ntt, ntt_inverse, multiply_ntts
from .rounding import (
    power2round_poly,
    high_bits_poly,
    low_bits_poly,
    make_hint_poly,
    use_hint_poly,
    mod_pm,
)
from .hashes import (
    expand_keygen_seed,
    crh,
    message_representative,
    mask_seed,
    commitment_hash,
    integer_to_bytes,
)
from .sampling import expand_a, expand_s, expand_mask, sample_in_ball
from .encode import (
    pk_encode,
    pk_decode,
    sk_encode,
    sk_decode,
    sig_encode,
    sig_decode,
    w1_encode,
)


# --- Module linear algebra over stacks of polynomials. ---

def _ntt_vec(v: np.ndarray) -> np.ndarray:
    """Apply the forward NTT to each polynomial of an (m, 256) stack."""
    return np.array([ntt(v[i]) for i in range(v.shape[0])], dtype=np.int64)


def _intt_vec(v_hat: np.ndarray) -> np.ndarray:
    """Apply the inverse NTT to each polynomial of an (m, 256) stack."""
    return np.array([ntt_inverse(v_hat[i]) for i in range(v_hat.shape[0])], dtype=np.int64)


def _matrix_vector_ntt(a_hat: np.ndarray, v_hat: np.ndarray) -> np.ndarray:
    """Compute (A_hat . v_hat) in the NTT domain: row r = sum_s A[r,s] * v[s]."""
    k, l = a_hat.shape[0], a_hat.shape[1]
    out = np.zeros((k, 256), dtype=np.int64)
    for r in range(k):
        acc = np.zeros(256, dtype=np.int64)
        for s in range(l):
            prod = multiply_ntts(a_hat[r][s], v_hat[s])
            acc = (acc + prod) % Q
        out[r] = acc
    return out


def _scalar_vector_ntt(c_hat: np.ndarray, v_hat: np.ndarray) -> np.ndarray:
    """Multiply every polynomial of a stack by the scalar polynomial c (NTT domain)."""
    return np.array([multiply_ntts(c_hat, v_hat[i]) for i in range(v_hat.shape[0])], dtype=np.int64)


def _center(arr: np.ndarray) -> np.ndarray:
    """Reduce every coefficient to its centered representative in (-q/2, q/2]."""
    a = arr % Q
    return np.where(a > Q // 2, a - Q, a)


def _inf_norm(arr: np.ndarray) -> int:
    """Infinity norm using centered representatives (FIPS 204's ||.||_inf)."""
    return int(np.max(np.abs(_center(arr)))) if arr.size else 0


# --- Algorithm 6: KeyGen_internal. ---

def ml_dsa_keygen_internal(params: MLDSAParams, xi: bytes) -> tuple[bytes, bytes]:
    """FIPS 204 Algorithm 6. Expand the 32-byte seed xi into (pk, sk)."""
    assert len(xi) == 32, f"keygen: xi must be 32 bytes, got {len(xi)}"
    rho, rho_prime, K = expand_keygen_seed(xi, params.k, params.l)
    a_hat = expand_a(params, rho)
    s1, s2 = expand_s(params, rho_prime)

    # t = A . s1 + s2
    s1_hat = _ntt_vec(s1)
    t = (_intt_vec(_matrix_vector_ntt(a_hat, s1_hat)) + s2) % Q

    # (t1, t0) = Power2Round(t) componentwise
    t1 = np.empty((params.k, 256), dtype=np.int64)
    t0 = np.empty((params.k, 256), dtype=np.int64)
    for r in range(params.k):
        t1[r], t0[r] = power2round_poly(t[r])

    pk = pk_encode(params, rho, t1)
    tr = crh(pk)
    sk = sk_encode(params, rho, K, tr, s1, s2, t0)
    return pk, sk


def _public_key_from_sk(params: MLDSAParams, sk: bytes) -> bytes:
    """Reconstruct pk from sk (recompute t, Power2Round, pkEncode). Test helper."""
    rho, _K, _tr, s1, s2, _t0 = sk_decode(params, sk)
    a_hat = expand_a(params, rho)
    t = (_intt_vec(_matrix_vector_ntt(a_hat, _ntt_vec(s1))) + s2) % Q
    t1 = np.empty((params.k, 256), dtype=np.int64)
    for r in range(params.k):
        t1[r], _ = power2round_poly(t[r])
    return pk_encode(params, rho, t1)


# --- Algorithm 7: Sign_internal (with the abort loop). ---

def _sign_internal_traced(
    params: MLDSAParams, sk: bytes, m_prime: bytes, rnd: bytes,
) -> tuple[bytes, int]:
    """Sign and also return the number of rejection-loop iterations (for tests)."""
    assert len(rnd) == 32, f"sign: rnd must be 32 bytes, got {len(rnd)}"
    rho, K, tr, s1, s2, t0 = sk_decode(params, sk)
    s1_hat = _ntt_vec(s1)
    s2_hat = _ntt_vec(s2)
    t0_hat = _ntt_vec(t0)
    a_hat = expand_a(params, rho)

    mu = message_representative(tr, m_prime)
    rho_dprime = mask_seed(K, rnd, mu)

    g1, g2, beta = params.gamma_1, params.gamma_2, params.beta
    kappa = 0
    iterations = 0
    while True:
        iterations += 1
        y = expand_mask(params, rho_dprime, kappa)
        kappa += params.l

        w = _intt_vec(_matrix_vector_ntt(a_hat, _ntt_vec(y)))
        w1 = np.array([high_bits_poly(w[r], g2) for r in range(params.k)], dtype=np.int64)

        c_tilde = commitment_hash(mu, w1_encode(params, w1), params.c_tilde_len())
        c = sample_in_ball(params, c_tilde)
        c_hat = ntt(c)

        cs1 = _intt_vec(_scalar_vector_ntt(c_hat, s1_hat))          # (l, 256)
        cs2 = _intt_vec(_scalar_vector_ntt(c_hat, s2_hat))          # (k, 256)

        z = (y + cs1) % Q
        r0 = np.array([low_bits_poly((w[r] - cs2[r]) % Q, g2) for r in range(params.k)],
                      dtype=np.int64)

        if _inf_norm(z) >= g1 - beta or _inf_norm(r0) >= g2 - beta:
            continue

        ct0 = _intt_vec(_scalar_vector_ntt(c_hat, t0_hat))          # (k, 256)
        h = np.array(
            [make_hint_poly(-ct0[r], (w[r] - cs2[r] + ct0[r]) % Q, g2) for r in range(params.k)],
            dtype=np.int64,
        )
        if _inf_norm(ct0) >= g2 or int(np.sum(h)) > params.omega:
            continue

        z_centered = _center(z)
        sigma = sig_encode(params, c_tilde, z_centered, h)
        return sigma, iterations


def ml_dsa_sign_internal(params: MLDSAParams, sk: bytes, m_prime: bytes, rnd: bytes) -> bytes:
    """FIPS 204 Algorithm 7. Deterministic when rnd is all-zero, hedged otherwise."""
    sigma, _ = _sign_internal_traced(params, sk, m_prime, rnd)
    return sigma


# --- Algorithm 8: Verify_internal. ---

def ml_dsa_verify_internal(params: MLDSAParams, pk: bytes, m_prime: bytes, sigma: bytes) -> bool:
    """FIPS 204 Algorithm 8. Returns True iff sigma is a valid ML-DSA signature."""
    rho, t1 = pk_decode(params, pk)
    c_tilde, z, h = sig_decode(params, sigma)
    if h is None:
        return False

    a_hat = expand_a(params, rho)
    tr = crh(pk)
    mu = message_representative(tr, m_prime)
    c = sample_in_ball(params, c_tilde)

    # w'Approx = NTT^-1( A_hat . NTT(z) - NTT(c) . NTT(t1 . 2^d) )
    az_hat = _matrix_vector_ntt(a_hat, _ntt_vec(z))
    c_hat = ntt(c)
    t1_scaled = (t1 * (1 << D)) % Q
    ct1_hat = _scalar_vector_ntt(c_hat, _ntt_vec(t1_scaled))
    w_approx_hat = (az_hat - ct1_hat) % Q
    w_approx = _intt_vec(w_approx_hat)

    w1_prime = np.array([use_hint_poly(h[r], w_approx[r], params.gamma_2) for r in range(params.k)],
                        dtype=np.int64)
    c_tilde_prime = commitment_hash(mu, w1_encode(params, w1_prime), params.c_tilde_len())

    return _inf_norm(z) < params.gamma_1 - params.beta and c_tilde == c_tilde_prime


# --- Algorithms 2-3: external context wrappers (pure, no pre-hash). ---

def _format_message(m: bytes, ctx: bytes) -> bytes:
    """FIPS 204 M' = IntegerToBytes(0,1) || IntegerToBytes(|ctx|,1) || ctx || M."""
    assert len(ctx) <= 255, f"context must be <= 255 bytes, got {len(ctx)}"
    return integer_to_bytes(0, 1) + integer_to_bytes(len(ctx), 1) + ctx + m


def ml_dsa_sign(params: MLDSAParams, sk: bytes, m: bytes, ctx: bytes = b"",
                rnd: bytes = bytes(32)) -> bytes:
    """FIPS 204 Algorithm 2 (pure). Sign message m under context ctx."""
    return ml_dsa_sign_internal(params, sk, _format_message(m, ctx), rnd)


def ml_dsa_verify(params: MLDSAParams, pk: bytes, m: bytes, sigma: bytes,
                  ctx: bytes = b"") -> bool:
    """FIPS 204 Algorithm 3 (pure). Verify signature on m under context ctx."""
    return ml_dsa_verify_internal(params, pk, _format_message(m, ctx), sigma)
