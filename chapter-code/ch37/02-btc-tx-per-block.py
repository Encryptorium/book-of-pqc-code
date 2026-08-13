# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 37: Layer-1 signature migration: Bitcoin and Ethereum
# Section: "Cutover with a composite signature"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch37-l1-signature-migration/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch37/02-btc-tx-per-block.py

# Block 2: pedagogical slice of l1_migration.throughput_compare.rank (stdlib only).
BTC_BLOCK_WEIGHT_LIMIT = 4_000_000
BTC_TX_OVERHEAD_WU = 200
ETH_BLOCK_GAS_LIMIT = 60_000_000
ETH_TX_BASE_GAS = 21_000
ETH_GAS_PER_NONZERO_CALLDATA_BYTE = 16

CANDIDATES = {
    "ECDSA-secp256k1":    {"sig": 64,       "pk":   33, "reveal_pk": False},
    "ML-DSA-65":          {"sig": 3309,     "pk": 1952, "reveal_pk": True},
    "SLH-DSA-128s":       {"sig": 7856,     "pk":   32, "reveal_pk": True},
    "Ed25519+ML-DSA-65":  {"sig": 64+3309,  "pk": 32+1952, "reveal_pk": True},
}


def btc_tx_per_block(primitive):
    c = CANDIDATES[primitive]
    witness = c["sig"] + (c["pk"] if c["reveal_pk"] else 0)
    return BTC_BLOCK_WEIGHT_LIMIT // (BTC_TX_OVERHEAD_WU + witness)


def eth_tx_per_block(primitive):
    # Calldata-only lower bound; pk is assumed in wallet contract state.
    per_tx = ETH_TX_BASE_GAS + CANDIDATES[primitive]["sig"] * ETH_GAS_PER_NONZERO_CALLDATA_BYTE
    return ETH_BLOCK_GAS_LIMIT // per_tx


def rank(budget):
    assert budget in ("btc", "eth"), f"unknown budget: {budget!r}"
    fn = btc_tx_per_block if budget == "btc" else eth_tx_per_block
    scored = [(p, fn(p)) for p in CANDIDATES]
    return sorted(scored, key=lambda pair: (-pair[1], pair[0]))


for budget in ("btc", "eth"):
    print(f"-- {budget} --")
    for primitive, count in rank(budget):
        print(f"{primitive:<19} {count:>6}")
# ==> -- btc --
# ==> ECDSA-secp256k1      15151
# ==> ML-DSA-65              732
# ==> Ed25519+ML-DSA-65      719
# ==> SLH-DSA-128s           494
# ==> -- eth --
# ==> ECDSA-secp256k1       2724
# ==> ML-DSA-65              811
# ==> Ed25519+ML-DSA-65      800
# ==> SLH-DSA-128s           409
