# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "Signatures as Fiat-Shamir with aborts"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/01-signatures-as-fiat-shamir-with-aborts.py

# A scalar model of z = y + c*s1, not ML-DSA: one coefficient, a challenge
# c of +1 or -1, a secret s with |s| <= 4, and the mask bound cut to 2**10
# so that every mask y can be listed rather than sampled.
gamma_1, eta = 2**10, 4
masks = range(-gamma_1 + 1, gamma_1 + 1)  # y uniform on (-gamma_1, gamma_1]

tops, accepted = [], set()
for s in range(-eta, eta + 1):
    pairs = [(c, y + c * s) for c in (-1, 1) for y in masks]
    tops.append(max(c * z for c, z in pairs) - gamma_1)
    kept = frozenset((c, z) for c, z in pairs if abs(z) < gamma_1 - eta)
    accepted.add(kept)

print("secrets s:", list(range(-eta, eta + 1)))
print("top of c*z, less gamma_1:", tops)
print("distinct accepted sets:", len(accepted))
print("pairs in it:", len(kept), "of", len(pairs))
# ==> secrets s: [-4, -3, -2, -1, 0, 1, 2, 3, 4]
# ==> top of c*z, less gamma_1: [-4, -3, -2, -1, 0, 1, 2, 3, 4]
# ==> distinct accepted sets: 1
# ==> pairs in it: 4078 of 4096
