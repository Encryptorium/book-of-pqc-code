"""Tests for wallet_rotation.mosca_wallet.

Covers the breach window calculation, the per-cadence feasibility
report, and the recommendation function under three Z scenarios for
the Strand wallet surface (X = 10, Y = 4 from tests/ch36/conftest.py).
"""

from wallet_rotation import mosca_wallet


def test_breach_years_aggressive(strand_wallet_xy):
    X, Y = strand_wallet_xy
    # Z = 4 (aggressive arrival). Breach = 10 + 4 - 4 = 10.
    assert mosca_wallet.breach_years(X, Y, 4) == 10


def test_breach_years_ncsc_2035(strand_wallet_xy):
    X, Y = strand_wallet_xy
    # Z = 9 (NCSC working assumption). Breach = 10 + 4 - 9 = 5.
    assert mosca_wallet.breach_years(X, Y, 9) == 5


def test_breach_years_mid_2040_boundary(strand_wallet_xy):
    X, Y = strand_wallet_xy
    # Z = 14 (mid-2040). Breach = 10 + 4 - 14 = 0 (boundary case).
    assert mosca_wallet.breach_years(X, Y, 14) == 0


def test_breach_years_no_breach_when_z_dominates(strand_wallet_xy):
    X, Y = strand_wallet_xy
    # Z = 25 puts the arrival horizon past every reasonable seed lifetime.
    assert mosca_wallet.breach_years(X, Y, 25) == -11


def test_breach_years_rejects_negative_inputs():
    try:
        mosca_wallet.breach_years(-1, 4, 9)
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for negative input")


def test_recommend_calendar_when_no_breach(strand_wallet_xy):
    X, Y = strand_wallet_xy
    out = mosca_wallet.recommend_cadence(X, Y, 14)
    assert out["recommendation"] == "calendar"
    assert out["breach_years"] == 0
    assert out["rotation_interval_years"] == Y


def test_recommend_every_n_years_under_ncsc_2035(strand_wallet_xy):
    X, Y = strand_wallet_xy
    out = mosca_wallet.recommend_cadence(X, Y, 9)
    assert out["recommendation"] == "every-N-years"
    # Z - Y = 9 - 4 = 5; rotation interval N = 5 brings effective X to 5.
    assert out["rotation_interval_years"] == 5
    assert out["breach_years"] == 5


def test_recommend_external_trigger_under_aggressive(strand_wallet_xy):
    X, Y = strand_wallet_xy
    out = mosca_wallet.recommend_cadence(X, Y, 4)
    # Z = Y so safe_window = 0; no fixed-interval rotation feasible.
    assert out["recommendation"] == "external-trigger"
    assert out["rotation_interval_years"] == 0


def test_recommend_three_scenarios_table_rolls_through(strand_wallet_xy, mosca_z_values):
    X, Y = strand_wallet_xy
    table = {
        label: mosca_wallet.recommend_cadence(X, Y, z)
        for label, z in mosca_z_values.items()
    }
    assert table["aggressive"]["recommendation"] == "external-trigger"
    assert table["ncsc_2035"]["recommendation"] == "every-N-years"
    assert table["mid_2040"]["recommendation"] == "calendar"


def test_cadence_options_full_inventory(strand_wallet_xy):
    X, Y = strand_wallet_xy
    options = mosca_wallet.cadence_options(X, Y, 9)
    assert set(options.keys()) == set(mosca_wallet.CADENCE_NAMES)
    # Calendar infeasible under breach; every-N-years feasible; external
    # trigger always feasible.
    assert options["calendar"]["feasible"] is False
    assert options["every-N-years"]["feasible"] is True
    assert options["every-N-transactions"]["feasible"] is True
    assert options["external-trigger"]["feasible"] is True


def test_cadence_option_costs_are_ranked():
    options = mosca_wallet.cadence_options(10, 4, 9)
    # Operational cost label monotonically rises across the four options.
    cost_order = ["low", "medium", "medium-high", "high"]
    actual = [options[name]["operational_cost"] for name in mosca_wallet.CADENCE_NAMES]
    assert actual == cost_order


def test_evaluate_uses_strand_anchor_by_default():
    # No X or Y override; Z=9 (NCSC working assumption).
    out = mosca_wallet.evaluate(9)
    assert out["X"] == mosca_wallet.STRAND_WALLET_X == 10
    assert out["Y"] == mosca_wallet.STRAND_WALLET_Y == 4
    assert out["recommendation"] == "every-N-years"


def test_evaluate_respects_x_y_overrides():
    # Pass a hypothetical custodial-exchange wallet with shorter X.
    out = mosca_wallet.evaluate(9, X=3, Y=2)
    assert out["X"] == 3 and out["Y"] == 2
    # 3 + 2 = 5 < 9, no breach. Cadence = calendar.
    assert out["recommendation"] == "calendar"
