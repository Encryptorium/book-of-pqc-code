"""Mosca's inequality applied to a blockchain signature surface.

Mosca's inequality (Ch 01) is the urgency relation for a migration
deadline. Given:

- ``x``: the data lifetime, in years (how long the asset remains
  attackable; for an on-chain transaction signature on a public
  ledger, ``x`` is the archival retention horizon, which is
  effectively unbounded).
- ``y``: the migration time, in years (how long the operator needs to
  swap primitives across every node, wallet, and verifier).
- ``z``: the years until a cryptographically relevant quantum
  computer (CRQC) arrives.

The inequality ``x + y > z`` flags an asset that a CRQC reaches before
migration completes. The exposure window in years is

    ``max(x + y - z, 0)``

A return of zero means the asset migrates with margin to spare under
the chosen ``z``; a positive return is the number of years the asset
sits exposed under the chosen ``z``.

Inputs are non-negative integers (years). Python booleans are
``int`` subclasses and are rejected; pass a plain ``int``. The
function asserts the contract; bad input fails loudly per CLAUDE.md
section 9 (no ``try``/``except``).
"""


def evaluate(x: int, y: int, z: int) -> int:
    """Return the exposure window in years.

    ``x``, ``y``, ``z`` are non-negative integers expressing years.
    The result is ``max(x + y - z, 0)``: zero if migration completes
    before the CRQC arrives, otherwise the number of years the asset
    sits exposed.
    """
    assert isinstance(x, int) and not isinstance(x, bool), (
        f"x must be a non-bool int (got {type(x).__name__})"
    )
    assert isinstance(y, int) and not isinstance(y, bool), (
        f"y must be a non-bool int (got {type(y).__name__})"
    )
    assert isinstance(z, int) and not isinstance(z, bool), (
        f"z must be a non-bool int (got {type(z).__name__})"
    )
    assert x >= 0 and y >= 0 and z >= 0, (
        f"x, y, z must be non-negative (got x={x}, y={y}, z={z})"
    )
    breach = x + y - z
    return breach if breach > 0 else 0
