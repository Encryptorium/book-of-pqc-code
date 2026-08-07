# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "A concrete ML-KEM-768 parameter and seed derivation"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/01-a-concrete-ml-kem-768-parameter-and-seed.py

import hashlib

# ML-KEM-768 parameter constants from FIPS 203 Section 8 Table 2.
n, q, k = 256, 3329, 3
eta_1, eta_2 = 2, 2
d_u, d_v = 10, 4

# Derived byte lengths from FIPS 203 Section 8 Table 3 and the K-PKE/ML-KEM algorithms.
ek_len = 384 * k + 32
dk_pke_len = 384 * k
dk_len = dk_pke_len + ek_len + 32 + 32
ct_len = 32 * (d_u * k + d_v)
ss_len = 32

# NIST ACVP test case ML-KEM-768 tcId = 26 seeds.
d_hex = "A2B4BCA315A6EA4600B4A316E09A2578AA1E8BCE919C8DF3A96C71C843F5B38B"
z_hex = "D6BF055CB7B375E3271ED131F1BA31F83FEF533A239878A71074578B891265D1"
d = bytes.fromhex(d_hex)
z = bytes.fromhex(z_hex)

# The K-PKE seed derivation: G(d || k) splits SHA3-512 into (rho, sigma).
rho_sigma = hashlib.sha3_512(d + bytes([k])).digest()
rho = rho_sigma[:32]
sigma = rho_sigma[32:]

print("ek_len =", ek_len)
print("dk_len =", dk_len)
print("ct_len =", ct_len)
print("ss_len =", ss_len)
print("rho[:8]   =", rho[:8].hex())
print("sigma[:8] =", sigma[:8].hex())
# ==> ek_len = 1184
# ==> dk_len = 2400
# ==> ct_len = 1088
# ==> ss_len = 32
# ==> rho[:8]   = e2212400769de8e1
# ==> sigma[:8] = ea2f872a82cc0c20
