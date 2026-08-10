"""Generic attack exponents: classical and quantum, preimage and collision.

Four numbers per hash width, and Chapter 18's argument is about which of them
binds. Preimage costs `2**n` classically and `2**(n/2)` under Grover. Collision
costs `2**(n/2)` classically by the birthday bound and `2**(n/3)` under
Brassard-Hoyer-Tapp, given quantum-accessible memory at that same scale.

The BHT exponent is the smallest of the four and it is not the binding one. It is
a query-complexity result in a black-box model with an amount of quantum RAM that
nothing on any roadmap provides, and NIST's categories compare full attack
resources against reference primitives rather than query counts. The function is
here because the chapter explains the algorithm; the comparison it feeds is the
one that shows collision resistance is not what SLH-DSA's security rests on.

Every value is an exponent in bits, never a cost. Returning `2**85` as an integer
would be arithmetically honest and completely unreadable, and the chapter's
tables print exponents throughout.

Standard library only.
"""

from __future__ import annotations


def classical_preimage_bits(n_bits: int) -> float:
    """Brute-force preimage search: `2**n` evaluations, so `n` bits."""
    return float(n_bits)


def grover_preimage_bits(n_bits: int) -> float:
    """Grover preimage search: `2**(n/2)` evaluations, so `n / 2` bits.

    A first-order figure. The gate cost of one Grover iteration depends on the
    circuit depth of the hash being inverted, and NIST's category comparisons
    price that rather than counting oracle queries.
    """
    return n_bits / 2


def birthday_collision_bits(n_bits: int) -> float:
    """Classical collision search: `2**(n/2)` evaluations, so `n / 2` bits.

    Numerically equal to `grover_preimage_bits` at every width, which is a
    coincidence of two unrelated square roots and not a shared mechanism.
    """
    return n_bits / 2


def bht_collision_bits(n_bits: int) -> float:
    """Brassard-Hoyer-Tapp collision search: `2**(n/3)`, so `n / 3` bits.

    Assumes `2**(n/3)` entries of quantum-accessible RAM, queryable in
    superposition. Read it as the exponent an idealised black-box model yields,
    not as a cost an attacker pays.
    """
    return n_bits / 3
