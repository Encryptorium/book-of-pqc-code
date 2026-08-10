# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "Verify: recomputing the commitment through UseHint"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/08-verify-recomputing-the-commitment-through-usehint.py

import sys

sys.path.insert(0, "solutions/ch12-mldsa/src")
from mldsa.params import ML_DSA_65
from mldsa.ml_dsa import (
    ml_dsa_keygen_internal,
    ml_dsa_sign_internal,
    ml_dsa_verify_internal,
)

# The from-scratch package assembles the primitives above into the three
# operations. KeyGen expands a 32-byte seed; Sign runs the abort loop; Verify
# recomputes the commitment through UseHint. These are the internal (explicit
# seed and rnd) variants the ACVP vectors drive.
xi = bytes.fromhex(
    "A991FD42B071D49C48AE3E75C647459E0DAAD1E1BA356A04801912D3294BCFF8"
)
pk, sk = ml_dsa_keygen_internal(ML_DSA_65, xi)

# M' is the internal message: 0x00 || len(ctx) || ctx || message, empty context.
m_prime = bytes([0, 0]) + b"the abort loop terminates"
sigma = ml_dsa_sign_internal(ML_DSA_65, sk, m_prime, bytes(32))

good = ml_dsa_verify_internal(ML_DSA_65, pk, m_prime, sigma)
tampered = bytes([sigma[0] ^ 0x01]) + sigma[1:]
bad = ml_dsa_verify_internal(ML_DSA_65, pk, m_prime, tampered)

print("pk, sk, sig lengths =", (len(pk), len(sk), len(sigma)))
print("honest signature verifies =", good)
print("tampered signature verifies =", bad)
# ==> pk, sk, sig lengths = (1952, 4032, 3309)
# ==> honest signature verifies = True
# ==> tampered signature verifies = False
