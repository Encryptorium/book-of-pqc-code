"""The four-layer decomposition itself, as data plus three lookups.

Chapter 31's Table 31.1 names the four layers, Table 31.2 sorts five
representative systems by their L2 commitment and L4 transform, and the
chapter's two figures colour the result. This module is that table,
written so a test can pin each assignment to the chapter rather than
leaving the layer labels to prose alone.

There is no cryptography here. The module classifies; it computes
nothing an adversary could attack. Its value is that a per-layer posture
claim becomes a value some test can contradict, which is the one thing a
table drawn in an SVG cannot offer.

The one arithmetic routine, ``hash_bits_for_pq_collision``, sizes a hash
output against a target collision strength. It is the inverse of Chapter
32's ``commitment_schemes.merkle.quantum_collision_bits_bht``, which
goes the other way, from a width to the bits it delivers.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

# The posture vocabulary, worst first. `thinnest_layer` ranks by this
# order, so the tuple is the ranking and not merely a list of the values
# that happen to appear.
#
# "pq-assumption" sits below "safe" on purpose. A lattice commitment is
# unbroken, but its L2 binding rests on a computational assumption,
# where L1 rests on nothing an adversary can attack. "not-applicable"
# sits last because a layer a system does not have is a layer with
# nothing in it to audit, which is not the same as that layer being an
# advantage: Chapter 31 says outright that Groth16's missing L4 is not a
# safety advantage but the shape that makes its L2 break structural.
POSTURES = (
    "broken",
    "weakened",
    "pending",
    "pq-assumption",
    "safe",
    "not-applicable",
)


@dataclass(frozen=True)
class Layer:
    """One layer of the decomposition: what it is and what it does."""

    key: str
    name: str
    role: str


# Table 31.1. The four layers, in order.
LAYERS: tuple[Layer, ...] = (
    Layer(
        "L1",
        "Arithmetization / encoding",
        "Expresses a computation as algebraic constraints or polynomials "
        "over a finite field.",
    ),
    Layer(
        "L2",
        "Commitment + consistency",
        "Binds the prover to witness data and exposes a consistency-check "
        "mechanism the verifier can run on a small number of queries.",
    ),
    Layer(
        "L3",
        "Protocol logic",
        "The IOP or argument structure that reduces a statement to a "
        "sequence of oracle-access checks.",
    ),
    Layer(
        "L4",
        "Non-interactivity + extraction",
        "The Fiat-Shamir transform, the oracle model (ROM or QROM), and "
        "the extractability assumption.",
    ),
)

LAYER_KEYS = tuple(layer.key for layer in LAYERS)


@dataclass(frozen=True)
class SystemProfile:
    """One row of Table 31.2, with the mechanism named at each layer.

    ``l2_posture`` and ``l4_posture`` are the only two the chapter states
    directly. L1 is uniformly safe because it carries no cryptographic
    assumption, and L3 inherits L2, so neither needs its own field.
    """

    key: str
    label: str
    arithmetization: str
    commitment: str
    protocol_logic: str
    non_interactivity: str
    l2_posture: str
    l4_posture: str


# Table 31.2's five rows, keyed by L2 commitment choice. The `label`
# names the systems the chapter gives as examples for that row.
SYSTEMS: dict[str, SystemProfile] = {
    "groth16": SystemProfile(
        key="groth16",
        label="Groth16",
        arithmetization="R1CS / QAP",
        commitment="Pairing equation (KZG-style, SRS-bound)",
        protocol_logic="Algebraic NIZK",
        non_interactivity="none (no Fiat-Shamir)",
        l2_posture="broken",
        l4_posture="not-applicable",
    ),
    "plonk_kzg": SystemProfile(
        key="plonk_kzg",
        label="PLONK with KZG",
        arithmetization="PLONKish gates",
        commitment="KZG",
        protocol_logic="Polynomial identities",
        non_interactivity="Fiat-Shamir",
        l2_posture="broken",
        l4_posture="pending",
    ),
    "ipa_fs": SystemProfile(
        key="ipa_fs",
        label="Halo 2, Bulletproofs",
        arithmetization="PLONKish gates (Halo 2), arithmetic circuit (Bulletproofs)",
        commitment="IPA over a discrete-log-hard group",
        protocol_logic="Inner-product argument",
        non_interactivity="Fiat-Shamir",
        l2_posture="broken",
        l4_posture="pending",
    ),
    "starks_fri": SystemProfile(
        key="starks_fri",
        label="STARKs, Plonky2",
        arithmetization="AIR",
        commitment="Merkle + FRI",
        protocol_logic="IOP (proximity + consistency)",
        non_interactivity="Fiat-Shamir",
        l2_posture="weakened",
        l4_posture="pending",
    ),
    "lattice_fs": SystemProfile(
        key="lattice_fs",
        label="Lattice-commitment systems",
        arithmetization="varies",
        commitment="Lattice (module-SIS / ring-SIS)",
        protocol_logic="Polynomial or IOP argument",
        non_interactivity="Fiat-Shamir",
        l2_posture="pq-assumption",
        l4_posture="pending",
    ),
}


def layer_posture(system: str, layer: str) -> str:
    """The quantum-safety posture of one layer of one system.

    L1 is ``"safe"`` for every system: it is a statement about
    finite-field arithmetic and carries no cryptographic assumption. L2
    and L4 come from the system's profile. L3 returns whatever L2
    returns, because in the systems Part VI covers L3 is largely
    information-theoretic once the L2 binding interface is fixed, so its
    posture is inherited rather than its own.

    Raises ``ValueError`` for an unknown system or layer key.
    """
    # EXERCISE: implement this function.
    #
    # Reject an unknown system or layer key with ValueError before reading
    # anything. L1 is 'safe' for every system, because it is a statement
    # about finite-field arithmetic and carries no cryptographic assumption
    # at all. L2 and L4 come from the system's own profile. L3 returns
    # whatever L2 returns rather than carrying a field of its own: in the
    # systems Part VI covers, L3 is largely information-theoretic once the
    # L2 binding interface is fixed, so its posture is inherited and a
    # separate L3 field would be a second place for the same fact to go
    # stale.
    #
    # Reference: Chapter 31, 'Cryptanalysis: per-layer quantum-safety'
    #
    # Proved by:
    #   tests/ch31/test_layers.py
    raise NotImplementedError("exercise: layer_posture")


def thinnest_layer(system: str) -> str:
    """The layer to audit first: the worst posture, earliest layer wins.

    Rank the four layers by ``POSTURES`` and return the worst. Where two
    layers tie, return the lower-numbered one. That tie-break is what
    makes the answer L2 rather than L3 for every discrete-log system,
    and it is the right answer for the same reason the chapter gives:
    L3 inherits L2's posture, so auditing L3 in isolation tells the
    operator nothing L2 has not already told them.

    Raises ``ValueError`` for an unknown system.
    """
    # EXERCISE: implement this function.
    #
    # Rank the four layers by their position in POSTURES, which is ordered
    # worst first, and return the worst one. Where two layers tie, return
    # the lower-numbered one; min over LAYER_KEYS gives that for free,
    # because it returns the first minimal element. The tie-break is the
    # whole point rather than a detail: L3 inherits L2, so every
    # discrete-log system ties at L2 and L3, and the answer has to be L2
    # because auditing L3 in isolation tells an operator nothing L2 has not
    # already told them. Check what the ordering does to a lattice system
    # before assuming the answer is always L2.
    #
    # Reference: Chapter 31, 'Tradeoffs across commitment and non-interactivity choices'
    #
    # Proved by:
    #   tests/ch31/test_layers.py
    raise NotImplementedError("exercise: thinnest_layer")


def hash_bits_for_pq_collision(target_bits: int, model: str = "bht") -> int:
    """Minimum hash output width for ``target_bits`` of PQ collision security.

    Under the Brassard-Hoyer-Tapp query-model bound an ``n``-bit hash
    delivers about ``n / 3`` bits of quantum collision resistance, so
    reaching ``target_bits`` needs ``n >= 3 * target_bits``. Under the
    Chailloux-Naya-Plasencia-Schrottenloher bound, which assumes no
    quantum random-access classical memory, the exponent is ``2n / 5``
    and the requirement is ``n >= 5 * target_bits / 2``.

    At a 128-bit target the BHT model returns 384, which is why Chapter
    31 says a STARK deployment holding that target moves to a 384-bit or
    larger hash output. Both figures are worst-case theoretical targets
    rather than literal deployment-cost estimates.

    Raises ``ValueError`` for a non-positive target or an unknown model.
    """
    # EXERCISE: implement this function.
    #
    # Invert the collision bound. Under Brassard-Hoyer-Tapp an n-bit hash
    # delivers about n/3 bits, so a target of t bits needs n >= 3t. Under
    # Chailloux-Naya-Plasencia-Schrottenloher, which assumes no quantum
    # random-access classical memory, the exponent is 2n/5 and the
    # requirement is n >= 5t/2. Round the second one up rather than down: a
    # width that lands half a bit short of the target does not reach it.
    # Reject a non-positive target and an unrecognised model with
    # ValueError.
    #
    # Reference: Chapter 31, 'Cryptanalysis: per-layer quantum-safety'
    #
    # Proved by:
    #   tests/ch31/test_layers.py
    raise NotImplementedError("exercise: hash_bits_for_pq_collision")
