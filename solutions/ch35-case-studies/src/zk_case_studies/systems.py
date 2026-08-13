"""The six deployed configurations Chapter 35 walks.

Each record carries the layer assignment that decides its grid cell and the
one primitive fact that distinguishes it from the configurations sharing that
cell. Sapling and the ZKsync outer wrapper occupy the same cell, as do the
ZKsync inner, ethSTARK / Stone, and Stwo; the ``detail`` field is what keeps
them from being interchangeable.
"""

from .grid import classify

__all__ = ["SYSTEMS", "STWO_DEFAULTS", "names", "posture"]

SYSTEMS = {
    "sapling": {
        "label": "Zcash Sapling",
        "l2": "pairing",
        "l4": "crs",
        "detail": "Groth16 over BLS12-381",
        "transition": "replacement",
    },
    "orchard": {
        "label": "Zcash Orchard",
        "l2": "ipa_dlp",
        "l4": "fs_over_dlp",
        "detail": "Halo 2 IPA over the Pallas and Vesta cycle",
        "transition": "replacement",
    },
    "boojum_outer": {
        "label": "ZKsync Era outer wrapper",
        "l2": "pairing",
        "l4": "crs",
        "detail": "pairing-based SNARK wrapper read first by the L1 verifier",
        "transition": "replacement",
    },
    "boojum_inner": {
        "label": "ZKsync Era inner",
        "l2": "fri",
        "l4": "fs_tier3_classical_rom",
        "detail": "Merkle plus FRI over the Goldilocks field",
        "transition": "parameter bumps",
    },
    "ethstark": {
        "label": "Starknet ethSTARK / Stone (legacy)",
        "l2": "fri",
        "l4": "fs_tier3_classical_rom",
        "detail": "Merkle plus FRI over a 61-bit prime base field",
        "transition": "parameter bumps",
    },
    "stwo": {
        "label": "Starknet Stwo (current)",
        "l2": "fri",
        "l4": "fs_tier3_classical_rom",
        "detail": "Circle STARK over Mersenne-31",
        "transition": "parameter bumps",
    },
}

# Published in the starkware-libs/stwo-cairo README. Stwo is the only system
# in the chapter whose parameters are published rather than illustrative.
STWO_DEFAULTS = {"n_queries": 70, "pow_bits": 26, "log_blowup": 1}


def names() -> list[str]:
    """The system keys, in the order the chapter walks them."""
    return list(SYSTEMS)


def posture(name: str) -> dict:
    """Classify one named system and attach its transition scope."""
    if name not in SYSTEMS:
        raise ValueError(f"unknown system: {name!r}")
    record = SYSTEMS[name]
    result = classify(record)
    result["label"] = record["label"]
    result["transition"] = record["transition"]
    return result
