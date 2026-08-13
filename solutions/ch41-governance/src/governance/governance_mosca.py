"""Specialized Mosca-window calculator for the governance surface.

Ch 36 introduces Mosca's inequality in the blockchain context with X
as the data lifetime, Y as the migration time, and Z as the years
until a cryptographically relevant quantum computer arrives. The
strict breach condition is X + Y > Z.

This module specializes the calculation to the Strand governance
surface (X = 4 years, Y = 3 years per the Ch 36 fixture) and
recommends one of four governance-rotation cadences based on the
breach window. The four cadence options are tuned to the multisig
governance committee's per-vote tempo.

The four cadence options:

- ``per-vote-cycle``: rotate the governance signing keys at every
  governance vote (per-vote rotation). Operationally prohibitive
  because every vote would require a multisig key-ceremony plus
  on-chain registration. Recorded as the zero-overhead lower bound;
  never recommended in practice.
- ``every-N-vote-cycles``: rotate every N governance votes where N
  implies an effective X_eff <= Z - Y. The default for a breach
  with a positive safe window (Y < Z < X+Y). Practical N values
  run from a small number of votes (sub-annual cadence) to many
  votes (multi-year cadence).
- ``governance-trigger``: rotate at a named governance event (a
  multisig committee membership change, a treasury proposal milestone,
  a chain-tip protocol upgrade). The default when the breach window
  is comfortable; the rotation interval is set by the governance
  cadence rather than by Mosca arithmetic.
- ``hard-fork-trigger``: rotate at a named L1 hard-fork event (CRQC
  arrival rumor, jurisdictional mandate, post-quantum activation
  fork). The default when Z <= Y; the rotation interval drops below
  the practical governance tempo.

The recommendation function picks the cadence whose effective X
clears the breach inequality with the smallest operational cost. A
caller can override the recommendation by inspecting the per-cadence
cost rankings the function returns alongside the recommendation.
"""

from typing import Dict, Tuple, TypedDict


class CadenceOption(TypedDict):
    name: str
    feasible: bool
    rotation_interval_years: int
    operational_cost: str
    rationale: str


CADENCE_NAMES: Tuple[str, ...] = (
    "per-vote-cycle",
    "every-N-vote-cycles",
    "governance-trigger",
    "hard-fork-trigger",
)

# Strand governance-surface anchor from tests/ch36/conftest.py.
STRAND_GOVERNANCE_X = 4
STRAND_GOVERNANCE_Y = 3

# Three Z-scenario names locked at planning. The vocabulary
# (narrow / central / wide) deliberately avoids collision with
# any deployment-status or pq-status cell value in
# stakeholder_matrix or fork_choreography. Z = 6 forces a breach
# (X + Y = 7 > 6) and selects the every-N-vote-cycles cadence
# with a three-year safe window. Z = 9 mirrors the Ch 36 / Ch 39
# / Ch 40 NCSC-2035 anchor and clears the breach by two years;
# Z = 13 is a wide-horizon scenario that also clears.
SCENARIO_Z_VALUES: Dict[str, int] = {
    "narrow": 6,
    "central": 9,
    "wide": 13,
}


def breach_years(X: int, Y: int, Z: int) -> int:
    """Return X + Y - Z, the governance-surface Mosca breach window.

    A positive value indicates the governance surface breaches the
    Mosca window: the governance-key reuse window plus the
    migration time runs past the CRQC arrival horizon. A non-
    positive value indicates the surface clears the window
    (boundary X + Y == Z is treated as cleared per Ch 36's strict
    inequality framing).
    """
    assert X >= 0 and Y >= 0 and Z >= 0, "X, Y, Z must be non-negative"
    return X + Y - Z


def cadence_options(X: int, Y: int, Z: int) -> Dict[str, CadenceOption]:
    """Per-cadence feasibility and operational cost under (X, Y, Z).

    Each cadence carries a feasibility flag, a rotation interval in
    years, an operational-cost label, and a one-line rationale. The
    recommendation function consumes this dict to pick the cheapest
    feasible cadence.
    """
    breach = breach_years(X, Y, Z)
    safe_window = max(0, Z - Y)

    per_vote_cycle: CadenceOption = {
        "name": "per-vote-cycle",
        "feasible": True,
        "rotation_interval_years": 0,
        "operational_cost": "prohibitive",
        "rationale": (
            "rotate every governance vote; the multisig key-ceremony "
            "plus on-chain registration choreography makes this "
            "operationally prohibitive in practice"
        ),
    }

    every_n_cycles: CadenceOption = {
        "name": "every-N-vote-cycles",
        "feasible": safe_window >= 1 and breach > 0,
        "rotation_interval_years": safe_window,
        "operational_cost": "medium",
        "rationale": (
            "rotate every N governance votes with N tuned so effective "
            "governance-key reuse plus migration clears the Mosca "
            "window"
        ),
    }

    governance_trigger: CadenceOption = {
        "name": "governance-trigger",
        "feasible": breach <= 0,
        "rotation_interval_years": 0,
        "operational_cost": "low",
        "rationale": (
            "rotate at a named governance event; feasible only when "
            "X + Y already clears Z, since governance cadence is set "
            "by the multisig committee rather than by Mosca arithmetic"
        ),
    }

    hard_fork_trigger: CadenceOption = {
        "name": "hard-fork-trigger",
        "feasible": True,
        "rotation_interval_years": 0,
        "operational_cost": "high",
        "rationale": (
            "rotate at a named L1 hard-fork event; the default when "
            "Z <= Y leaves no room for a fixed-interval rotation"
        ),
    }

    return {
        "per-vote-cycle": per_vote_cycle,
        "every-N-vote-cycles": every_n_cycles,
        "governance-trigger": governance_trigger,
        "hard-fork-trigger": hard_fork_trigger,
    }


def recommend_cadence(X: int, Y: int, Z: int) -> Dict[str, object]:
    """Pick the cheapest feasible cadence under the (X, Y, Z) tuple.

    Order of preference (lowest operational cost first):

    1. ``governance-trigger`` if no breach.
    2. ``every-N-vote-cycles`` if a positive safe window exists.
    3. ``hard-fork-trigger`` otherwise.

    The ``per-vote-cycle`` cadence is always feasible as a lower
    bound but is operationally prohibitive; the function returns it
    as a runner-up rather than as the recommendation.
    """
    breach = breach_years(X, Y, Z)
    options = cadence_options(X, Y, Z)
    safe_window = max(0, Z - Y)

    if breach <= 0:
        recommendation = "governance-trigger"
        recommended_interval = 0
    elif safe_window >= 1:
        recommendation = "every-N-vote-cycles"
        recommended_interval = safe_window
    else:
        recommendation = "hard-fork-trigger"
        recommended_interval = 0

    return {
        "X": X,
        "Y": Y,
        "Z": Z,
        "breach_years": breach,
        "safe_window_years": safe_window,
        "recommendation": recommendation,
        "rotation_interval_years": recommended_interval,
        "options": options,
    }


def evaluate(
    Z: int, X: int = STRAND_GOVERNANCE_X, Y: int = STRAND_GOVERNANCE_Y
) -> Dict[str, object]:
    """Run the recommendation under the Strand governance anchor (X=4, Y=3).

    The default X and Y come from tests/ch36/conftest.py for the
    governance row. Pass an alternate X or Y to model a different
    chain's governance surface.
    """
    return recommend_cadence(X, Y, Z)


def evaluate_named_scenario(scenario: str) -> Dict[str, object]:
    """Run the recommendation for one of the three named Z scenarios.

    The scenario names (narrow, central, wide) and Z values are
    locked at planning time. ``narrow`` is Z = 6 (CRQC arrival sooner
    than the governance-key reuse window plus migration time, forcing
    a breach with a three-year safe window), ``central`` is Z = 9
    (the chapter's central NCSC-style estimate, which clears the
    governance surface by two years), ``wide`` is Z = 13 (a
    comfortable horizon for governance-paced rotation).
    """
    assert scenario in SCENARIO_Z_VALUES, f"unknown scenario: {scenario!r}"
    Z = SCENARIO_Z_VALUES[scenario]
    return evaluate(Z)
