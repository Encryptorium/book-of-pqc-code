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
    assert X >= 0 and Y >= 0 and Z >= 0, "X, Y, Z must be non-negative"
    return X + Y - Z


def cadence_options(X: int, Y: int, Z: int) -> Dict[str, CadenceOption]:
    """Per-cadence feasibility and operational cost under the (X, Y, Z) tuple.

    Each cadence carries a feasibility flag, a rotation interval in
    years, an operational-cost label, and a one-line rationale. The
    recommendation function consumes this dict to pick the cheapest
    feasible cadence.
    """
    breach = breach_years(X, Y, Z)
    safe_window = max(0, Z - Y)

    calendar: CadenceOption = {
        "name": "calendar",
        "feasible": breach <= 0,
        "rotation_interval_years": Y,
        "operational_cost": "low",
        "rationale": (
            "fixed calendar rotation aligned with address-book turnover; "
            "feasible only when X + Y already clears Z"
        ),
    }

    every_n_years: CadenceOption = {
        "name": "every-N-years",
        "feasible": safe_window >= 1 and breach > 0,
        "rotation_interval_years": safe_window,
        "operational_cost": "medium",
        "rationale": (
            "rotate every N years with N at most Z - Y so effective seed "
            "lifetime plus migration clears the Mosca window"
        ),
    }

    every_n_transactions: CadenceOption = {
        "name": "every-N-transactions",
        "feasible": safe_window >= 1 and breach > 0,
        "rotation_interval_years": safe_window,
        "operational_cost": "medium-high",
        "rationale": (
            "rotate every N spends; caps per-key exposure by transaction "
            "count, useful when seed age is dominated by spend frequency"
        ),
    }

    external_trigger: CadenceOption = {
        "name": "external-trigger",
        "feasible": True,
        "rotation_interval_years": 0,
        "operational_cost": "high",
        "rationale": (
            "rotate on a named external signal; the default when Z <= Y "
            "leaves no room for a fixed-interval rotation"
        ),
    }

    return {
        "calendar": calendar,
        "every-N-years": every_n_years,
        "every-N-transactions": every_n_transactions,
        "external-trigger": external_trigger,
    }


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
    breach = breach_years(X, Y, Z)
    options = cadence_options(X, Y, Z)
    safe_window = max(0, Z - Y)

    if breach <= 0:
        recommendation = "calendar"
        recommended_interval = Y
    elif safe_window >= 1:
        recommendation = "every-N-years"
        recommended_interval = safe_window
    else:
        recommendation = "external-trigger"
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


def evaluate(Z: int, X: int = STRAND_WALLET_X, Y: int = STRAND_WALLET_Y) -> Dict[str, object]:
    """Run the recommendation under the Strand wallet anchor (X=10, Y=4).

    The default X and Y come from tests/ch36/conftest.py for the
    wallet row. Pass an alternate X or Y to model a different
    wallet's surface.
    """
    return recommend_cadence(X, Y, Z)
