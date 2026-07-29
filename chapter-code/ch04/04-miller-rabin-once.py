# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 4: From classical to post-quantum
# Section: "Building textbook RSA"
# https://book.encryptorium.com/part-1-foundations/ch04-from-classical-to-post-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch04/04-miller-rabin-once.py

def miller_rabin_once(n, a):
    if n < 2:
        return False          # without this, n = 1 loops forever below
    if n % 2 == 0:
        return n == 2
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False

# 3184935163 is prime; 3184935164 is not; 1 is neither.
print(miller_rabin_once(3184935163, 2))
print(miller_rabin_once(3184935164, 2))
print(miller_rabin_once(1, 2))
# ==> True
# ==> False
# ==> False
