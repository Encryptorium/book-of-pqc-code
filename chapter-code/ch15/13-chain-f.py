# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "Leaf reuse"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/13-chain-f.py

import hashlib

def chain_f(x, start, steps, pk_seed, addr, n=4):
    value = x
    for i in range(start, start + steps):
        value = hashlib.sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        ).digest()[:n]
    return value

def base_w(data, w, out_len):
    lg_w = w.bit_length() - 1
    digits = []
    for byte in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]

# The toy from the start of the chapter: w = 4 and n = 4 bytes.
w, n = 4, 4
lg_w = w.bit_length() - 1
ell_1 = (8 * n + lg_w - 1) // lg_w                # 16 message digits
max_c = ell_1 * (w - 1)
ell_2 = (max_c.bit_length() + lg_w - 1) // lg_w   # 3 checksum digits

def csum_digits(c):    # 6 bits, left-aligned in one byte
    return base_w((c << (8 - ell_2 * lg_w)).to_bytes(1, "big"), w, ell_2)

def all_digits(message):
    d = base_w(hashlib.sha256(message).digest()[:n], w, ell_1)
    return d + csum_digits(max_c - sum(d))

# The signer holds sk: 19 secret values, derived as at the start.
sk_seed, pk_seed = b"ch15-tiny-sk", b"ch15-tiny-pk"
sk = [hashlib.sha256(sk_seed + b"sk" + i.to_bytes(4, "big")).digest()[:n]
      for i in range(ell_1 + ell_2)]
pk = [chain_f(s, 0, w - 1, pk_seed, i) for i, s in enumerate(sk)]
print(sk[0].hex(), pk[0].hex())
# ==> 2c85517f 33b2bbda

def sign(message):
    return [chain_f(sk[i], 0, d, pk_seed, i) for i, d in enumerate(all_digits(message))]

def verify(message, sig):
    return all(chain_f(sig[i], d, w - 1 - d, pk_seed, i) == pk[i]
               for i, d in enumerate(all_digits(message)))

# The adversary holds pk, pk_seed and the signatures it has seen, never sk.
# At each chain it keeps the lowest (position, value) pair it was given,
# and from there it can only hash forward.
def forge(held, message):
    sig = []
    for i, ((pos, value), d) in enumerate(zip(held, all_digits(message))):
        if d < pos:
            return None    # would need a preimage
        sig.append(chain_f(value, pos, d - pos, pk_seed, i))
    return sig

m_a, m_b = b"first message", b"second message"
one = list(zip(all_digits(m_a), sign(m_a)))
two = [min(a, b) for a, b in zip(one, zip(all_digits(m_b), sign(m_b)))]

candidates = [b"forge-%d" % j for j in range(1 << 16)]
print(sum(forge(one, m) is not None for m in candidates))
# ==> 0
target = next(m for m in candidates if forge(two, m) is not None)
print(target.decode(), verify(target, forge(two, target)))
# ==> forge-2254 True

# How many of the 4^16 digests can the adversary sign? ways[s] counts the
# message-digit vectors with each digit at or above its held position and
# digit sum s. The checksum of that sum must clear the held checksum digits.
ways = {0: 1}
for pos, _ in two[:ell_1]:
    nxt = {}
    for s, k in ways.items():
        for d in range(pos, w):
            nxt[s + d] = nxt.get(s + d, 0) + k
    ways = nxt

def clears(s):
    return all(d >= pos for d, (pos, _) in zip(csum_digits(max_c - s), two[ell_1:]))

print(sum(k for s, k in ways.items() if clears(s)), w ** ell_1)
# ==> 351788 4294967296
