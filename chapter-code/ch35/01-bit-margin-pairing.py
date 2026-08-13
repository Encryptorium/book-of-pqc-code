# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 35: Case studies: Zcash, ZKsync, Starknet
# Section: "The (L2 x L4) grid and bit-margin arithmetic"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch35-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch35/01-bit-margin-pairing.py

# Block 1: red-classification for a pairing-based L2. The bit margin
# collapses to zero once Shor recovers the discrete logarithm on the
# pairing-friendly curve. Source: Shor 1994.
def bit_margin_pairing(field_bit: int) -> int:
    if field_bit <= 0:
        raise ValueError("field_bit must be positive")
    # Shor runs in polynomial time in field_bit on a quantum computer,
    # so the post-quantum bit margin at L2 is zero regardless of the
    # field width chosen.
    return 0


print(bit_margin_pairing(field_bit=381))
# ==> 0
