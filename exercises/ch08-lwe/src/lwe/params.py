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
        # EXERCISE: implement this function.
        #
        # Assert that all four fields are plain ints, then assert the
        # parameter constraints one at a time: n >= 1, q >= 2, m >= n so the
        # noise-free system is determined, noise_bound >= 0, and 2 *
        # noise_bound + 1 < q so the error support fits strictly inside Z_q
        # without wrapping.
        #
        # Reference: Chapter 8, 'Search LWE and decisional LWE'
        #
        # Proved by:
        #   tests/ch08/test_params.py
        raise NotImplementedError("exercise: LWEParams.__post_init__")
