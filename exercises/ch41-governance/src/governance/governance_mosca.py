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
    # EXERCISE: implement this function.
    #
    # Return X + Y - Z after asserting all three are non-negative. The value
    # is signed on purpose: the Strand governance surface sits at X = 4 and
    # Y = 3, so the central scenario at Z = 9 returns -2 and the committee
    # reads how much headroom it has rather than only that it cleared. The
    # boundary X + Y == Z returns 0 and counts as cleared, following Ch 36's
    # strict inequality.
    #
    # Reference: Chapter 41, 'Plan the governance-rotation cadence'
    #
    # Proved by:
    #   tests/ch41/test_governance_mosca.py
    raise NotImplementedError("exercise: breach_years")


def cadence_options(X: int, Y: int, Z: int) -> Dict[str, CadenceOption]:
    """Per-cadence feasibility and operational cost under (X, Y, Z).

    Each cadence carries a feasibility flag, a rotation interval in
    years, an operational-cost label, and a one-line rationale. The
    recommendation function consumes this dict to pick the cheapest
    feasible cadence.
    """
    # EXERCISE: implement this function.
    #
    # Compute the breach and the safe window (max of 0 and Z - Y) once, then
    # build all four CadenceOption records. per-vote-cycle is always
    # feasible with interval 0 and cost 'prohibitive', because rotating the
    # committee's keys at every vote would need a multisig key ceremony plus
    # on-chain registration each time; it is the zero-overhead lower bound
    # and never the answer. every-N-vote-cycles is feasible when the safe
    # window is at least one year and the breach is positive, carries the
    # safe window as its interval, and costs 'medium'. governance-trigger is
    # feasible only when the breach is non-positive, carries interval 0, and
    # costs 'low', because the committee sets the tempo rather than the
    # arithmetic. hard-fork-trigger is always feasible with interval 0 and
    # cost 'high'. Key the returned dict by the four CADENCE_NAMES. The
    # rationale strings are prose for the operator and nothing asserts on
    # them.
    #
    # Reference: Chapter 41, 'Plan the governance-rotation cadence'
    #
    # Proved by:
    #   tests/ch41/test_governance_mosca.py
    raise NotImplementedError("exercise: cadence_options")


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
    # EXERCISE: implement this function.
    #
    # Pick the cheapest feasible cadence in one three-branch cascade: no
    # breach gives governance-trigger at interval 0; otherwise a safe window
    # of at least one year gives every-N-vote-cycles at that window;
    # otherwise hard-fork-trigger at interval 0. per-vote-cycle is never the
    # recommendation, because its prohibitive cost loses to every other
    # feasible option, so it comes back only inside the options dict as the
    # lower bound. Return X, Y, Z, breach_years, safe_window_years,
    # recommendation, rotation_interval_years, and the full options dict, so
    # a caller can override the pick from the same call.
    #
    # Reference: Chapter 41, 'Plan the governance-rotation cadence'
    #
    # Proved by:
    #   tests/ch41/test_governance_mosca.py
    raise NotImplementedError("exercise: recommend_cadence")


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
    # EXERCISE: implement this function.
    #
    # Assert the scenario is one of the three names locked at planning, read
    # its Z out of SCENARIO_Z_VALUES, and run evaluate on it so the Strand X
    # = 4 and Y = 3 anchor threads through rather than being restated here.
    # narrow is Z = 6 and is the only scenario that breaches, by one year,
    # recommending every-N-vote-cycles at a three-year interval; central at
    # Z = 9 clears by two years and wide at Z = 13 clears by six, both
    # recommending governance-trigger. narrow sits at 6 rather than 7
    # because the strict-inequality boundary for this surface is X + Y = 7,
    # so 6 is the smallest breach the scenario set admits.
    #
    # Reference: Chapter 41, 'Plan the governance-rotation cadence'
    #
    # Proved by:
    #   tests/ch41/test_governance_mosca.py
    raise NotImplementedError("exercise: evaluate_named_scenario")
