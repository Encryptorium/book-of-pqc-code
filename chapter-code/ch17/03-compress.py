# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 17: SLH-DSA (FIPS 205) from scratch
# Section: "WOTS+ with ADRS"
# https://book.encryptorium.com/part-3-hash-based/ch17-slh-dsa-fips-205/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch17/03-compress.py

import hashlib, struct, math

n, w = 16, 16
lg_w = int(math.log2(w))
ell_1 = math.ceil(8 * n / lg_w)
mc = ell_1 * (w - 1)
ell_2 = math.ceil((math.floor(math.log2(mc)) + 1) / lg_w)
ell = ell_1 + ell_2

def compress(ad):
    return bytes([ad[3]]) + bytes(ad[8:16]) + bytes([ad[19]]) + bytes(ad[20:32])

def tw_F(pk_s, ad, m):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + m).digest()[:n]

def tw_T(pk_s, ad, m):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + m).digest()[:n]

def tw_PRF(pk_s, sk_s, ad):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + sk_s).digest()[:n]

def set_type_clear(ad, v):
    struct.pack_into(">I", ad, 16, v)
    ad[20:32] = b"\x00" * 12

def set_kp(ad, v):
    struct.pack_into(">I", ad, 20, v)

def get_kp(ad):
    return struct.unpack_from(">I", ad, 20)[0]

def set_chain(ad, v):
    struct.pack_into(">I", ad, 24, v)

def set_hash_addr(ad, v):
    struct.pack_into(">I", ad, 28, v)

pk_seed = bytes.fromhex("f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6")
sk_seed = bytes.fromhex("a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")

ad = bytearray(32)
set_kp(ad, 0)

# Generate one WOTS+ secret and chain it to the endpoint
sk_ad = bytearray(ad); set_type_clear(sk_ad, 5); set_kp(sk_ad, 0)
set_chain(sk_ad, 0)
secret = tw_PRF(pk_seed, sk_seed, sk_ad)

w_ad = bytearray(ad); set_type_clear(w_ad, 0); set_kp(w_ad, 0)
set_chain(w_ad, 0)
val = secret
for j in range(w - 1):
    set_hash_addr(w_ad, j)
    val = tw_F(pk_seed, w_ad, val)

print(f"WOTS+ chain 0: secret {secret.hex()[:16]}... -> endpoint {val.hex()[:16]}...")
print(f"Chain length: {w - 1} F calls, ell = {ell} chains, sig = {ell * n} bytes")
# ==> WOTS+ chain 0: secret 36c81ce3666e22c6... -> endpoint 19f71540b3d7e140...
# ==> Chain length: 15 F calls, ell = 35 chains, sig = 560 bytes
