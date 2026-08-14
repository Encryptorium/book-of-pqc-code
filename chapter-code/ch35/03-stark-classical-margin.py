# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 35: Case studies: Zcash, ZKsync, Starknet
# Section: "ZKsync Era: composite architecture"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch35-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch35/03-stark-classical-margin.py

# Block 3: Boojum inner FRI-STARK classical-ROM margin via the Ch 34
# Section 5.5 composed-soundness formula. The proximity threshold
# delta_0 = 1 - sqrt(rho) is the Johnson / Guruswami-Sudan
# list-decoding radius, which is exactly where BCIKS Theorem 1.2
# proves the proximity gap; Ch 34 Section 5.1 sets out the three
# radii and works at this one throughout for that reason. A pipeline
# that sets delta_0 above it is in the conjectured regime, which is
# the discount Ch 34's closing aside records as having fallen in late
# 2025. The DFMS20 parameter-bump check from Ch 33's multi-round
# subsection then asks whether the deployed challenge-space width
# absorbs the QROM loss at a target PQ margin. Exact Boojum
# parameters are not published at the granularity below; values are
# illustrative of a Goldilocks extension-field configuration.
# Source: Ch 34 Sections 5.1 and 5.5; Ch 33 'Multi-round
# Fiat-Shamir'; Ben-Sasson, Carmon, Ishai, Kopparty, Saraf (2020,
# proximity gap at the Johnson bound); ZKsync (2023); Block et al.
# (2023, classical NI/ROM bound; the same paper's QROM
# bound is one factor of q heavier).
import math


def stark_classical_margin(field_bits: int, L: int, N: int, mu: int,
                           r_FRI: int, grinding: int) -> float:
    if min(field_bits, L, N, mu, r_FRI) <= 0:
        raise ValueError("field_bits, L, N, mu, r_FRI must be positive")
    if grinding < 0:
        raise ValueError("grinding must be non-negative")
    if L >= N:
        raise ValueError("L must be less than N")
    rho = L / N
    # Johnson / Guruswami-Sudan radius, where BCIKS Theorem 1.2
    # proves the proximity gap.
    delta_0 = 1.0 - math.sqrt(rho)
    log_bad_beta = math.log2(r_FRI * (N + 1)) - field_bits
    log_per_round = mu * math.log2(1.0 - delta_0)
    log_consistency = mu * math.log2((L - 1) / N)
    # Ch 34 Section 5.5: grinding attenuates the query-miss terms only.
    # A forger who wins on a bad fold challenge never re-grinds.
    composed_prob = (2.0 ** log_bad_beta
                     + 2.0 ** -grinding * (2.0 ** log_per_round
                                           + 2.0 ** log_consistency))
    return round(-math.log2(composed_prob), 1)


def dfms20_required_cbits(k_target: int, q_bits: int, r_FS: int) -> int:
    if k_target <= 0 or r_FS <= 0 or q_bits < 0:
        raise ValueError("k_target, r_FS must be positive; q_bits non-negative")
    # The exact form is c_bits >= 2 log2(2 q + 1) + k / r_FS per
    # Ch 33's quantum-oracle-cost section; the approximation
    # c_bits >= 2 q_bits + k / r_FS drops
    # the log2(2 q + 1) approximate q_bits + 1 correction and under-
    # estimates by roughly 2 bits per round.
    return 2 * q_bits + math.ceil(k_target / r_FS)


# Illustrative Boojum inner.
k_classical_boojum = stark_classical_margin(field_bits=128, L=2 ** 16,
                                            N=2 ** 20, mu=40, r_FRI=16,
                                            grinding=20)
c_bits_required = dfms20_required_cbits(k_target=128, q_bits=80, r_FS=6)
print(k_classical_boojum, c_bits_required)
# ==> 99.9 182
