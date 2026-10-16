# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 27: Hybrid schemes in practice
# Section: "Cryptanalysis and known attacks"
# https://book.encryptorium.com/part-5-migration-deployment/ch27-hybrid-schemes-in-practice/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch27/04-x25519.py

# Block 4: two X25519 shares, one shared secret, one combiner key. Stdlib only.
import hashlib, hmac, os

P = 2**255 - 19

def x25519(k, u):
    # RFC 7748 Section 5: clamp the scalar, mask bit 255, run the ladder.
    # The swap below branches on secret bits, so this is not constant-time.
    k = bytearray(k)
    k[0] &= 248
    k[31] = (k[31] & 127) | 64
    k = int.from_bytes(k, "little")
    x1 = int.from_bytes(u, "little") & ((1 << 255) - 1)
    x2, z2, x3, z3, swap = 1, 0, x1, 1, 0
    for t in reversed(range(255)):
        bit = (k >> t) & 1
        if swap ^ bit:
            x2, x3, z2, z3 = x3, x2, z3, z2
        swap = bit
        a, b, c, d = x2 + z2, x2 - z2, x3 + z3, x3 - z3
        aa, bb, da, cb = a * a % P, b * b % P, d * a % P, c * b % P
        e = aa - bb
        x3, z3 = (da + cb) ** 2 % P, x1 * (da - cb) ** 2 % P
        x2, z2 = aa * bb % P, e * (aa + 121665 * e) % P
    if swap:
        x2, z2 = x3, z3
    return (x2 * pow(z2, P - 2, P) % P).to_bytes(32, "little")

def hkdf_sha256(ikm, info, length=32):
    # Block 1's derivation: the two secrets go in, the ciphertexts do not.
    prk = hmac.new(b"\x00" * 32, ikm, hashlib.sha256).digest()
    out, t, counter = b"", b"", 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        out += t
        counter += 1
    return out[:length]

# RFC 7748 Section 6.1: Alice's private key, and Bob's public key, which
# plays the X25519 half of the ciphertext sent to Alice.
alice_sk = bytes.fromhex("77076d0a7318a57d3c16c17251b26645"
                         "df4c2f87ebc0992ab177fba51db92c2a")
share = bytes.fromhex("de9edb7d7b7dc1b4d35b61c2ece43537"
                      "3f8343c85b78674dadfc7e146f882b4f")

# The adversary sees only the ciphertext. Inverting the share's
# u-coordinate modulo p takes no key.
twin = pow(int.from_bytes(share, "little"), P - 2, P).to_bytes(32, "little")

# Alice decapsulates both. The ML-KEM half is unchanged, so its secret
# is the same both times.
ss_mlkem = os.urandom(32)
label = b"tls13 x25519_mlkem768"
k_share = hkdf_sha256(ss_mlkem + x25519(alice_sk, share), label)
k_twin = hkdf_sha256(ss_mlkem + x25519(alice_sk, twin), label)
print(twin != share, x25519(alice_sk, twin).hex()[:16], k_share == k_twin)
# ==> True 4a5d9d5ba4ce2de1 True
