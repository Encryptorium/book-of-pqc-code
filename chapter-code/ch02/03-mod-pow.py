# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 2: Mathematical preliminaries
# Section: "Modular exponentiation"
# https://book.encryptorium.com/part-1-foundations/ch02-mathematical-preliminaries/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch02/03-mod-pow.py

def mod_pow(base, exponent, modulus):
    assert exponent >= 0, "exponent must be non-negative"
    assert modulus >= 1, "modulus must be at least 1"
    result = 1 % modulus
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result

# 7^200 mod 13, matching the opening calculation.
print(mod_pow(7, 200, 13))
# ==> 3
