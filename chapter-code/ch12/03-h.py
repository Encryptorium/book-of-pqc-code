# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "Hash derivations from a single SHAKE"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/03-h.py

import hashlib


def H(data, outlen):
    return hashlib.shake_256(data).digest(outlen)


def integer_to_bytes(x, length):
    return x.to_bytes(length, "little")


# ML-DSA-65 module shape.
k, l = 6, 5

# KeyGen seed split: (rho, rho', K) = H(xi || k || l, 128).
xi = bytes.fromhex(
    "A991FD42B071D49C48AE3E75C647459E0DAAD1E1BA356A04801912D3294BCFF8"
)
raw = H(xi + integer_to_bytes(k, 1) + integer_to_bytes(l, 1), 128)
rho, rho_prime, K = raw[:32], raw[32:96], raw[96:128]

# The public-key transcript tr = H(pk, 64), the message representative
# mu = H(tr || M', 64), and the per-signature mask seed rho'' = H(K || rnd || mu, 64).
pk_stub = bytes(1952)                       # length of a real ML-DSA-65 pk
tr = H(pk_stub, 64)
m_prime = integer_to_bytes(0, 1) + integer_to_bytes(0, 1) + b"sign me"
mu = H(tr + m_prime, 64)
rho_dprime = H(K + bytes(32) + mu, 64)      # rnd = 0^32 is the deterministic variant

print("H is SHAKE256 :", H(b"", 32) == hashlib.shake_256(b"").digest(32))
print("len(rho, rho', K) =", (len(rho), len(rho_prime), len(K)))
print("len(tr, mu, rho'') =", (len(tr), len(mu), len(rho_dprime)))
print("mu[:8] =", mu[:8].hex())
# ==> H is SHAKE256 : True
# ==> len(rho, rho', K) = (32, 64, 32)
# ==> len(tr, mu, rho'') = (64, 64, 64)
# ==> mu[:8] = 5cc3785bc60dd808
