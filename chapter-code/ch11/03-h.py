# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "Hash primitives: H, G, PRF, XOF, J"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/03-h.py

import hashlib


def H(data):
    return hashlib.sha3_256(data).digest()


def G(data):
    digest = hashlib.sha3_512(data).digest()
    return digest[:32], digest[32:]


def PRF(eta, seed, nonce):
    assert eta in (2, 3)
    shake = hashlib.shake_256()
    shake.update(seed + bytes([nonce]))
    return shake.digest(64 * eta)


def XOF(shake_input, outlen):
    shake = hashlib.shake_128()
    shake.update(shake_input)
    return shake.digest(outlen)


def J(data):
    return hashlib.shake_256(data).digest(32)


# A sanity check: G applied to the empty byte string is SHA3-512 of
# the empty byte string split into two 32-byte halves. Compare the
# concatenation against the canonical FIPS 202 digest.
k_half, r_half = G(b"")
full = k_half + r_half
expected = bytes.fromhex(
    "a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a6"
    "15b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26"
)
print("H len =", len(H(b"abc")))
print("PRF(2) len =", len(PRF(2, b"\x00" * 32, 0)))
print("J len =", len(J(b"")))
print("G matches SHA3-512 on empty input =", full == expected)
# ==> H len = 32
# ==> PRF(2) len = 128
# ==> J len = 32
# ==> G matches SHA3-512 on empty input = True
