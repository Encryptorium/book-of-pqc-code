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
        assert isinstance(self.n, int), "RegevParams.n must be an int"
        assert isinstance(self.q, int), "RegevParams.q must be an int"
        assert isinstance(self.m, int), "RegevParams.m must be an int"
        assert isinstance(self.noise_bound, int), (
            "RegevParams.noise_bound must be an int"
        )
        assert self.n >= 1, f"RegevParams requires n >= 1 (got n={self.n})"
        assert self.q >= 2, f"RegevParams requires q >= 2 (got q={self.q})"
        assert self.m >= 1, f"RegevParams requires m >= 1 (got m={self.m})"
        assert self.noise_bound >= 0, (
            f"RegevParams.noise_bound must be nonnegative "
            f"(got {self.noise_bound})"
        )
        assert 2 * self.noise_bound + 1 < self.q, (
            f"RegevParams.noise_bound must satisfy 2B + 1 < q so that the "
            f"error distribution fits inside Z_q without wraparound "
            f"(got noise_bound={self.noise_bound}, q={self.q})"
        )

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
        return (self.q // 2) / 2 - self.m * self.noise_bound

    def is_noise_budget_feasible(self) -> bool:
        """Return True iff 2 * m * noise_bound < q // 2."""
        return self.noise_budget_headroom() > 0
