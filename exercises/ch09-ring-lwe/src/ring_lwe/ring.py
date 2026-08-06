"""Ring arithmetic in R_q = Z_q[x]/(x^n + 1).

Two operations:

- ring_add(f, g, q) adds two polynomials coefficient-wise modulo q
- ring_mul_naive(f, g, q) multiplies two polynomials via schoolbook
  convolution and then reduces modulo x^n + 1 by the rule x^n -> -1

Polynomials are numpy int64 arrays of length n in ascending-degree
order: entry i is the coefficient of x^i. The multiplication output
has exactly n entries after the negacyclic reduction, regardless of
the degrees of the inputs (inputs shorter than n are zero-padded by
the caller, which the sample routines do before calling this).

The schoolbook convolution is O(n^2) in ring operations. The
companion ntt module's ring_mul_ntt computes the same product
through the negacyclic NTT wherever 2n | q - 1, but it implements
the transform from its direct definition, so it is also O(n^2).
The O(n log n) path needs the iterative Cooley-Tukey form, which
Chapter 11 builds at ML-KEM scale.
"""

from __future__ import annotations

import numpy as np


def _as_ring_element(f: np.ndarray, n: int, q: int) -> np.ndarray:
    """Coerce f to a length-n int64 numpy array in [0, q)."""
    f = np.asarray(f, dtype=np.int64)
    assert f.ndim == 1, f"ring element must be 1-D, got shape {f.shape}"
    assert f.shape[0] == n, (
        f"ring element must have length n={n}, got length {f.shape[0]}"
    )
    return f % q


def ring_add(f: np.ndarray, g: np.ndarray, q: int) -> np.ndarray:
    """Add two elements of R_q coefficient-wise modulo q.

    Both f and g must be length-n numpy arrays at the same n. The
    caller is responsible for agreeing on n.
    """
    # EXERCISE: implement this function.
    #
    # Coerce both operands to int64, assert they have the same shape and are
    # one-dimensional, and return their sum reduced modulo q. Addition in
    # R_q needs no reduction modulo x^n + 1: the sum of two representatives
    # of degree below n is still of degree below n.
    #
    # Reference: Chapter 9, 'The ring R_q and its negacyclic multiplication'
    #
    # Proved by:
    #   tests/ch09/test_ring.py
    raise NotImplementedError("exercise: ring_add")


def ring_mul_naive(f: np.ndarray, g: np.ndarray, q: int) -> np.ndarray:
    """Multiply two elements of R_q = Z_q[x]/(x^n + 1).

    Computes the schoolbook product in Z[x], then reduces modulo
    x^n + 1 by folding every coefficient at index i + j with
    i + j >= n into index i + j - n with a sign flip. Finally reduces
    every coefficient modulo q.

    The output has exactly n entries. The algorithm is O(n^2) in
    integer operations and has no dependence on q beyond the final
    modular reduction.
    """
    # EXERCISE: implement this function.
    #
    # Coerce both operands to int64 and assert matching one-dimensional
    # shapes, with 'shape mismatch' in the message. Read n off the input
    # length and accumulate the schoolbook product into a length-n int64
    # array: the term f[i] * g[j] lands at index i + j when i + j < n, and
    # at index i + j - n with a minus sign when it does not, because x^n =
    # -1 in R_q. Reduce modulo q once at the end, not inside the loop.
    #
    # Reference: Chapter 9, 'The ring R_q and its negacyclic multiplication'
    #
    # Proved by:
    #   tests/ch09/test_ring.py
    #   tests/ch09/test_ringsample.py
    #   tests/ch09/test_module_collapses_to_ring.py
    raise NotImplementedError("exercise: ring_mul_naive")
