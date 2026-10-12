# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 5: KEMs vs key agreement vs public-key encryption
# Section: "The Fujisaki-Okamoto transform: from PKE component to CCA-secure KEM"
# https://book.encryptorium.com/part-1-foundations/ch05-kem-vs-key-agreement-vs-pke/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch05/04-enc.py

# The same toy ElGamal, put through the Fujisaki-Okamoto pattern.
import hashlib
import random

p, q, g = 2063, 1031, 4
rng = random.Random(5)  # fixed seed for a reproducible page; keys come from secrets

x = rng.randrange(1, q)  # Bob's private key
h = pow(g, x, p)         # Bob's public key
z = pow(g, rng.randrange(q), p)  # Bob's rejection seed, a secret group element

def enc(h, m, r):
    return (pow(g, r, p), m * pow(h, r, p) % p)

def dec(x, c):
    c1, c2 = c
    return c2 * pow(pow(c1, x, p), -1, p) % p

def hash_to_int(tag, *parts):
    data = tag.encode() + b"|" + b"|".join(str(v).encode() for v in parts)
    return int.from_bytes(hashlib.sha256(data).digest(), "big")

def G(m):          # coins derived from the message
    return hash_to_int("G", m) % q

def H(*parts):     # the shared key, truncated to 32 bits for the page
    return hash_to_int("H", *parts) % 2**32

def encap(h):
    m = pow(g, rng.randrange(q), p)     # a random message, never sent in clear
    c = enc(h, m, G(m))                 # coins come from G(m), not from rng
    return c, H(m, c)

# No input checks: decap expects two subgroup elements, and c1 = 0 raises.
def decap(x, z, h, c):
    m_prime = dec(x, c)
    if enc(h, m_prime, G(m_prime)) == c:   # re-encrypt and compare
        return H(m_prime, c)
    return H(z, c)                          # implicit rejection

c, K = encap(h)
print(decap(x, z, h, c) == K)

# The mauling from before. Decryption gives 4m, but the coins G(4m) do not
# reproduce the first component, so the comparison fails.
c_mauled = (c[0], c[1] * 4 % p)
m_prime = dec(x, c_mauled)
print(enc(h, m_prime, G(m_prime)) == c_mauled)

# What the attacker receives: a value fixed by (z, c_mauled), not by K.
k1 = decap(x, z, h, c_mauled)
k2 = decap(x, z, h, c_mauled)
k3 = decap(x, z, h, (c[0], c[1] * 9 % p))
print(k1 == k2, k1 != K, k1 != k3)
# ==> True
# ==> False
# ==> True True True
