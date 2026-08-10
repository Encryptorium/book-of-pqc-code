# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "A concrete ML-DSA-65 parameter and seed derivation"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/01-a-concrete-ml-dsa-65-parameter-and-seed-derivation.py

import hashlib

# ML-DSA-65 parameters (FIPS 204 Table 1; n is the ring degree, from Section 2.4.1).
n, q, d = 256, 8380417, 13
k, l, eta = 6, 5, 4
gamma_1, omega, lam = 1 << 19, 55, 192

# Bit widths that drive the packed lengths (FIPS 204 Section 7.2 encoders).
t1_bits = (q - 1).bit_length() - d            # 23 - 13 = 10
eta_bits = (2 * eta).bit_length()             # bitlen(8) = 4
gamma1_bits = (2 * gamma_1 - 1).bit_length()  # 20

# Derived byte lengths (FIPS 204 Table 2), computed rather than hard-coded.
c_tilde_len = lam // 4
pk_len = 32 + 32 * t1_bits * k
sk_len = 32 + 32 + 64 + 32 * eta_bits * (k + l) + 32 * d * k
sig_len = c_tilde_len + 32 * gamma1_bits * l + omega + k

# NIST ACVP ML-DSA-65 keyGen test case tcId = 26 seed.
xi = bytes.fromhex(
    "A991FD42B071D49C48AE3E75C647459E0DAAD1E1BA356A04801912D3294BCFF8"
)

# The KeyGen seed expansion: H(xi || k || l) split into (rho, rho', K).
raw = hashlib.shake_256(xi + bytes([k]) + bytes([l])).digest(128)
rho, rho_prime, K = raw[:32], raw[32:96], raw[96:128]

print("pk_len =", pk_len)
print("sk_len =", sk_len)
print("sig_len =", sig_len)
print("c_tilde_len =", c_tilde_len)
print("rho[:8]  =", rho[:8].hex())
print("rho'[:8] =", rho_prime[:8].hex())
print("K[:8]    =", K[:8].hex())
# ==> pk_len = 1952
# ==> sk_len = 4032
# ==> sig_len = 3309
# ==> c_tilde_len = 48
# ==> rho[:8]  = 36db0b5dce98bd19
# ==> rho'[:8] = 3a443ee0b259e6e5
# ==> K[:8]    = 33824e8fa472bead
