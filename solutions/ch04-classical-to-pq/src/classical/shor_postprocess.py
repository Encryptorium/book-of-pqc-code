"""Classical post-processing step of Shor's factoring algorithm.

Given ``N = p * q`` with ``p`` and ``q`` unknown, a random base ``a``
coprime to ``N``, and the multiplicative order (period) ``r`` of ``a``
modulo ``N``, try the two ``gcd`` candidates and either recover a
non-trivial factor of ``N`` or signal that the outer Shor loop must retry
with a fresh base. Not every genuine order yields a factor: an odd ``r``,
or ``a^(r/2) == -1 (mod N)``, sends the caller back for a new ``a``.
``ord(2) mod 3233 = 780`` is a real order that fails this way.

The quantum period-finding step that produces ``r`` is NOT implemented
here. On a fault-tolerant quantum computer it runs in polynomial time;
see Shor 1994 and Nielsen-Chuang 2010. On a classical computer, period
finding itself is hard, so this module takes ``r`` as an input.

The post-processing identity is elementary. If ``r`` is even and
``a^{r/2} != -1 (mod N)`` then

    a^r = 1                 (mod N)
    (a^{r/2} - 1)(a^{r/2} + 1) = 0   (mod N)

so ``N`` divides the product ``(a^{r/2} - 1)(a^{r/2} + 1)`` but divides
neither factor on its own; hence ``gcd(a^{r/2} - 1, N)`` is a non-trivial
factor of ``N``. The function tries both ``gcd`` candidates.
"""

from __future__ import annotations

from math import gcd


def recover_factor(n: int, a: int, r: int) -> int:
    """Given ``(n, a, r)``, return a non-trivial factor of ``n``.

    Raises ``ValueError`` if the period is odd, if ``a^{r/2} == -1 mod n``,
    or if neither ``gcd`` candidate lands in ``(1, n)``. In any of those
    cases the classical Shor algorithm retries with a fresh random base
    ``a`` and a fresh period-finding call; the retry loop is outside the
    scope of this toy and lives in the chapter prose.
    """
    if r % 2 != 0:
        raise ValueError(f"period {r} is odd; Shor's algorithm retries with a new base a")
    x = pow(a, r // 2, n)
    if x == n - 1:
        raise ValueError(f"a^(r/2) == -1 mod n; Shor's algorithm retries with a new base a")
    for candidate in (gcd(x - 1, n), gcd(x + 1, n)):
        if 1 < candidate < n:
            return candidate
    raise ValueError(f"period {r} did not recover a non-trivial factor of {n}")
