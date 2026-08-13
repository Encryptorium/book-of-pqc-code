# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 35: Case studies: Zcash, ZKsync, Starknet
# Section: "Migration cost, parameter bump, and pending-literature risk"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch35-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch35/06-classify.py

# Block 6: taxonomy grid classifier. Takes a dict describing a
# deployed system's L2 and L4 layers and returns the grid cell color
# per Figure 31.2 plus the CNFL route per the two specializations from
# the math-preliminaries section of this chapter. Red dominates amber
# dominates green. Source: Ch 31 Figure 31.2; Renz (2026) Section 6.
L2_COLORS = {"pairing": "red", "ipa_dlp": "red",
             "fri": "amber", "lattice_pcs": "amber"}
L4_COLORS = {"crs": "red", "fs_over_dlp": "red",
             "fs_tier1": "amber", "fs_tier2": "amber",
             "fs_tier3_classical_rom": "amber"}


def classify(system: dict) -> dict:
    if "l2" not in system or "l4" not in system:
        raise ValueError("system dict must include l2 and l4 keys")
    l2_color = L2_COLORS.get(system["l2"])
    l4_color = L4_COLORS.get(system["l4"])
    if l2_color is None:
        raise ValueError(f"unknown l2 value: {system['l2']!r}")
    if l4_color is None:
        raise ValueError(f"unknown l4 value: {system['l4']!r}")
    order = {"red": 0, "amber": 1, "green": 2}
    dominant = min(l2_color, l4_color, key=lambda c: order[c])
    if dominant == "red":
        if system["l2"] == "pairing":
            cnfl = "pairing forward forgery plus retroactive soundness erosion"
        else:
            cnfl = "DLP forward forgery plus retroactive soundness erosion"
    else:
        cnfl = "L2 hash binding (BHT/CNPS) plus L4 Fiat-Shamir parameter point, QROM-pending"
    return {"cell": (l2_color, l4_color), "posture": dominant,
            "cnfl_route": cnfl}


sapling = classify({"l2": "pairing", "l4": "crs"})
orchard = classify({"l2": "ipa_dlp", "l4": "fs_over_dlp"})
boojum_outer = classify({"l2": "pairing", "l4": "crs"})
boojum_inner = classify({"l2": "fri", "l4": "fs_tier3_classical_rom"})
ethstark = classify({"l2": "fri", "l4": "fs_tier3_classical_rom"})
print(sapling["posture"], orchard["posture"], boojum_outer["posture"],
      boojum_inner["posture"], ethstark["posture"])
# ==> red red red amber amber
