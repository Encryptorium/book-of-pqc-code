"""Threshold-scheme by candidate support matrix.

The chapter operates over a fixed five-by-three matrix of candidate
primitives by threshold-protocol roles. Each cell carries a deployment
status drawn from {production, fips-final, pre-draft, research} and two
qualitative flags (admits T-of-N split, requires online combine round)
that produce the per-cell decision.

The five candidate primitives match ``aggregation_overhead.CANDIDATES``.
The three threshold-protocol roles:

- ``no-threshold``: every validator signs independently with its own
  key. The simplest deployment shape; matches Ethereum's beacon-chain
  pattern under the BLS baseline.
- ``classical-FROST``: threshold Schnorr per the FROST specification
  (Komlo and Goldberg, 2020). Discrete-log-based and therefore
  Shor-vulnerable; included only to disqualify it from the
  post-quantum candidate set.
- ``threshold-PQ``: threshold variant of a post-quantum scheme. At
  chain-tip 2026 the deployed status is research-grade for every PQ
  candidate; no NIST standard exists for threshold post-quantum
  signatures.

The function ``lookup`` returns the per-cell decision; the function
``deployment_summary`` flattens the matrix for a chapter table.
"""

from typing import Dict, List, Tuple, TypedDict


class ThresholdCell(TypedDict):
    deployment_status: str
    admits_t_of_n: bool
    requires_combine_round: bool
    rationale: str


PRIMITIVES: Tuple[str, ...] = (
    "BLS-BLS12-381",
    "ML-DSA-65",
    "SLH-DSA-128s",
    "FN-DSA-512",
    "threshold-ML-DSA",
)

THRESHOLD_ROLES: Tuple[str, ...] = (
    "no-threshold",
    "classical-FROST",
    "threshold-PQ",
)


def _cell(
    deployment_status: str,
    admits_t_of_n: bool,
    requires_combine_round: bool,
    rationale: str,
) -> ThresholdCell:
    return {
        "deployment_status": deployment_status,
        "admits_t_of_n": admits_t_of_n,
        "requires_combine_round": requires_combine_round,
        "rationale": rationale,
    }


# Each row is one primitive's per-role status. The rationale records
# the load-bearing fact for the cell decision; the chapter cites the
# rationale when the table renders.
MATRIX: Dict[str, Dict[str, ThresholdCell]] = {
    "BLS-BLS12-381": {
        "no-threshold": _cell(
            "production",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "Ethereum beacon-chain baseline; per-validator signing "
                "with pairing-based aggregation off-chain"
            ),
        ),
        "classical-FROST": _cell(
            "research-classical-only",
            admits_t_of_n=True,
            requires_combine_round=True,
            rationale=(
                "FROST is threshold Schnorr; Shor-vulnerable; not a "
                "post-quantum migration target"
            ),
        ),
        "threshold-PQ": _cell(
            "incompatible",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "BLS aggregation already collapses partials to one "
                "signature; a PQ threshold variant of BLS is not "
                "a research direction"
            ),
        ),
    },
    "ML-DSA-65": {
        "no-threshold": _cell(
            "fips-final",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "FIPS 204 final; per-validator signing with N "
                "independent signatures on-chain"
            ),
        ),
        "classical-FROST": _cell(
            "incompatible",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "FROST is Schnorr-only; ML-DSA does not admit a "
                "Schnorr-style identification protocol"
            ),
        ),
        "threshold-PQ": _cell(
            "research-grade",
            admits_t_of_n=True,
            requires_combine_round=True,
            rationale=(
                "active research direction at chain-tip 2026; multiple "
                "candidate constructions, none NIST-standardized"
            ),
        ),
    },
    "SLH-DSA-128s": {
        "no-threshold": _cell(
            "fips-final",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "FIPS 205 final; conservative-assumption preference "
                "for long-lived validator-set keys"
            ),
        ),
        "classical-FROST": _cell(
            "incompatible",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "hash-based signatures do not admit a Schnorr-style "
                "threshold variant"
            ),
        ),
        "threshold-PQ": _cell(
            "research-early",
            admits_t_of_n=True,
            requires_combine_round=True,
            rationale=(
                "less mature than threshold-lattice; the combine round "
                "for hypertree signatures is an open problem in 2026"
            ),
        ),
    },
    "FN-DSA-512": {
        "no-threshold": _cell(
            "pre-draft",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "FIPS 206 under development with no initial public "
                "draft; smallest PQ signature in the candidate set; "
                "per-validator signing"
            ),
        ),
        "classical-FROST": _cell(
            "incompatible",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "FN-DSA uses NTRU-based Gaussian sampling; the "
                "FROST framework does not transfer"
            ),
        ),
        "threshold-PQ": _cell(
            "research-early",
            admits_t_of_n=True,
            requires_combine_round=True,
            rationale=(
                "Gaussian-sampling distributed protocols are an active "
                "research direction; less mature than threshold-Dilithium"
            ),
        ),
    },
    "threshold-ML-DSA": {
        "no-threshold": _cell(
            "research-grade",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "the threshold-ML-DSA construction degenerates to "
                "plain ML-DSA-65 at T=1=N"
            ),
        ),
        "classical-FROST": _cell(
            "incompatible",
            admits_t_of_n=False,
            requires_combine_round=False,
            rationale=(
                "FROST is Schnorr-only; not the right combinator for "
                "a lattice scheme"
            ),
        ),
        "threshold-PQ": _cell(
            "research-grade",
            admits_t_of_n=True,
            requires_combine_round=True,
            rationale=(
                "the candidate slot for a post-quantum threshold "
                "primitive at chain-tip 2026"
            ),
        ),
    },
}


def lookup(primitive: str, role: str) -> Dict[str, object]:
    """Return the per-cell record for the (primitive, role) pair.

    The cell carries the deployment status at chain-tip 2026, the
    T-of-N support flag, the requires-combine-round flag, and a
    one-line rationale.
    """
    assert primitive in PRIMITIVES, f"unknown primitive: {primitive!r}"
    assert role in THRESHOLD_ROLES, f"unknown role: {role!r}"
    cell = MATRIX[primitive][role]
    return {
        "primitive": primitive,
        "role": role,
        "deployment_status": cell["deployment_status"],
        "admits_t_of_n": cell["admits_t_of_n"],
        "requires_combine_round": cell["requires_combine_round"],
        "rationale": cell["rationale"],
    }


def deployment_summary() -> List[Dict[str, object]]:
    """Flatten the full five-by-three matrix into a list of cells.

    Order matches PRIMITIVES x THRESHOLD_ROLES so a chapter table
    renders deterministically. Useful for the chapter's inline Block 2
    pretty-print and for a test that asserts the deterministic order.
    """
    out: List[Dict[str, object]] = []
    for primitive in PRIMITIVES:
        for role in THRESHOLD_ROLES:
            out.append(lookup(primitive, role))
    return out


def production_ready_at(role: str) -> List[str]:
    """Return the list of primitives whose deployment status is ``production`` for the role.

    Used by the chapter to identify the primitives an operator can
    deploy today versus those that require a research-track wait.
    """
    assert role in THRESHOLD_ROLES, f"unknown role: {role!r}"
    return [
        p
        for p in PRIMITIVES
        if MATRIX[p][role]["deployment_status"] == "production"
    ]
