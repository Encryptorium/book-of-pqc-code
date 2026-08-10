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
    # EXERCISE: implement this function.
    #
    # Expand xi into (rho, rho', K), build A_hat from rho, draw (s1, s2)
    # from rho'. Form t = A s1 + s2 with the matrix product taken in the NTT
    # domain and brought back, split it with Power2Round into (t1, t0), then
    # pk = pkEncode(rho, t1), tr = H(pk, 64), sk = skEncode(rho, K, tr, s1,
    # s2, t0).
    #
    # Reference: Chapter 12, 'KeyGen' (FIPS 204 Algorithm 6)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sign.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: ml_dsa_keygen_internal")


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
    # EXERCISE: implement this function.
    #
    # The Fiat-Shamir-with-aborts loop. Decode sk, compute mu and rho''.
    # Each attempt: expand a fresh mask y from rho'' and kappa (advance
    # kappa by l), form w = A y and w1 = HighBits(w), derive c-tilde and c =
    # SampleInBall, set z = y + c*s1 and r0 = LowBits(w - c*s2). Reject and
    # restart if ||z||_inf >= gamma1 - beta or ||r0||_inf >= gamma2 - beta.
    # Otherwise build h = MakeHint(-c*t0, w - c*s2 + c*t0) and reject if
    # ||c*t0||_inf >= gamma2 or the hint weight exceeds omega. On success
    # return (sigEncode(c-tilde, center(z), h), iteration_count).
    #
    # Reference: Chapter 12, 'Sign: the rejection-sampling abort loop' (FIPS 204 Algorithm 7)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sign.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: _sign_internal_traced")


def ml_dsa_sign_internal(params: MLDSAParams, sk: bytes, m_prime: bytes, rnd: bytes) -> bytes:
    """FIPS 204 Algorithm 7. Deterministic when rnd is all-zero, hedged otherwise."""
    sigma, _ = _sign_internal_traced(params, sk, m_prime, rnd)
    return sigma


# --- Algorithm 8: Verify_internal. ---

def ml_dsa_verify_internal(params: MLDSAParams, pk: bytes, m_prime: bytes, sigma: bytes) -> bool:
    """FIPS 204 Algorithm 8. Returns True iff sigma is a valid ML-DSA signature."""
    # EXERCISE: implement this function.
    #
    # Decode pk and the signature; return False immediately if the hint
    # decoded to None. Recompute w'Approx = A z - c * (t1 * 2^d) in the NTT
    # domain, apply w1' = UseHint(h, w'Approx), and recompute c-tilde' =
    # H(mu || w1Encode(w1')). Accept iff ||z||_inf < gamma1 - beta and
    # c-tilde' == c-tilde.
    #
    # Reference: Chapter 12, 'Verify: recomputing the commitment through UseHint' (FIPS 204 Algorithm 8)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sign.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: ml_dsa_verify_internal")


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
