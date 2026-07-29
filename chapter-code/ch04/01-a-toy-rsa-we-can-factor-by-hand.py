# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 4: From classical to post-quantum
# Section: "A toy RSA we can factor by hand"
# https://book.encryptorium.com/part-1-foundations/ch04-from-classical-to-post-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch04/01-a-toy-rsa-we-can-factor-by-hand.py

# In the full package this is classical.rsa.keygen. Called as
# keygen(bits=64, rng=random.Random(42)) it uses Miller-Rabin to
# generate these two distinct 32-bit primes. It returns the pair
# (public_key, private_key), with p and q stored on the private key.
p = 3184935163
q = 3199286161
n = p * q
print(n)
# ==> 10189518990668179243
