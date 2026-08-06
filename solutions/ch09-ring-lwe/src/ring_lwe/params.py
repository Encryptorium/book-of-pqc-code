"""The RingParams and ModuleParams dataclasses.

A Ring-LWE instance is specified by four numbers:

- n: the ring degree (power of two)
- q: the modulus (prime, with 2n dividing q - 1 so the NTT is available)
- m: the number of samples (Ring-LWE pairs emitted)
- noise_bound: an integer B, with errors drawn uniformly from {-B, ..., B}

A Module-LWE instance adds one more:

- k: the module rank (number of ring elements in the secret vector)

No error handling on degenerate input: the dataclasses assert and
crash loudly on bad values, which is the correct behaviour for a
pedagogical package.
"""

from __future__ import annotations

from dataclasses import dataclass


def _is_power_of_two(n: int) -> bool:
    return n >= 1 and (n & (n - 1)) == 0


def _is_prime(q: int) -> bool:
    if q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    i = 3
    while i * i <= q:
        if q % i == 0:
            return False
        i += 2
    return True


@dataclass
class RingParams:
    """Parameters for a Ring-LWE instance over R_q = Z_q[x]/(x^n + 1).

    This package requires n a power of two and q prime; the ring
    itself is well defined for any modulus, but the prime case is
    the one the chapter and these routines work in. The
    stricter condition 2n | q - 1 (needed for the full negacyclic
    NTT) is enforced inside the NTT functions rather than on the
    dataclass, so that rings like ML-KEM's (n = 256, q = 3329) which
    admit only a partial NTT still construct successfully here and
    can be used with the schoolbook ring_mul_naive. Chapter 11
    handles the partial NTT separately for ML-KEM.
    """

    n: int
    q: int
    m: int
    noise_bound: int

    def __post_init__(self) -> None:
        assert isinstance(self.n, int), "RingParams.n must be an int"
        assert isinstance(self.q, int), "RingParams.q must be an int"
        assert isinstance(self.m, int), "RingParams.m must be an int"
        assert isinstance(self.noise_bound, int), (
            "RingParams.noise_bound must be an int"
        )
        assert _is_power_of_two(self.n), (
            f"RingParams requires n to be a power of two (got n={self.n})"
        )
        assert self.n >= 2, (
            f"RingParams requires n >= 2 so the ring is non-trivial "
            f"(got n={self.n})"
        )
        assert _is_prime(self.q), (
            f"RingParams requires q to be prime (got q={self.q})"
        )
        assert self.m >= 1, f"RingParams requires m >= 1 (got m={self.m})"
        assert self.noise_bound >= 0, (
            f"RingParams.noise_bound must be nonnegative "
            f"(got {self.noise_bound})"
        )
        assert 2 * self.noise_bound + 1 < self.q, (
            f"RingParams.noise_bound must satisfy 2B + 1 < q so that the "
            f"error distribution fits inside Z_q without wraparound "
            f"(got noise_bound={self.noise_bound}, q={self.q})"
        )

    def ntt_available(self) -> bool:
        """Return True iff 2n | q - 1, the condition for the full negacyclic NTT."""
        return (self.q - 1) % (2 * self.n) == 0


@dataclass
class ModuleParams:
    """Parameters for a toy Module-LWE instance over R_q^k.

    Module-LWE collapses to Ring-LWE at k = 1 and to flat LWE at
    n = 1. The interesting regime for practical schemes is in between:
    ML-KEM-512 uses k = 2, ML-KEM-768 uses k = 3, ML-KEM-1024 uses
    k = 4, all over the ring R_q = Z_3329[x]/(x^256 + 1).
    """

    n: int
    q: int
    k: int
    m: int
    noise_bound: int

    def __post_init__(self) -> None:
        assert isinstance(self.n, int), "ModuleParams.n must be an int"
        assert isinstance(self.q, int), "ModuleParams.q must be an int"
        assert isinstance(self.k, int), "ModuleParams.k must be an int"
        assert isinstance(self.m, int), "ModuleParams.m must be an int"
        assert isinstance(self.noise_bound, int), (
            "ModuleParams.noise_bound must be an int"
        )
        assert _is_power_of_two(self.n), (
            f"ModuleParams requires n to be a power of two (got n={self.n})"
        )
        assert self.n >= 2, (
            f"ModuleParams requires n >= 2 (got n={self.n})"
        )
        assert _is_prime(self.q), (
            f"ModuleParams requires q to be prime (got q={self.q})"
        )
        assert self.k >= 1, f"ModuleParams requires k >= 1 (got k={self.k})"
        assert self.m >= 1, f"ModuleParams requires m >= 1 (got m={self.m})"
        assert self.noise_bound >= 0, (
            f"ModuleParams.noise_bound must be nonnegative "
            f"(got {self.noise_bound})"
        )
        assert 2 * self.noise_bound + 1 < self.q, (
            f"ModuleParams.noise_bound must satisfy 2B + 1 < q "
            f"(got noise_bound={self.noise_bound}, q={self.q})"
        )

    def as_ring_params(self) -> RingParams:
        """Return a RingParams with the same (n, q, m, noise_bound).

        Used by sample_module_lwe to delegate per-row ring sampling.
        """
        return RingParams(
            n=self.n, q=self.q, m=self.m, noise_bound=self.noise_bound
        )
