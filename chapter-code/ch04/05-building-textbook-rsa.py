# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 4: From classical to post-quantum
# Section: "Building textbook RSA"
# https://book.encryptorium.com/part-1-foundations/ch04-from-classical-to-post-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch04/05-building-textbook-rsa.py

p = 3184935163
q = 3199286161
n = p * q
e = 65537
phi = (p - 1) * (q - 1)
# If 65537 divides phi, retry with new primes. For these two it does not.
assert phi % e != 0
d = pow(e, -1, phi)
public_key = (n, e)
private_key = (n, d)
print(public_key[0].bit_length(), "bit modulus")
print("public exponent", public_key[1])
# ==> 64 bit modulus
# ==> public exponent 65537
