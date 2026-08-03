# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 6: Digital signatures reconsidered
# Section: "A textbook forgery"
# https://book.encryptorium.com/part-1-foundations/ch06-digital-signatures-reconsidered/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch06/01-a-textbook-forgery.py

# Textbook RSA signing on the 64-bit modulus from Chapter 5.
# Raw modular exponentiation is a group homomorphism on (Z/nZ)^*:
# s1 * s2 = (m1 * m2)^d mod n, which verifies as a signature on (m1 * m2) mod n.
p = 3184935163
q = 3199286161
n = p * q
e = 65537
d = pow(e, -1, (p - 1) * (q - 1))

# Honest signer produces two legitimate signatures.
m1 = 0x1111222233334444
m2 = 0x5555666677778888
s1 = pow(m1, d, n)
s2 = pow(m2, d, n)

# Attacker sees (m1, s1) and (m2, s2) and multiplies them.
s_forged = (s1 * s2) % n
m_forged = (m1 * m2) % n

# The forged pair verifies under the textbook rule s^e == m mod n,
# and m_forged is a fresh message the signer never signed.
assert m_forged not in {m1, m2}
assert pow(s_forged, e, n) == m_forged
print(pow(s_forged, e, n) == m_forged)
# ==> True
