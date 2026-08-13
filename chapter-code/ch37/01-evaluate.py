# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 37: Layer-1 signature migration: Bitcoin and Ethereum
# Section: "Choose the candidate"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch37-l1-signature-migration/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch37/01-evaluate.py

# Block 1: pedagogical slice of l1_migration.byte_budget.evaluate (stdlib only).
BTC_BLOCK_WEIGHT_LIMIT = 4_000_000
BTC_TX_OVERHEAD_WU = 200
ETH_BLOCK_GAS_LIMIT = 60_000_000  # EIP-7935 / Fusaka, Dec 2025
ETH_TX_BASE_GAS = 21_000
ETH_GAS_PER_NONZERO_CALLDATA_BYTE = 16

# ECDSA-secp256k1 is the Taproot key-path baseline: the tweaked public
# key lives in the output script, so the witness reveals only the sig.
# The PQ candidates are modeled as P2WPKH-style commit-then-reveal,
# so the spend witness reveals both the public key and the signature.
CANDIDATES = {
    "ECDSA-secp256k1":     {"sig_bytes": 64,        "pk_bytes":   33, "reveal_pk": False},
    "ML-DSA-65":           {"sig_bytes": 3309,      "pk_bytes": 1952, "reveal_pk": True},
    "SLH-DSA-128s":        {"sig_bytes": 7856,      "pk_bytes":   32, "reveal_pk": True},
    "Ed25519+ML-DSA-65":   {"sig_bytes": 64+3309,   "pk_bytes": 32+1952, "reveal_pk": True},
}


def evaluate(primitive):
    assert primitive in CANDIDATES, f"unknown primitive: {primitive!r}"
    sig = CANDIDATES[primitive]["sig_bytes"]
    pk = CANDIDATES[primitive]["pk_bytes"]
    witness = sig + (pk if CANDIDATES[primitive]["reveal_pk"] else 0)
    btc_tx = BTC_BLOCK_WEIGHT_LIMIT // (BTC_TX_OVERHEAD_WU + witness)
    # Ethereum side assumes the wallet contract stores the public key
    # in state (paid at deployment), so only the signature rides in
    # calldata per user operation.
    eth_per_tx_gas = ETH_TX_BASE_GAS + sig * ETH_GAS_PER_NONZERO_CALLDATA_BYTE
    eth_tx = ETH_BLOCK_GAS_LIMIT // eth_per_tx_gas
    return sig, pk, btc_tx, eth_tx


for primitive in CANDIDATES:
    sig, pk, btc, eth = evaluate(primitive)
    print(f"{primitive:<19} sig={sig:>5} pk={pk:>5} btc_tx={btc:>5} eth_tx={eth:>4}")
# ==> ECDSA-secp256k1     sig=   64 pk=   33 btc_tx=15151 eth_tx=2724
# ==> ML-DSA-65           sig= 3309 pk= 1952 btc_tx=  732 eth_tx= 811
# ==> SLH-DSA-128s        sig= 7856 pk=   32 btc_tx=  494 eth_tx= 409
# ==> Ed25519+ML-DSA-65   sig= 3373 pk= 1984 btc_tx=  719 eth_tx= 800
