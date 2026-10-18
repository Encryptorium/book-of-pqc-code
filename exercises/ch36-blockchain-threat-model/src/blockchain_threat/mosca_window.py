"""Mosca's inequality applied to a blockchain surface.

Mosca's inequality (Ch 01) is the urgency relation for a migration
deadline. Given:

- ``x``: the data lifetime, in years (how long the asset remains
  attackable; for an on-chain transaction signature on a public
  ledger, ``x`` is the value lifetime, how long the exposed key
  still controls assets, which is effectively unbounded because the
  chain cannot rotate its holders' keys).
- ``y``: the migration time, in years (how long the operator needs to
  swap primitives across every node, wallet, and verifier).
- ``z``: the years until a cryptographically relevant quantum
  computer (CRQC) arrives.

The inequality ``x + y > z`` flags an asset still protected by
quantum-vulnerable cryptography when migration ends, which a CRQC can
break before its ``x`` years are up. The exposure window in years is

    ``max(x + y - z, 0)``

A return of zero means the asset's ``x`` years, counted from the end
of migration, run out no later than the chosen ``z``; a positive
return is the number of years the asset sits exposed under the chosen
``z``.

Inputs are non-negative integers (years). Python booleans are
``int`` subclasses and are rejected; pass a plain ``int``. The
function asserts the contract; bad input fails loudly per CLAUDE.md
section 9 (no ``try``/``except``).
"""


def evaluate(x: int, y: int, z: int) -> int:
    """Return the exposure window in years.

    ``x``, ``y``, ``z`` are non-negative integers expressing years.
    The result is ``max(x + y - z, 0)``: zero if the asset's ``x``
    years, counted from the end of migration, run out no later than
    the CRQC arrives, otherwise the number of years the asset sits
    exposed.
    """
    # EXERCISE: implement this function.
    #
    # Return max(x + y - z, 0), the exposure window in years. The inequality
    # X + Y > Z is strict, so x + y == z sits on the boundary and yields
    # zero, not one. Check the contract before computing: each argument must
    # be an int and must not be a bool, because Python's bool subclasses int
    # and True would silently pass as one year; then all three must be
    # non-negative. Assert rather than coerce, so bad input crashes loudly.
    #
    # Reference: Chapter 36, 'Mosca's inequality on a public ledger'
    #
    # Proved by:
    #   tests/ch36/test_mosca_window.py
    raise NotImplementedError("exercise: evaluate")
