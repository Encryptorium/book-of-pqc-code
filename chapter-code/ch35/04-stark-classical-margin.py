# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 35: Case studies: Zcash, ZKsync, Starknet
# Section: "Starknet: legacy ethSTARK and current Stwo"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch35-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch35/04-stark-classical-margin.py

# Block 4: illustrative ethSTARK-style classical-ROM margin at a
# reference-like parameter point (not a verified deployed Starknet
# parameter table), via the Ch 34 Section 5.5 composed-soundness
# formula at the Johnson-bound proximity radius (same regime note as
# Block 3). The DFMS20 parameter-bump check compares
# the F_{p^4} challenge-field width (~244 bits, recommended in
# ethSTARK Documentation v1.2 Section 5.10.2 for provable 128-bit
# IOP knowledge soundness) against the required challenge width at
# the 128-bit PQ target Ch 34 Section 5.7 uses as the headline
# production example. Source: Ch 34 Sections 5.1, 5.5 and 5.7;
# Ch 33 'Multi-round Fiat-Shamir' and 'Cost of the quantum oracle';
# Ben-Sasson, Bentov, Horesh, Riabzev (2018); Ben-Sasson (2021,
# ethSTARK documentation, §5.10.2); Block et al. (2023,
# classical NI/ROM bound; the same paper's QROM bound is
# one factor of q heavier).
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
    return 2 * q_bits + math.ceil(k_target / r_FS)


# Illustrative ethSTARK-style reference point at blowup 16, mu = 48,
# r_FRI = 20, grinding = 20. Not a verified deployed Starknet
# parameter table; see ethSTARK Documentation v1.2 Section 6 for the
# concrete (s = 79 / 105 / 141)-style settings. The challenge-field
# width 244 corresponds to F_{p^4} per ethSTARK Documentation v1.2
# Section 5.10.2 for provable 128-bit IOP knowledge soundness; the
# conjectured-soundness path uses F_{p^3} at 183 bits. The DFMS20
# bump target is k = 128 to match Ch 34 Section 5.7's headline
# production example.
k_classical_ethstark = stark_classical_margin(field_bits=244, L=2 ** 20,
                                              N=2 ** 24, mu=48, r_FRI=20,
                                              grinding=20)
c_bits_required_k128 = dfms20_required_cbits(k_target=128, q_bits=80,
                                             r_FS=6)
c_bits_deployed = 244
print(k_classical_ethstark, c_bits_required_k128, c_bits_deployed)
# ==> 116.0 182 244
