"""Pricing the two WOTS+ implementation countermeasures Chapter 18 recommends.

Both cost the same `ell * (w - 1)` hash calls, and they are not the same measure.

**Verify-after-sign** defends against fault injection: the signer re-derives the
public key from the signature it just produced and compares. A fault that moved a
chain value produces a different public key and the check fails. Its cost is
`sign + verify`, and the message digits cancel out of that sum, which is the
result Chapter 18's fourth exercise asks for.

**Constant-time chaining** defends against timing analysis: the signer walks every
chain the full `w - 1` steps regardless of the digit and selects the value it
needs. Its cost is `ell * (w - 1)` by construction rather than by cancellation.

The two arrive at one number from different directions, and neither implies the
other. Verify-after-sign is constant-cost in total while its signing half still
runs in `sum(digits)` time, so it leaks exactly what constant-time chaining
removes unless the two halves are indistinguishable to the observer. Constant-time
chaining hides the digits and detects no faults at all.

Digits here are the WOTS+ message and checksum digits together, each in
`[0, w - 1]`, as produced by base-`w` encoding (Chapter 15).

Standard library only.
"""

from __future__ import annotations

from collections.abc import Sequence


def wots_sign_hash_calls(digits: Sequence[int]) -> int:
    """Hash calls to sign: chain `i` is walked `digits[i]` steps from its secret."""
    return sum(digits)


def wots_verify_hash_calls(digits: Sequence[int], w: int) -> int:
    """Hash calls to verify: chain `i` is walked from step `digits[i]` to `w - 1`.

    The verifier starts where the signer stopped and finishes the chain, so it
    pays `w - 1 - digits[i]` per chain: the exact complement of what signing
    paid. A signature over small digits is cheap to make and dear to check, and
    the two costs move in opposite directions digit for digit.
    """
    return sum(w - 1 - d for d in digits)


def verify_after_sign_hash_calls(digits: Sequence[int], w: int) -> int:
    """Total hash calls to sign then verify: `ell * (w - 1)`, whatever the digits.

    Every `digits[i]` appears once positively from signing and once negatively
    from verification, so the message contributes nothing to the sum and only the
    chain count and `w` survive. That cancellation is why the countermeasure is
    priced as a fixed multiple of signing rather than as a variable surcharge.
    """
    return wots_sign_hash_calls(digits) + wots_verify_hash_calls(digits, w)


def constant_time_chain_cost(ell: int, w: int) -> int:
    """Hash calls for a signer that walks all `ell` chains their full length."""
    return ell * (w - 1)
