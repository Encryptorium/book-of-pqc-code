# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 35: Case studies: Zcash, ZKsync, Starknet
# Section: "Starknet: legacy ethSTARK and current Stwo"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch35-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch35/05-query-miss-bits.py

# Block 5: Stwo's published defaults, read at all three decoding
# radii. A blowup of 2^log_blowup gives rate rho; each of the
# n_queries FRI query paths misses a delta_0-far codeword with
# probability at most (1 - delta_0), and grinding adds pow_bits on
# top. Source: starkware-libs/stwo-cairo README (the defaults);
# Ch 34 Section 5.1 (the three radii); Ben-Sasson, Carmon, Ishai,
# Kopparty, Saraf (2020); Crites and Stewart (2025).
import math


def query_miss_bits(n_queries: int, pow_bits: int, log_blowup: int,
                    regime: str) -> float:
    if min(n_queries, log_blowup) <= 0 or pow_bits < 0:
        raise ValueError("n_queries, log_blowup positive; pow_bits"
                         " non-negative")
    rho = 2.0 ** (-log_blowup)
    if regime == "capacity":
        delta_0 = 1.0 - rho
    elif regime == "johnson":
        delta_0 = 1.0 - math.sqrt(rho)
    elif regime == "unique":
        delta_0 = (1.0 - rho) / 2.0
    else:
        raise ValueError(f"unknown regime: {regime!r}")
    return round(-n_queries * math.log2(1.0 - delta_0) + pow_bits, 1)


stwo = {"n_queries": 70, "pow_bits": 26, "log_blowup": 1}
print(query_miss_bits(**stwo, regime="capacity"),
      query_miss_bits(**stwo, regime="johnson"),
      query_miss_bits(**stwo, regime="unique"))
# ==> 96.0 61.0 55.1
