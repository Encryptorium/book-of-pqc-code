# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 13: Lattice cryptanalysis
# Section: "A core-SVP estimator in Python"
# https://book.encryptorium.com/part-2-lattices/ch13-lattice-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch13/04-delta-beta.py

import math


def delta_beta(beta):
    numerator = ((math.pi * beta) ** (1.0 / beta)) * beta
    return (numerator / (2.0 * math.pi * math.e)) ** (1.0 / (2.0 * (beta - 1)))


def primal_succeeds(beta, d, q, m, sigma):
    log_lhs = math.log(sigma * math.sqrt(beta))
    log_rhs = (2 * beta - d - 1) * math.log(delta_beta(beta)) + (m / d) * math.log(q)
    return log_lhs <= log_rhs


def core_svp_beta(k, n, q, sigma):
    for beta in range(50, 1200):
        for m in range(1, (k + 1) * n + 1):
            d = m + k * n + 1
            if primal_succeeds(beta, d, q, m, sigma):
                return beta
    raise AssertionError("no beta in range")


parameter_sets = [
    ("ML-KEM-512",  2, 256, 3329, 3),
    ("ML-KEM-768",  3, 256, 3329, 2),
    ("ML-KEM-1024", 4, 256, 3329, 2),
]

print(f"{'name':<12} {'beta':>5} {'classical':>10} {'quantum':>8}")
# ==> name          beta  classical  quantum
for name, k, n, q, eta_1 in parameter_sets:
    sigma = math.sqrt(eta_1 / 2.0)
    beta = core_svp_beta(k, n, q, sigma)
    print(f"{name:<12} {beta:>5} {int(0.292 * beta):>10} {int(0.265 * beta):>8}")
# ==> ML-KEM-512     406        118      107
# ==> ML-KEM-768     624        182      165
# ==> ML-KEM-1024    874        255      231
