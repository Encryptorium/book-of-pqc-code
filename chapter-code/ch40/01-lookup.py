# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 40: Quantum threats to ZK rollups
# Section: "Decompose the verifier into layers and pick a per-layer candidate"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch40-zk-rollups-under-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch40/01-lookup.py

# Block 1: pedagogical slice of zk_rollups.verifier_layers
# (stdlib only).
LAYERS = (
    "L1-arithmetization",
    "L2-commitment",
    "L3-protocol-logic",
    "L4-fiat-shamir",
)

# Per-cell decision: post-quantum status per (layer, candidate).
# off-chain means the layer runs off-chain in the prover and the
# verifier-contract never executes the layer's logic.
MATRIX = {
    "L1-arithmetization": {
        "AIR":      "off-chain",
        "Plonkish": "off-chain",
    },
    "L2-commitment": {
        "KZG":         "shor-broken",
        "FRI":         "grover-weakened",
        "lattice-PCS": "pq-secure",
    },
    "L3-protocol-logic": {
        "FRI-IOP": "off-chain",
        "IPA-IOP": "shor-broken",
    },
    "L4-fiat-shamir": {
        "SHA-256":    "grover-weakened",
        "SHAKE-256":  "grover-weakened",
        "Keccak-256": "grover-weakened",
    },
}


def lookup(layer, candidate):
    assert layer in LAYERS
    assert candidate in MATRIX[layer]
    return MATRIX[layer][candidate]


# Print the load-bearing on-chain layers (L2 and L4) for a small
# candidate set. The off-chain layers L1 and L3 carry no on-chain
# decision.
print(f"{'layer':<19} {'candidate':<14} pq_status")
for layer in ("L2-commitment", "L4-fiat-shamir"):
    for candidate in MATRIX[layer]:
        status = lookup(layer, candidate)
        print(f"{layer:<19} {candidate:<14} {status}")
# ==> layer               candidate      pq_status
# ==> L2-commitment       KZG            shor-broken
# ==> L2-commitment       FRI            grover-weakened
# ==> L2-commitment       lattice-PCS    pq-secure
# ==> L4-fiat-shamir      SHA-256        grover-weakened
# ==> L4-fiat-shamir      SHAKE-256      grover-weakened
# ==> L4-fiat-shamir      Keccak-256     grover-weakened
