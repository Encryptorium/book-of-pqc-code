# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 13: Lattice cryptanalysis
# Section: "The primal embedding"
# https://book.encryptorium.com/part-2-lattices/ch13-lattice-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch13/02-delta-beta.py

import math


def delta_beta(beta):
    """Chen 2013 root-Hermite factor approximation."""
    numerator = ((math.pi * beta) ** (1.0 / beta)) * beta
    return (numerator / (2.0 * math.pi * math.e)) ** (1.0 / (2.0 * (beta - 1)))


def primal_succeeds(beta, d, q, m, sigma):
    """Kyber Round 3 submission equation 9."""
    log_lhs = math.log(sigma * math.sqrt(beta))
    log_rhs = (2 * beta - d - 1) * math.log(delta_beta(beta)) + (m / d) * math.log(q)
    return log_lhs <= log_rhs


# ML-KEM-768: k = 3, n = 256, q = 3329, eta_1 = 2, sigma = 1.
k, n, q, sigma = 3, 256, 3329, 1.0
# Try the attack at the published optimal number of samples m = 650 (d = 1419).
m = 650
d = m + k * n + 1
print(f"ML-KEM-768 lattice dimension d = {d}")
# ==> ML-KEM-768 lattice dimension d = 1419
print(f"primal succeeds at beta = 500 ? {primal_succeeds(500, d, q, m, sigma)}")
# ==> primal succeeds at beta = 500 ? False
print(f"primal succeeds at beta = 700 ? {primal_succeeds(700, d, q, m, sigma)}")
# ==> primal succeeds at beta = 700 ? True
