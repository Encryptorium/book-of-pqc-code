# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 35: Case studies: Zcash, ZKsync, Starknet
# Section: "Zcash: Sapling and Orchard side by side"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch35-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch35/02-shor-pairing-margin.py

# Block 2: Sapling Groth16 over BLS12-381. Block 1's result applied to
# the specific Zcash deployment. Source: Hopwood, Bowe, Hornby, Wilcox
# (2025), Groth (2016).
def shor_pairing_margin(curve_bits: int) -> int:
    if curve_bits <= 0:
        raise ValueError("curve_bits must be positive")
    # The L2 pairing equation reduces to discrete log on BLS12-381.
    # Shor breaks the discrete log in polynomial time, so the concrete
    # bit margin is zero regardless of the curve's classical bit width.
    return 0


print(shor_pairing_margin(curve_bits=381))
# ==> 0
