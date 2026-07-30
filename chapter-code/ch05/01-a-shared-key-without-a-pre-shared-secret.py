# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 5: KEMs vs key agreement vs public-key encryption
# Section: "A shared key without a pre-shared secret"
# https://book.encryptorium.com/part-1-foundations/ch05-kem-vs-key-agreement-vs-pke/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch05/01-a-shared-key-without-a-pre-shared-secret.py

# Toy Diffie-Hellman in (Z/pZ)^* with p = 23 and g = 5.
# g is a primitive root mod 23, so ord(g) = phi(23) = 22.
p = 23
g = 5

# Alice picks a secret exponent and publishes A.
a = 6
A = pow(g, a, p)

# Bob picks a secret exponent and publishes B.
b = 15
B = pow(g, b, p)

# Each party computes the shared value from the other's public value.
alice_shared = pow(B, a, p)
bob_shared = pow(A, b, p)
print(A, B)
print(alice_shared == bob_shared, alice_shared)
# ==> 8 19
# ==> True 2
