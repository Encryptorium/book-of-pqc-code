# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 13: Lattice cryptanalysis
# Section: "The dual distinguisher"
# https://book.encryptorium.com/part-2-lattices/ch13-lattice-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch13/03-dual-advantage.py

import math


def dual_advantage(w_norm, sigma, q):
    """Kyber Round 3 submission, Section 5.1.3 distinguishing bound."""
    tau = (w_norm * sigma) / q
    return 4.0 * math.exp(-2.0 * math.pi * math.pi * tau * tau)


# At ML-KEM-768 parameters (sigma = 1) the bound depends only on the
# ratio of the dual vector norm to the modulus q = 3329. The bound is
# meaningful only when below 1; a much shorter vector saturates it.
print(f"w norm 1000: advantage <= {dual_advantage(1000, 1.0, 3329):.4f}")
# ==> w norm 1000: advantage <= 0.6738
print(f"w norm 1500: advantage <= {dual_advantage(1500, 1.0, 3329):.6f}")
# ==> w norm 1500: advantage <= 0.072708
print(f"w norm q = 3329: advantage <= {dual_advantage(3329, 1.0, 3329):.3e}")
# ==> w norm q = 3329: advantage <= 1.070e-08
