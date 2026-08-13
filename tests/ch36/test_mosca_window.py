"""Tests for ``blockchain_threat.mosca_window``."""

import pytest

from blockchain_threat import evaluate


def test_breach_returns_positive_window() -> None:
    # x + y = 55, z = 9; window is 46 years.
    assert evaluate(50, 5, 9) == 46


def test_no_breach_returns_zero() -> None:
    # x + y = 3, z = 14; migration completes nine years before CRQC.
    assert evaluate(2, 1, 14) == 0


def test_exact_threshold_returns_zero() -> None:
    # x + y == z is on the boundary; the inequality is strict, so the
    # window is zero.
    assert evaluate(5, 4, 9) == 0


def test_strand_consensus_under_ncsc_2035(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["consensus"]
    z = mosca_z_values["ncsc_2035"]
    # consensus: x=2, y=1, z=9; no breach.
    assert evaluate(x, y, z) == 0


def test_strand_transaction_under_ncsc_2035(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["transaction"]
    z = mosca_z_values["ncsc_2035"]
    # transaction: x=50, y=5, z=9; window is 46 years.
    assert evaluate(x, y, z) == 46


def test_strand_wallet_under_ncsc_2035(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["wallet"]
    z = mosca_z_values["ncsc_2035"]
    # wallet: x=10, y=4, z=9; window is 5 years (the second breach
    # surface in the chapter's running example).
    assert evaluate(x, y, z) == 5


def test_strand_wallet_under_mid_2040(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["wallet"]
    z = mosca_z_values["mid_2040"]
    # wallet: x=10, y=4, z=14; on the strict-inequality boundary.
    # x+y == z, so the inequality x+y > z is not satisfied and the
    # breach window is zero.
    assert evaluate(x, y, z) == 0


def test_strand_transaction_under_mid_2040(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["transaction"]
    z = mosca_z_values["mid_2040"]
    # transaction: x=50, y=5, z=14; window is 41 years (the only
    # surface that still breaches under the mid-2040 Z).
    assert evaluate(x, y, z) == 41


def test_strand_verifier_under_ncsc_2035(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["on-chain-verifier"]
    z = mosca_z_values["ncsc_2035"]
    # on-chain verifier: x=3, y=2, z=9; sits inside the migration
    # window with margin to spare.
    assert evaluate(x, y, z) == 0


def test_strand_governance_under_ncsc_2035(
    mosca_z_values: dict[str, int],
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    x, y = strand_xy["governance"]
    z = mosca_z_values["ncsc_2035"]
    # governance: x=4, y=3, z=9; does not breach under NCSC 2035
    # but is the first surface to breach under stricter Z.
    assert evaluate(x, y, z) == 0


def test_nsm10_2035_matches_ncsc_2035(
    mosca_z_values: dict[str, int],
) -> None:
    # The two 2035 scenarios use the same Z value; the chapter cites
    # them separately because the policy framings differ (NCSC 2035
    # migration horizon vs NSM-10 / CNSA 2.0 2035 NSS regulatory
    # deadline). Both are planning deadlines, not CRQC forecasts.
    assert mosca_z_values["nsm10_2035"] == mosca_z_values["ncsc_2035"] == 9


def test_strand_xy_pins_each_surface_under_an_aggressive_z(
    strand_xy: dict[str, tuple[int, int]],
) -> None:
    # Every test above reads the three non-breaching surfaces at a Z
    # where all three return zero, so consensus, on-chain-verifier and
    # governance can swap (X, Y) pairs with the whole suite green.
    # Z = 2, the aggressive early-CRQC scenario the Appendix D
    # solution to Exercise 1 uses, separates all five surfaces: the
    # windows are distinct, so no permutation survives.
    windows = {
        surface: evaluate(x, y, 2) for surface, (x, y) in strand_xy.items()
    }
    assert windows == {
        "transaction": 53,
        "consensus": 1,
        "wallet": 12,
        "on-chain-verifier": 3,
        "governance": 5,
    }


def test_negative_input_asserts() -> None:
    with pytest.raises(AssertionError, match="non-negative"):
        evaluate(-1, 5, 9)


def test_non_integer_input_asserts() -> None:
    with pytest.raises(AssertionError, match="non-bool int"):
        evaluate(5.0, 5, 9)


def test_bool_input_asserts() -> None:
    # Python booleans are ``int`` subclasses; the contract forbids them
    # because ``True`` and ``False`` would silently coerce to 1 and 0.
    with pytest.raises(AssertionError, match="non-bool int"):
        evaluate(True, 5, 9)
