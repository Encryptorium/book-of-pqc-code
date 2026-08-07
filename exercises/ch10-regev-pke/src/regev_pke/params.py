"""The RegevParams dataclass.

A Regev public-key encryption instance is specified by four numbers:

- n: the LWE secret dimension (length of the secret s)
- q: the modulus (all arithmetic is over Z_q)
- m: the number of LWE rows in the public key (rows of A, length of b)
- noise_bound: an integer B, with errors drawn uniformly from {-B, ..., B}

The dataclass validates structural correctness in __post_init__. The
noise-budget correctness condition 2 * m * B < q // 2 is exposed as a
method rather than asserted at construction time, so tests can
deliberately instantiate parameters that violate the budget and observe
decryption failing. This matches the philosophy of Chapter 8's
LWEParams, which likewise validates structure without asserting
cryptographic correctness conditions.

No error handling on degenerate input beyond the asserts: the dataclass
crashes loudly on bad values, which is the correct behaviour for a
pedagogical package.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RegevParams:
    """Parameters for a toy Regev public-key encryption instance over Z_q."""

    n: int
    q: int
    m: int
    noise_bound: int

    def __post_init__(self) -> None:
        # EXERCISE: implement this function.
        #
        # Assert that all four fields are plain ints, then assert n >= 1, q
        # >= 2, m >= 1, noise_bound >= 0, and 2 * noise_bound + 1 < q so the
        # error range {-B, ..., B} fits inside Z_q without wrapping. Stop
        # there. The noise budget is deliberately not asserted at
        # construction, because the tests build parameters that violate it
        # and then watch decryption fail; the budget is exposed as a method
        # instead.
        #
        # Reference: Chapter 10, 'A bit hidden in LWE noise'
        #
        # Proved by:
        #   tests/ch10/test_regev_params.py
        raise NotImplementedError("exercise: RegevParams.__post_init__")

    def noise_budget_headroom(self) -> float:
        """Return (q // 2) / 2 - m * noise_bound.

        The decoder's two codewords are 0 and q // 2, so a decrypted
        value survives rounding for both message bits exactly when
        2 |e^T r| < q // 2. That is Regev's Lemma 5.1 condition,
        |e| < floor(p/2) / 2, and it is tight: at q = 97 it admits
        |e^T r| up to 23, and |e^T r| = -24 under the bit 1 lands on
        24, which the decoder reads as 0. The asymptotic form of the
        same condition is the more familiar |e^T r| < q / 4; the two
        differ by a quarter for odd q, which is enough to matter at
        the small moduli this package runs on.

        The worst case over r in {0, 1}^m with every |e_i| <= B is
        |e^T r| = m B, so 2 m B < q // 2 is sufficient for every
        (e, r) pair. The headroom is the gap between that worst case
        and the decoding threshold: positive means the scheme decodes
        every honest sample correctly, negative means some fail.
        """
        # EXERCISE: implement this function.
        #
        # Return (q // 2) / 2 minus m * noise_bound, as a float, so (q, m,
        # B) = (97, 8, 1) gives 16.0. The decoder's two codewords are 0 and
        # q // 2, so a decrypted value survives rounding for both message
        # bits exactly when 2 |e^T r| < q // 2, and the worst case over r in
        # {0, 1}^m with every |e_i| <= B is m * B. The headroom is the gap
        # between the two. Positive means every honest encryption decodes;
        # negative means some do not. Do not use q / 4: it is the asymptotic
        # form of the same condition and it is one step too generous at
        # small odd q.
        #
        # Reference: Chapter 10, 'Noise budget and symmetric representatives'
        #
        # Proved by:
        #   tests/ch10/test_regev_params.py
        #   tests/ch10/test_noise_budget.py
        raise NotImplementedError("exercise: RegevParams.noise_budget_headroom")

    def is_noise_budget_feasible(self) -> bool:
        """Return True iff 2 * m * noise_bound < q // 2."""
        return self.noise_budget_headroom() > 0
