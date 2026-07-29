# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 4: From classical to post-quantum
# Section: "What Shor does to this"
# https://book.encryptorium.com/part-1-foundations/ch04-from-classical-to-post-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch04/09-what-shor-does-to-this.py

from math import gcd

n = 323
a = 2
r = 72
x = pow(a, r // 2, n)
factor = gcd(x - 1, n)
factor2 = gcd(x + 1, n)
print(x, factor, factor2)
# ==> 305 19 17
