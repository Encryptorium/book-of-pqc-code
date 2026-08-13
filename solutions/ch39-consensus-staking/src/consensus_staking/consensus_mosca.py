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

    per_epoch: CadenceOption = {
        "name": "per-epoch",
        "feasible": breach <= 0,
        "rotation_interval_years": 0,
        "operational_cost": "low",
        "rationale": (
            "rotate every epoch alongside the validator-set turnover; "
            "feasible only when X + Y already clears Z"
        ),
    }

    every_n_epochs: CadenceOption = {
        "name": "every-N-epochs",
        "feasible": safe_window >= 1 and breach > 0,
        "rotation_interval_years": safe_window,
        "operational_cost": "medium",
        "rationale": (
            "rotate every N epochs with N at most Z - Y in years so "
            "effective key reuse plus migration clears the Mosca window"
        ),
    }

    every_n_validator_rotations: CadenceOption = {
        "name": "every-N-validator-rotations",
        "feasible": safe_window >= 1 and breach > 0,
        "rotation_interval_years": safe_window,
        "operational_cost": "medium-high",
        "rationale": (
            "rotate alongside validator-set exit-and-entry; useful when "
            "the validator set turns over faster than the calendar "
            "interval implied by Z - Y"
        ),
    }

    hard_fork_trigger: CadenceOption = {
        "name": "hard-fork-trigger",
        "feasible": True,
        "rotation_interval_years": 0,
        "operational_cost": "high",
        "rationale": (
            "rotate at a named hard-fork event; the default when Z <= Y "
            "leaves no room for a fixed-interval rotation"
        ),
    }

    return {
        "per-epoch": per_epoch,
        "every-N-epochs": every_n_epochs,
        "every-N-validator-rotations": every_n_validator_rotations,
        "hard-fork-trigger": hard_fork_trigger,
    }


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
    breach = breach_years(X, Y, Z)
    options = cadence_options(X, Y, Z)
    safe_window = max(0, Z - Y)

    if breach <= 0:
        recommendation = "per-epoch"
        recommended_interval = 0
    elif safe_window >= 1:
        recommendation = "every-N-epochs"
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
    Z: int, X: int = STRAND_CONSENSUS_X, Y: int = STRAND_CONSENSUS_Y
) -> Dict[str, object]:
    """Run the recommendation under the Strand consensus anchor (X=2, Y=1).

    The default X and Y come from tests/ch36/conftest.py for the
    consensus row. Pass an alternate X or Y to model a different
    chain's consensus surface.
    """
    return recommend_cadence(X, Y, Z)
