# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Field arithmetic"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/04-gf16-mul.py

def gf16_mul(a, b):
    """Multiply in GF(2^4) = GF(2)[x]/(x^4 + x + 1)."""
    result = 0
    for _ in range(4):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 16:
            a ^= 0b10011  # x^4 + x + 1 = 19
    return result

def gf16_inv(a):
    """Brute-force inverse in GF(16)."""
    for x in range(1, 16):
        if gf16_mul(a, x) == 1:
            return x

print(f"3 * 5 = {gf16_mul(3, 5)}")
print(f"inv(7) = {gf16_inv(7)}")
print(f"7 * inv(7) = {gf16_mul(7, gf16_inv(7))}")
# ==> 3 * 5 = 15
# ==> inv(7) = 6
# ==> 7 * inv(7) = 1
