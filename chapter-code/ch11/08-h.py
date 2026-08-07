# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "The Fujisaki-Okamoto wrapper"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/08-h.py

import hashlib


def H(data):
    return hashlib.sha3_256(data).digest()


def G(data):
    digest = hashlib.sha3_512(data).digest()
    return digest[:32], digest[32:]


def J(data):
    return hashlib.shake_256(data).digest(32)


# Mock K-PKE: encryption prepends m to a deterministic tag derived
# from (ek, r); decryption reads m from the first 32 bytes. This is
# not the real Module-Regev construction — it exists only to exercise
# the FO wrapper's re-encryption check at the byte level. What
# matters for the mock: it round-trips on honest inputs and diverges
# when any byte of the ciphertext is flipped.
def mock_kpke_encrypt(ek, m, r):
    tag = hashlib.sha3_256(ek + r).digest()
    return m + tag


def mock_kpke_decrypt(dk_pke, c):
    return c[:32]


ek = b"public key bytes".ljust(32, b"\x00")
m = b"message_of_exactly_32_bytes_okay"
z = b"implicit_rejection_seed_32_bytes"
dk_pke = b"stub dk_pke, unused by the mock" + b"\x00"

# Encapsulate.
K, r = G(m + H(ek))
c = mock_kpke_encrypt(ek, m, r)

# Decapsulate: recover m', recompute (K', r'), re-encrypt, compare.
m_prime = mock_kpke_decrypt(dk_pke, c)
K_prime, r_prime = G(m_prime + H(ek))
c_prime = mock_kpke_encrypt(ek, m_prime, r_prime)
if c == c_prime:
    K_out = K_prime
else:
    K_out = J(z + c)

# Honest path: K matches K_prime.
print("honest decapsulation matches encapsulation K =", K_out == K)

# Tampered path: flip a byte of c and observe the rejection branch.
c_tampered = bytes([c[0] ^ 0xFF]) + c[1:]
m_prime_bad = mock_kpke_decrypt(dk_pke, c_tampered)
K_prime_bad, r_prime_bad = G(m_prime_bad + H(ek))
c_reenc = mock_kpke_encrypt(ek, m_prime_bad, r_prime_bad)
if c_tampered == c_reenc:
    K_bad = K_prime_bad
else:
    K_bad = J(z + c_tampered)
print("tampered decapsulation returns J(z || c) =",
      K_bad == J(z + c_tampered))
print("tampered K != honest K =", K_bad != K)
# ==> honest decapsulation matches encapsulation K = True
# ==> tampered decapsulation returns J(z || c) = True
# ==> tampered K != honest K = True
