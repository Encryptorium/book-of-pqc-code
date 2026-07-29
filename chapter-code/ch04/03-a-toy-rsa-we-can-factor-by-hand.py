# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 4: From classical to post-quantum
# Section: "A toy RSA we can factor by hand"
# https://book.encryptorium.com/part-1-foundations/ch04-from-classical-to-post-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch04/03-a-toy-rsa-we-can-factor-by-hand.py

p = 3184935163
q = 3199286161
n = p * q
e = 65537
d = pow(e, -1, (p - 1) * (q - 1))
m = 0xDEADBEEF
c = pow(m, e, n)
back = pow(c, d, n)
print(c)
print(hex(back))
# ==> 2094384833718895087
# ==> 0xdeadbeef
