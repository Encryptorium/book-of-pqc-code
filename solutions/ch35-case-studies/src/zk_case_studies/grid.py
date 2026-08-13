"""The (L2, L4) grid: colour tables, the dominance rule, and the classifier."""

__all__ = ["L2_COLORS", "L4_COLORS", "ORDER", "classify", "dominant_color"]

L2_COLORS = {"pairing": "red", "ipa_dlp": "red",
             "fri": "amber", "lattice_pcs": "amber"}
L4_COLORS = {"crs": "red", "fs_over_dlp": "red",
             "fs_tier1": "amber", "fs_tier2": "amber",
             "fs_tier3_classical_rom": "amber"}

# Severity order. A cell takes the more severe of its two colours, which is
# why the ZKsync composite reads red: the on-chain verifier meets the outer
# wrapper first, and a forger who breaks it never touches the inner STARK.
ORDER = {"red": 0, "amber": 1, "green": 2}


def dominant_color(*colors: str) -> str:
    """Return the most severe of the colours given."""
    if not colors:
        raise ValueError("need at least one colour")
    for color in colors:
        if color not in ORDER:
            raise ValueError(f"unknown colour: {color!r}")
    return min(colors, key=lambda c: ORDER[c])


def classify(system: dict) -> dict:
    """Place a system in the grid and name its CNFL route."""
    if "l2" not in system or "l4" not in system:
        raise ValueError("system dict must include l2 and l4 keys")
    l2_color = L2_COLORS.get(system["l2"])
    l4_color = L4_COLORS.get(system["l4"])
    if l2_color is None:
        raise ValueError(f"unknown l2 value: {system['l2']!r}")
    if l4_color is None:
        raise ValueError(f"unknown l4 value: {system['l4']!r}")
    dominant = dominant_color(l2_color, l4_color)
    if dominant == "red":
        if system["l2"] == "pairing":
            cnfl = "pairing forward forgery plus retroactive soundness erosion"
        else:
            cnfl = "DLP forward forgery plus retroactive soundness erosion"
    else:
        cnfl = ("L2 hash binding (BHT/CNPS) plus L4 Fiat-Shamir parameter"
                " point, QROM-pending")
    return {"cell": (l2_color, l4_color), "posture": dominant,
            "cnfl_route": cnfl}
