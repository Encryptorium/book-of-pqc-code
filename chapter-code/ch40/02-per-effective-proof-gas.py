# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 40: Quantum threats to ZK rollups
# Section: "Quantify the per-proof gas-cost change"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch40-zk-rollups-under-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch40/02-per-effective-proof-gas.py

# Block 2: pedagogical slice of zk_rollups.gas_budget
# (stdlib only).
ETH_BLOCK_GAS_LIMIT = 60_000_000  # EIP-7935 EL-client default; Fusaka, December 2025.

# Per-proof gas anchors at chain-tip 2026 (ethSTARK-shaped).
GAS_PER_PROOF = {
    "legacy-sha256-stark":      5_000_000,
    "wider-hash-stark":         6_500_000,
    "recursive-outer":          7_000_000,
}
RECURSIVE_BATCH = 100  # inner proofs per outer recursive proof.


def per_effective_proof_gas(config):
    if config == "recursive-stark-wrapper":
        return GAS_PER_PROOF["recursive-outer"] // RECURSIVE_BATCH
    return GAS_PER_PROOF[config]


def proofs_per_block_max(config):
    if config == "recursive-stark-wrapper":
        outer = ETH_BLOCK_GAS_LIMIT // GAS_PER_PROOF["recursive-outer"]
        return outer * RECURSIVE_BATCH
    return ETH_BLOCK_GAS_LIMIT // GAS_PER_PROOF[config]


CONFIGS = (
    "legacy-sha256-stark",
    "wider-hash-stark",
    "recursive-stark-wrapper",
)

legacy_gas = GAS_PER_PROOF["legacy-sha256-stark"]
print(f"{'configuration':<26} {'gas/proof':>10} {'factor':>8} {'max/block':>10}")
for config in CONFIGS:
    gas = per_effective_proof_gas(config)
    factor = gas / legacy_gas
    max_per_block = proofs_per_block_max(config)
    print(f"{config:<26} {gas:>10,} {factor:>8.3f} {max_per_block:>10}")
# ==> configuration               gas/proof   factor  max/block
# ==> legacy-sha256-stark         5,000,000    1.000         12
# ==> wider-hash-stark            6,500,000    1.300          9
# ==> recursive-stark-wrapper        70,000    0.014        800
