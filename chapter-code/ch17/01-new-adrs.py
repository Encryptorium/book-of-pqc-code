# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 17: SLH-DSA (FIPS 205) from scratch
# Section: "SLH-DSA at toy parameters"
# https://book.encryptorium.com/part-3-hash-based/ch17-slh-dsa-fips-205/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch17/01-new-adrs.py

import hashlib, struct

# --- Toy parameters (NOT FIPS 205) ---
n = 16       # hash output bytes
h, d = 9, 3  # total height, layers -> hp = 3
hp = h // d  # subtree height
a, k = 3, 3  # FORS: t = 2^a = 8 leaves, k trees
w = 16       # Winternitz parameter

# --- ADRS (32-byte mutable address) ---
def new_adrs():
    return bytearray(32)

def set_layer(ad, v):
    struct.pack_into(">I", ad, 0, v)

def set_tree(ad, v):
    ad[4:16] = v.to_bytes(12, "big")

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

def set_height(ad, v):
    struct.pack_into(">I", ad, 24, v)

def set_idx(ad, v):
    struct.pack_into(">I", ad, 28, v)

def compress(ad):
    return bytes([ad[3]]) + bytes(ad[8:16]) + bytes([ad[19]]) + bytes(ad[20:32])

# --- Tweakable hashes (SHA-256 for n=16) ---
def tw_F(pk_s, ad, m):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + m).digest()[:n]

def tw_H(pk_s, ad, m1, m2):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + m1 + m2).digest()[:n]

def tw_T(pk_s, ad, m):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + m).digest()[:n]

def tw_PRF(pk_s, sk_s, ad):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + sk_s).digest()[:n]

# --- Keygen: compute top XMSS tree root ---
import math
lg_w = int(math.log2(w))
ell_1 = math.ceil(8 * n / lg_w)
mc = ell_1 * (w - 1)
ell_2 = math.ceil((math.floor(math.log2(mc)) + 1) / lg_w)
ell = ell_1 + ell_2

sk_seed = bytes.fromhex("a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")
sk_prf  = bytes.fromhex("01020304050607080910111213141516")
pk_seed = bytes.fromhex("f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6")

def wots_pk(sk_s, pk_s, ad):
    """Compressed WOTS+ public key (n bytes)."""
    kp = get_kp(ad)
    sk_ad = bytearray(ad); set_type_clear(sk_ad, 5); set_kp(sk_ad, kp)
    w_ad = bytearray(ad); set_type_clear(w_ad, 0); set_kp(w_ad, kp)
    tmp = b""
    for i in range(ell):
        set_chain(sk_ad, i)
        val = tw_PRF(pk_s, sk_s, sk_ad)
        set_chain(w_ad, i)
        for j in range(w - 1):
            set_hash_addr(w_ad, j)
            val = tw_F(pk_s, w_ad, val)
        tmp += val
    pk_ad = bytearray(ad); set_type_clear(pk_ad, 1); set_kp(pk_ad, kp)
    return tw_T(pk_s, pk_ad, tmp)

def xmss_node(sk_s, i, z, pk_s, ad):
    if z == 0:
        set_type_clear(ad, 0); set_kp(ad, i)
        return wots_pk(sk_s, pk_s, ad)
    left = xmss_node(sk_s, 2*i, z-1, pk_s, bytearray(ad))
    right = xmss_node(sk_s, 2*i+1, z-1, pk_s, bytearray(ad))
    set_type_clear(ad, 2); set_height(ad, z); set_idx(ad, i)
    return tw_H(pk_s, ad, left, right)

ad = new_adrs(); set_layer(ad, d - 1)
pk_root = xmss_node(sk_seed, 0, hp, pk_seed, ad)
pk = pk_seed + pk_root
print(f"Public key: {pk.hex()[:32]}... ({len(pk)} bytes)")
# ==> Public key: f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6... (32 bytes)
