"""Specialized Mosca-window calculator for the consensus surface.

Ch 36 introduces Mosca's inequality in the blockchain context with X
as the data lifetime, Y as the migration time, and Z as the years
until a cryptographically relevant quantum computer arrives. The
strict breach condition is X + Y > Z.

This module specializes the calculation to the Strand consensus
surface (X = 2 years, Y = 1 year per the Ch 36 fixture) and recommends
one of four rotation cadences based on the breach window.

The four cadence options:

- ``per-epoch``: rotate the validator-set signing key every epoch.
  Operationally cheap because the validator-set turnover already
  follows the epoch cadence on Ethereum mainnet (one epoch is 32
  slots at 12 seconds, 6.4 minutes). The default for X + Y <= Z.
- ``every-N-epochs``: rotate every N epochs where N implies an
  effective X_eff <= Z - Y. The default for a modest breach with
  Z > Y. Practical N values run from one (per-epoch) to several
  thousand (multi-month rotation).
- ``every-N-validator-rotations``: rotate alongside the validator-set
  exit-and-entry cadence (Ethereum's churn limit caps the number of
  validators that can exit per epoch). Useful when the validator
  set itself rotates faster than a stated calendar interval.
- ``hard-fork-trigger``: rotate at a named hard-fork event (CRQC
  arrival rumor, jurisdictional mandate, post-quantum activation
  fork). The default when Z <= Y, where the rotation interval drops
  below practical hard-fork tempo.

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
    "per-epoch",
    "every-N-epochs",
    "every-N-validator-rotations",
    "hard-fork-trigger",
)

# Strand consensus surface anchor from tests/ch36/conftest.py.
STRAND_CONSENSUS_X = 2
STRAND_CONSENSUS_Y = 1


def breach_years(X: int, Y: int, Z: int) -> int:
    """Return X + Y - Z, the consensus-surface Mosca breach window in years.

    A positive value indicates the consensus surface breaches the Mosca
    window: the validator-key reuse window plus the migration time
    runs past the CRQC arrival horizon. A non-positive value indicates
    the surface clears the window (boundary X + Y == Z is treated as
    cleared per Ch 36's strict inequality framing).
    """
    # EXERCISE: implement this function.
    #
    # Return X + Y - Z after asserting all three are non-negative. The value
    # is signed on purpose: the Strand consensus surface sits at X = 2 and Y
    # = 1, so the NCSC scenario at Z = 9 returns -6 and the reader can see
    # how much headroom the surface has rather than only that it cleared.
    # The boundary X + Y == Z returns 0 and counts as cleared, following Ch
    # 36's strict inequality.
    #
    # Reference: Chapter 39, 'Plan the validator-key rotation cadence'
    #
    # Proved by:
    #   tests/ch39/test_consensus_mosca.py
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
    # build all four CadenceOption records. per-epoch is feasible only when
    # the breach is non-positive, carries interval 0 because the epoch is
    # already the chain's heartbeat, and costs 'low'. every-N-epochs and
    # every-N-validator-rotations share a feasibility test (a safe window of
    # at least one year and a positive breach) and an interval of the safe
    # window, differing only in cost, 'medium' against 'medium-high',
    # because aligning rotation to validator-set attrition is more
    # coordination than aligning it to a calendar. hard-fork-trigger is
    # always feasible with interval 0 and cost 'high'. Key the returned dict
    # by the four CADENCE_NAMES. The rationale strings are prose for the
    # operator and nothing asserts on them.
    #
    # Reference: Chapter 39, 'Plan the validator-key rotation cadence'
    #
    # Proved by:
    #   tests/ch39/test_consensus_mosca.py
    raise NotImplementedError("exercise: cadence_options")


def recommend_cadence(X: int, Y: int, Z: int) -> Dict[str, object]:
    """Pick the cheapest feasible cadence under the (X, Y, Z) tuple.

    Order of preference (lowest operational cost first):

    1. ``per-epoch`` if no breach.
    2. ``every-N-epochs`` if a positive safe window exists.
    3. ``hard-fork-trigger`` otherwise.

    The ``every-N-validator-rotations`` cadence has the same
    feasibility as ``every-N-epochs`` but a higher operational cost;
    the function returns it as a runner-up rather than as the
    recommendation.
    """
    # EXERCISE: implement this function.
    #
    # Pick the cheapest feasible cadence in one three-branch cascade: no
    # breach gives per-epoch at interval 0; otherwise a safe window of at
    # least one year gives every-N-epochs at that window; otherwise
    # hard-fork-trigger at interval 0. every-N-validator-rotations is never
    # the recommendation because it matches every-N-epochs on feasibility
    # and loses on cost, so it comes back only inside the options dict as a
    # runner-up. Return X, Y, Z, breach_years, safe_window_years,
    # recommendation, rotation_interval_years, and the full options dict, so
    # a caller can override the pick from the same call.
    #
    # Reference: Chapter 39, 'Plan the validator-key rotation cadence'
    #
    # Proved by:
    #   tests/ch39/test_consensus_mosca.py
    raise NotImplementedError("exercise: recommend_cadence")


def evaluate(
    Z: int, X: int = STRAND_CONSENSUS_X, Y: int = STRAND_CONSENSUS_Y
) -> Dict[str, object]:
    """Run the recommendation under the Strand consensus anchor (X=2, Y=1).

    The default X and Y come from tests/ch36/conftest.py for the
    consensus row. Pass an alternate X or Y to model a different
    chain's consensus surface.
    """
    return recommend_cadence(X, Y, Z)
