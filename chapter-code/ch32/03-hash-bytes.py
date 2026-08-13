# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 32: PQ-secure commitment schemes
# Section: "Merkle: hash-based binding"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch32-commitment-schemes/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch32/03-hash-bytes.py

# Block 3: pedagogical slice of commitment_schemes.merkle.commit_leaves and
# quantum_collision_bits_{bht,cnps} (stdlib only).

import hashlib

def hash_bytes(data, width_bits):
    # SHAKE128's collision-resistance security strength is capped at
    # 128 bits regardless of output length (FIPS 202 Appendix A.1), so
    # routing 384/512-bit outputs through SHAKE128 would not actually
    # deliver the BHT/CNPS margins computed below. SHAKE256 is the
    # right XOF for output widths past 256 bits.
    if width_bits == 256:
        return hashlib.sha256(data).digest()
    if width_bits >= 384:
        return hashlib.shake_256(data).digest(width_bits // 8)
    return hashlib.shake_128(data).digest(width_bits // 8)

def merkle_root(leaves, arity, width_bits):
    zero = bytes(width_bits // 8)
    level = [hash_bytes(leaf, width_bits) for leaf in leaves]
    padded = arity
    while padded < len(level):
        padded *= arity
    level += [zero] * (padded - len(level))
    while len(level) > 1:
        level = [
            hash_bytes(b"".join(level[i:i + arity]), width_bits)
            for i in range(0, len(level), arity)
        ]
    return level[0]

leaves = [f"eval-{i}".encode() for i in range(8)]
root_bin = merkle_root(leaves, arity=2, width_bits=256)
root_quad = merkle_root(leaves, arity=4, width_bits=256)
print(f"binary root first 4 bytes = {root_bin[:4].hex()}")
print(f"quaternary root first 4 bytes = {root_quad[:4].hex()}")

for n in (256, 384, 512):
    bht = n // 3
    cnps = (2 * n) // 5
    print(f"n={n}: BHT={bht}, CNPS={cnps}")
# ==> binary root first 4 bytes = e3a3d759
# ==> quaternary root first 4 bytes = b1add67a
# ==> n=256: BHT=85, CNPS=102
# ==> n=384: BHT=128, CNPS=153
# ==> n=512: BHT=170, CNPS=204
