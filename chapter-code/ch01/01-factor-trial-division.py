# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 1: The quantum threat
# Section: "Classical factoring, to calibrate the threat"
# https://book.encryptorium.com/part-1-foundations/ch01-the-quantum-threat/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch01/01-factor-trial-division.py

def factor_trial_division(n: int) -> tuple[int, int] | None:
    """Return (p, q) with p * q == n if n is composite, else None.

    Trial division up to sqrt(n) is correct for any composite, since every
    composite has a prime factor at most sqrt(n). It is just catastrophically
    slow for moduli the size of any real RSA key.
    """
    candidate = 2
    while candidate * candidate <= n:
        if n % candidate == 0:
            return candidate, n // candidate
        candidate += 1
    return None


toy_modulus = 3233  # the secret factors are 53 and 61
result = factor_trial_division(toy_modulus)
assert result is not None
p, q = result
print(f"{toy_modulus} = {p} x {q}")
# ==> 3233 = 53 x 61
