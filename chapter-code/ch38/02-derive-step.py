# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 38: Wallets, addresses, and key rotation
# Section: "Design the derivation tree"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch38-wallets-addresses-key-rotation/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch38/02-derive-step.py

# Block 2: pedagogical slice of wallet_rotation.derivation_tree (stdlib only).
import hmac
from hashlib import sha512

# ECDSA-secp256k1 admits a public-key-only derivation (scalar offset on the
# curve), so non-hardened branches survive. Lattice and hash primitives have
# no such map; only hardened branches survive.
NON_HARDENED_OK = {
    "ECDSA-secp256k1":   True,
    "ML-DSA-65":         False,
    "SLH-DSA-128s":      False,
    "Ed25519+ML-DSA-65": False,
    "XMSS-MT":           False,
    "LMS":               False,
}


def derive_step(parent_secret, chain_code, index, hardened):
    if hardened:
        idx_bytes = (index | 0x80000000).to_bytes(4, "big")
        data = b"\x00" + parent_secret + idx_bytes
    else:
        # Pedagogical placeholder: real BIP-32 non-hardened mode hashes
        # the serialized parent public key plus the index. This walker
        # substitutes parent_secret so the chain-code propagation continues
        # past non-hardened steps; the survival flag is the actual signal.
        data = parent_secret + index.to_bytes(4, "big")
    out = hmac.new(chain_code, data, sha512).digest()
    return out[:32], out[32:]


def walk(primitive, master_seed, path):
    master = hmac.new(b"Bitcoin seed", master_seed, sha512).digest()
    secret, chain_code = master[:32], master[32:]
    rows = [f"  {'master':<8} supported"]
    for raw in [p for p in path.split("/")[1:] if p]:
        hardened = raw.endswith("'")
        idx = int(raw[:-1] if hardened else raw)
        secret, chain_code = derive_step(secret, chain_code, idx, hardened)
        label = f"m/{idx}{'h' if hardened else ' '}"
        flag = "supported" if (hardened or NON_HARDENED_OK[primitive]) else "NOT supported"
        rows.append(f"  {label:<8} {flag}")
    return rows


SEED = bytes.fromhex(
    "000102030405060708090a0b0c0d0e0f"
    "101112131415161718191a1b1c1d1e1f"
)
PATH = "m/44'/0'/0'/0/0"
for primitive in ("ECDSA-secp256k1", "ML-DSA-65"):
    print(f"-- {primitive} on {PATH} --")
    for row in walk(primitive, SEED, PATH):
        print(row)
# ==> -- ECDSA-secp256k1 on m/44'/0'/0'/0/0 --
# ==>   master   supported
# ==>   m/44h    supported
# ==>   m/0h     supported
# ==>   m/0h     supported
# ==>   m/0      supported
# ==>   m/0      supported
# ==> -- ML-DSA-65 on m/44'/0'/0'/0/0 --
# ==>   master   supported
# ==>   m/44h    supported
# ==>   m/0h     supported
# ==>   m/0h     supported
# ==>   m/0      NOT supported
# ==>   m/0      NOT supported
