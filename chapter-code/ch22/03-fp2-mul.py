# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 22: Isogenies for programmers
# Section: "Why $\mathbb{F}_{p^2}$?"
# https://book.encryptorium.com/part-4-code-isogeny/ch22-isogenies-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch22/03-fp2-mul.py

p = 431

def fp2_mul(x, y, p):
    return ((x[0]*y[0] - x[1]*y[1]) % p,
            (x[0]*y[1] + x[1]*y[0]) % p)

def fp2_inv(x, p):
    norm = (x[0]*x[0] + x[1]*x[1]) % p
    inv_n = pow(norm, -1, p)
    return ((x[0]*inv_n) % p, ((-x[1])*inv_n) % p)

# Verify: i^2 = -1 in F_{431^2}.
i = (0, 1)
print(fp2_mul(i, i, p))
# ==> (430, 0)

# Verify: (3 + 5i)*(3 + 5i)^{-1} = 1.
z = (3, 5)
z_inv = fp2_inv(z, p)
print(fp2_mul(z, z_inv, p))
# ==> (1, 0)
