# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 5: KEMs vs key agreement vs public-key encryption
# Section: "The KEM API and a toy RSA-KEM"
# https://book.encryptorium.com/part-1-foundations/ch05-kem-vs-key-agreement-vs-pke/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch05/02-encap.py

# Toy RSA-KEM built on the 64-bit textbook RSA from Chapter 4.
# Encap samples a random K in [1, n - 1] and encrypts it as K^e mod n.
# Decap runs raw RSA decryption to recover the same K.
# Demo only: random.Random is deterministic and NOT cryptographically secure.
# Real encapsulation uses secrets.SystemRandom and feeds the output through
# a KDF to produce a fixed-length symmetric key.
import random

p = 3184935163
q = 3199286161
n = p * q
e = 65537
d = pow(e, -1, (p - 1) * (q - 1))
public_key = (n, e)
private_key = (n, d)

def encap(pk, rng):
    mod, exp = pk
    K = rng.randint(1, mod - 1)
    c = pow(K, exp, mod)
    return (c, K)

def decap(sk, c):
    mod, dec_exp = sk
    return pow(c, dec_exp, mod)

rng = random.Random(7)  # fixed seed for reproducibility
c, K_alice = encap(public_key, rng)
K_bob = decap(private_key, c)
print(K_alice == K_bob)
print(0 < K_bob < n)
# ==> True
# ==> True
