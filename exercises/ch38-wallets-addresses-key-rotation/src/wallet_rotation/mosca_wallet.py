"""Specialized Mosca-window calculator for the wallet surface.

Ch 36 introduces Mosca's inequality in the blockchain context with
X as the data lifetime, Y as the migration time, and Z as the years
until a cryptographically relevant quantum computer arrives. The
strict breach condition is X + Y > Z.

This module specializes the calculation to the Strand wallet surface
(X = 10 years, Y = 4 years per the Ch 36 fixture) and recommends
one of four rotation cadences based on the breach window.

The four cadence options:

- ``calendar``: rotate on a fixed calendar (annual or per Y).
  Operationally cheap when no breach exists. The default for
  X + Y <= Z.
- ``every-N-years``: rotate every N years where N <= Z - Y.
  Brings effective seed lifetime to N; residual X_eff + Y <= Z.
  The default for a modest breach with Z > Y.
- ``every-N-transactions``: rotate every N spends. Caps per-key
  exposure by transaction count rather than calendar time. Useful
  when address-book turnover is dominated by transaction frequency
  rather than seed age.
- ``external-trigger``: rotate on a named external signal (CRQC
  arrival rumor, jurisdictional mandate, vendor recall). The
  default when Z <= Y, where the rotation interval drops below
  practical operational tempo.

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
    "calendar",
    "every-N-years",
    "every-N-transactions",
    "external-trigger",
)

# Strand wallet surface anchor from tests/ch36/conftest.py.
STRAND_WALLET_X = 10
STRAND_WALLET_Y = 4


def breach_years(X: int, Y: int, Z: int) -> int:
    """Return X + Y - Z, the wallet-surface Mosca breach window in years.

    A positive value indicates the wallet surface breaches the
    Mosca window: the seed lifetime plus the migration time runs
    past the CRQC arrival horizon. A non-positive value indicates
    the surface clears the window (boundary X + Y == Z is treated
    as cleared per Ch 36's strict inequality framing).
    """
    # EXERCISE: implement this function.
    #
    # Return X + Y - Z after asserting all three are non-negative. Unlike Ch
    # 36's evaluate this does not clamp at zero: a negative result carries
    # information, telling the operator how many years of headroom the
    # surface has rather than collapsing every safe case to the same answer.
    # The boundary X + Y == Z returns 0 and counts as cleared, following the
    # strict inequality in Ch 36.
    #
    # Reference: Chapter 38, 'Plan the rotation cadence'
    #
    # Proved by:
    #   tests/ch38/test_wallet_mosca.py
    raise NotImplementedError("exercise: breach_years")


def cadence_options(X: int, Y: int, Z: int) -> Dict[str, CadenceOption]:
    """Per-cadence feasibility and operational cost under the (X, Y, Z) tuple.

    Each cadence carries a feasibility flag, a rotation interval in
    years, an operational-cost label, and a one-line rationale. The
    recommendation function consumes this dict to pick the cheapest
    feasible cadence.
    """
    # EXERCISE: implement this function.
    #
    # Compute the breach and the safe window (max of 0 and Z - Y) once, then
    # build all four CadenceOption records. calendar is feasible only when
    # the breach is non-positive, rotates at Y, and costs 'low'.
    # every-N-years and every-N-transactions share a feasibility test (a
    # safe window of at least one year and a positive breach) and an
    # interval of the safe window, and differ only in cost: 'medium' against
    # 'medium-high', because triggering on spend count is more operational
    # work than triggering on a calendar. external-trigger is always
    # feasible with interval 0 and cost 'high'; feasible here means
    # definable, not risk-clearing, since it only helps if the trigger fires
    # with migration time left. Key the returned dict by the four
    # CADENCE_NAMES. The rationale strings are prose for the operator and
    # nothing asserts on them.
    #
    # Reference: Chapter 38, 'Plan the rotation cadence'
    #
    # Proved by:
    #   tests/ch38/test_wallet_mosca.py
    raise NotImplementedError("exercise: cadence_options")


def recommend_cadence(X: int, Y: int, Z: int) -> Dict[str, object]:
    """Pick the cheapest feasible cadence under the (X, Y, Z) tuple.

    Order of preference (lowest operational cost first):

    1. ``calendar`` if no breach.
    2. ``every-N-years`` if a positive safe window exists.
    3. ``external-trigger`` otherwise.

    The ``every-N-transactions`` cadence has the same feasibility as
    ``every-N-years`` but a higher operational cost; the function
    returns it as a runner-up rather than as the recommendation.
    """
    # EXERCISE: implement this function.
    #
    # Pick the cheapest feasible cadence in one three-branch cascade: no
    # breach gives calendar at interval Y; otherwise a safe window of at
    # least one year gives every-N-years at that window; otherwise
    # external-trigger at interval 0. every-N-transactions is never the
    # recommendation because it matches every-N-years on feasibility and
    # loses on cost, so it comes back only inside the options dict as a
    # runner-up. Return X, Y, Z, breach_years, safe_window_years,
    # recommendation, rotation_interval_years, and the full options dict, so
    # a caller can override the pick from the same call.
    #
    # Reference: Chapter 38, 'Plan the rotation cadence'
    #
    # Proved by:
    #   tests/ch38/test_wallet_mosca.py
    raise NotImplementedError("exercise: recommend_cadence")


def evaluate(Z: int, X: int = STRAND_WALLET_X, Y: int = STRAND_WALLET_Y) -> Dict[str, object]:
    """Run the recommendation under the Strand wallet anchor (X=10, Y=4).

    The default X and Y come from tests/ch36/conftest.py for the
    wallet row. Pass an alternate X or Y to model a different
    wallet's surface.
    """
    return recommend_cadence(X, Y, Z)
