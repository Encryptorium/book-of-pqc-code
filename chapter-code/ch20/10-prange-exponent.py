# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Cryptanalysis and ISD resistance"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/10-prange-exponent.py

from math import comb, log2

def prange_exponent(n, k, w):
    return log2(comb(n, w)) - log2(comb(n - k, w))

print(f"toy (n=16, k=8, t=2):  2^{prange_exponent(16, 8, 2):.1f}")
print(f"mceliece348864:        2^{prange_exponent(3488, 2720, 64):.1f}")
print(f"brute-force C(16,2) = {comb(16, 2)}")
# ==> toy (n=16, k=8, t=2):  2^2.1
# ==> mceliece348864:        2^142.8
# ==> brute-force C(16,2) = 120
