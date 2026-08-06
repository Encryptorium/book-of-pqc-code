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
        # EXERCISE: implement this function.
        #
        # Assert that all four fields are plain ints, then assert the ring
        # conditions one at a time: n is a power of two (say 'power of two'
        # in the message), n >= 2 so the ring does not collapse to Z_q, q is
        # 'prime', m >= 1, noise_bound is 'nonnegative', and '2B + 1 < q' so
        # the error interval fits inside Z_q without wrapping. Do not assert
        # 2n | q - 1 here. ML-KEM's ring at (n, q) = (256, 3329) is a
        # well-defined ring that must construct; only the full negacyclic
        # NTT needs the stronger condition, and ntt_available reports it.
        #
        # Reference: Chapter 9, 'Ring-LWE and Module-LWE'
        #
        # Proved by:
        #   tests/ch09/test_ringparams.py
        raise NotImplementedError("exercise: RingParams.__post_init__")

    def ntt_available(self) -> bool:
        """Return True iff 2n | q - 1, the condition for the full negacyclic NTT."""
        # EXERCISE: implement this function.
        #
        # Report whether 2n divides q - 1. The multiplicative group of Z_q
        # is cyclic of order q - 1, so it holds an element of order exactly
        # 2n only under that condition, and that element is the psi the full
        # negacyclic NTT needs. It is True at (4, 17) because q - 1 = 16 = 2
        # * 2n, and False at ML-KEM's (256, 3329) because q - 1 = 3328 = 256
        # * 13.
        #
        # Reference: Chapter 9, 'The number theoretic transform'
        #
        # Proved by:
        #   tests/ch09/test_ringparams.py
        #   tests/ch09/test_ntt.py
        raise NotImplementedError("exercise: RingParams.ntt_available")


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
        # EXERCISE: implement this function.
        #
        # The same five checks as RingParams.__post_init__ over the five int
        # fields, plus 'k >= 1' so the module has at least one ring
        # coordinate. Keep the same message substrings, because the tests
        # match on them.
        #
        # Reference: Chapter 9, 'Ring-LWE and Module-LWE'
        #
        # Proved by:
        #   tests/ch09/test_ringparams.py
        raise NotImplementedError("exercise: ModuleParams.__post_init__")

    def as_ring_params(self) -> RingParams:
        """Return a RingParams with the same (n, q, m, noise_bound).

        Used by sample_module_lwe to delegate per-row ring sampling.
        """
        return RingParams(
            n=self.n, q=self.q, m=self.m, noise_bound=self.noise_bound
        )
