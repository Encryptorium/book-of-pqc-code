# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "Prange information-set decoding"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/06-prange-exponent.py

import math

def prange_exponent(n, k, w):
    """Log2 of expected Prange iterations: C(n,k) / C(n-w,k)."""
    log_cost = (
        sum(math.log2(n - i) for i in range(k))
        - sum(math.log2(n - w - i) for i in range(k))
    )
    return log_cost

# Hamming [7,4,3] with w=1.
exp_hamming = prange_exponent(7, 4, 1)
print(f"[7,4,3] w=1: 2^{exp_hamming:.1f} iterations")
# ==> [7,4,3] w=1: 2^1.2 iterations

# Classic McEliece mceliece348864: n=3488, k=2720, w=64.
exp_mce = prange_exponent(3488, 2720, 64)
print(f"mceliece348864: 2^{exp_mce:.1f} iterations")
# ==> mceliece348864: 2^142.8 iterations

# Classic McEliece mceliece6960119: n=6960, k=5413, w=119.
exp_mce2 = prange_exponent(6960, 5413, 119)
print(f"mceliece6960119: 2^{exp_mce2:.1f} iterations")
# ==> mceliece6960119: 2^263.4 iterations
