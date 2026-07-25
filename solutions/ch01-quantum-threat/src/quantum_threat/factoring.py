"""Trial division: the classical factoring baseline of Chapter 1.

The chapter uses trial division to calibrate the quantum threat. It is the
most obvious factoring algorithm there is, it is correct on every composite,
and its cost on an RSA-sized modulus is the number the chapter compares Shor's
polynomial-time result against.

Two functions. ``factor_trial_division`` is the one the chapter prints.
``factor_trial_division_counted`` is the instrumented variant exercise 2 asks
for: same search, but it reports how many candidate divisions the loop
performed before it returned.

Neither validates its input, per the book's rule for toy code: bad input
crashes loudly rather than being handled. Note that an ``n`` below 4 exits the
loop immediately and reports ``None``, which is the honest answer to "is this
composite, and if so what are its factors" for 0, 1, 2, and 3 alike.
"""


def factor_trial_division(n: int) -> tuple[int, int] | None:
    """Return (p, q) with p * q == n if n is composite, else None.

    Trial division up to sqrt(n) is correct for any composite, since every
    composite has a prime factor at most sqrt(n). It is just catastrophically
    slow for moduli the size of any real RSA key.
    """
    candidate = 2
    while candidate * candidate <= n:
        if n % candidate == 0:
            return candidate, n // candidate
        candidate += 1
    return None


def factor_trial_division_counted(n: int) -> tuple[int, int, int] | None:
    """Return (p, q, divisions) for a composite n, else None.

    The same search as ``factor_trial_division``, carrying a count of the
    candidate divisions performed. The count is what makes the cost argument
    concrete: for a semiprime n = pq with p <= q, the loop stops at p, so it
    performs exactly p - 1 divisions rather than the floor(sqrt(n)) an
    unfactored worst case would need. For n = 3233 = 53 x 61 that is 52, while
    floor(sqrt(3233)) is 56.

    The worst case is what the chapter's RSA-2048 estimate rests on: a
    balanced modulus has both factors near sqrt(n), so the search runs to
    about 2^1024 divisions, and no constant-factor speedup closes a gap in the
    exponent.
    """
    candidate = 2
    count = 0
    while candidate * candidate <= n:
        count += 1
        if n % candidate == 0:
            return candidate, n // candidate, count
        candidate += 1
    return None
