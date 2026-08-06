"""The LWEParams dataclass.

An LWE instance is specified by four numbers:

- n: the secret dimension (number of unknowns in s)
- q: the modulus (all arithmetic is over Z_q)
- m: the number of samples (rows of A and length of b)
- noise_bound: an integer B, with errors drawn uniformly from {-B, ..., B}

No error handling on degenerate input: the dataclass asserts and
crashes loudly on bad values, which is the correct behaviour for a
pedagogical package.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LWEParams:
    """Parameters for a toy LWE instance over Z_q.

    The package accepts any q >= 2 so that readers can experiment
    with composite moduli; the "prime q polynomial in n" constraint
    from Regev's search-to-decision reduction is a theorem-level
    requirement, not a package-level one.
    """

    n: int
    q: int
    m: int
    noise_bound: int

    def __post_init__(self) -> None:
        assert isinstance(self.n, int), "LWEParams.n must be an int"
        assert isinstance(self.q, int), "LWEParams.q must be an int"
        assert isinstance(self.m, int), "LWEParams.m must be an int"
        assert isinstance(self.noise_bound, int), (
            "LWEParams.noise_bound must be an int"
        )
        assert self.n >= 1, f"LWEParams requires n >= 1 (got n={self.n})"
        assert self.q >= 2, f"LWEParams requires q >= 2 (got q={self.q})"
        assert self.m >= self.n, (
            f"LWEParams requires m >= n so that the noise-free system "
            f"is determined (got m={self.m}, n={self.n})"
        )
        assert self.noise_bound >= 0, (
            f"LWEParams.noise_bound must be nonnegative "
            f"(got {self.noise_bound})"
        )
        assert 2 * self.noise_bound + 1 < self.q, (
            f"LWEParams.noise_bound must satisfy 2B + 1 < q so that the "
            f"error distribution fits inside Z_q without wraparound "
            f"(got noise_bound={self.noise_bound}, q={self.q})"
        )
