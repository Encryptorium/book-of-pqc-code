# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 5: KEMs vs key agreement vs public-key encryption
# Section: "Correct is not secure"
# https://book.encryptorium.com/part-1-foundations/ch05-kem-vs-key-agreement-vs-pke/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch05/03-enc.py

# Toy ElGamal: Diffie-Hellman used to encrypt.
# p = 2063 = 2 * 1031 + 1, and g = 4 generates the subgroup of squares,
# which has prime order q = 1031. Messages are squares mod p, so 9 qualifies.
import random

p, q, g = 2063, 1031, 4
rng = random.Random(5)  # fixed seed for a reproducible page; keys come from secrets

x = rng.randrange(1, q)  # Bob's private key
h = pow(g, x, p)         # Bob's public key, a Diffie-Hellman share

def enc(h, m, r):
    # Alice's fresh share g^r, and m masked by the shared value h^r.
    return (pow(g, r, p), m * pow(h, r, p) % p)

def dec(x, c):
    c1, c2 = c
    shared = pow(c1, x, p)              # Bob recomputes h^r as c1^x
    return c2 * pow(shared, -1, p) % p

m = 9
c_first = enc(h, m, rng.randrange(1, q))
c_second = enc(h, m, rng.randrange(1, q))
print(c_first, c_second, dec(x, c_first) == dec(x, c_second) == m)

# The attacker holds a ciphertext c it cannot read, and can get any OTHER
# ciphertext decrypted. It multiplies the hidden message by 4 and asks.
c = enc(h, m, rng.randrange(1, q))
c_mauled = (c[0], c[1] * 4 % p)
reply = dec(x, c_mauled)                # one decryption of a different ciphertext
print(c_mauled != c, reply * pow(4, -1, p) % p == m)
# ==> (1664, 1910) (1803, 412) True
# ==> True True
