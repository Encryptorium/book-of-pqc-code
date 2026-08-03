# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 6: Digital signatures reconsidered
# Section: "Nonce reuse recovers the key"
# https://book.encryptorium.com/part-1-foundations/ch06-digital-signatures-reconsidered/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch06/02-nonce-reuse-recovers-the-key.py

# Toy ECDSA nonce-reuse attack on the order-11 subgroup of (Z/23)^*.
# g = 4 has order 11 modulo 23 (check: 4 = 2^2, and (Z/23)^* has order 22).
# The attacker sees two signatures (r, s1) and (r, s2) under the same nonce k
# and recovers the private key d from the two signatures alone.
p = 23
N = 11
g = 4

# Confirm that g has order N in (Z/p)^*.
assert pow(g, N, p) == 1

# Signer's keypair.
d = 7
y = pow(g, d, p)  # y = g^d mod p is the public "point"

# Two signatures under the SAME nonce on different message hashes.
k = 6
z1 = 3
z2 = 5

R = pow(g, k, p)          # "scalar multiplication" kG in the subgroup
r = R % N
s1 = (pow(k, -1, N) * (z1 + r * d)) % N
s2 = (pow(k, -1, N) * (z2 + r * d)) % N

# Real ECDSA rejects r = 0 and the recovery needs s1 != s2.
assert r != 0
assert s1 != s2

# Attacker sees (r, s1, z1) and (r, s2, z2). Recover k, then d.
k_rec = ((z1 - z2) * pow(s1 - s2, -1, N)) % N
d_rec = ((s1 * k_rec - z1) * pow(r, -1, N)) % N

print(d, d_rec, d == d_rec)
# ==> 7 7 True
