# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 13: Lattice cryptanalysis
# Section: "The same estimator against ML-DSA"
# https://book.encryptorium.com/part-2-lattices/ch13-lattice-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch13/06-delta-beta.py

import math


def delta_beta(beta):
    numerator = ((math.pi * beta) ** (1.0 / beta)) * beta
    return (numerator / (2.0 * math.pi * math.e)) ** (1.0 / (2.0 * (beta - 1)))


def primal_succeeds(beta, d, q, m, sigma):
    log_lhs = math.log(sigma * math.sqrt(beta))
    log_rhs = (2 * beta - d - 1) * math.log(delta_beta(beta)) + (m / d) * math.log(q)
    return log_lhs <= log_rhs


def mldsa_beta(k, ell, n, q, eta):
    # The unknowns are s_1, which is ell ring elements. The samples are
    # the k rows of t = A s_1 + s_2. A coefficient uniform on
    # [-eta, eta] has variance eta (eta + 1) / 3.
    sigma = math.sqrt(eta * (eta + 1) / 3.0)
    for beta in range(50, 1200):
        for m in range(1, k * n + 1):
            if primal_succeeds(beta, m + ell * n + 1, q, m, sigma):
                return beta
    raise AssertionError("no beta in range")


# ML-DSA parameter sets from FIPS 204 Table 1; q = 2**23 - 2**13 + 1.
q_dsa = 8380417
parameter_sets = [
    ("ML-DSA-44", 4, 4, 2, 2),
    ("ML-DSA-65", 6, 5, 4, 3),
    ("ML-DSA-87", 8, 7, 2, 5),
]

print(f"{'name':<11} {'beta':>5} {'classical':>10} {'quantum':>8} {'cat':>4}")
# ==> name         beta  classical  quantum  cat
for name, k, ell, eta, cat in parameter_sets:
    beta = mldsa_beta(k, ell, 256, q_dsa, eta)
    print(f"{name:<11} {beta:>5} {int(0.292 * beta):>10} {int(0.265 * beta):>8} {cat:>4}")
# ==> ML-DSA-44     424        123      112    2
# ==> ML-DSA-65     624        182      165    3
# ==> ML-DSA-87     863        251      228    5
