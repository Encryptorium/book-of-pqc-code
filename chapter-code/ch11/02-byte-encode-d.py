# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "Serialization: ByteEncode and ByteDecode"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/02-byte-encode-d.py

import numpy as np

Q = 3329
N = 256


def byte_encode_d(f, d):
    assert f.shape == (N,)
    # Precondition: for d < 12 the coefficients are already reduced
    # modulo 2^d; for d = 12 they are reduced modulo q. FIPS ByteEncode
    # does not itself mask, so assert the range rather than rely on it.
    if d == 12:
        assert bool(np.all((0 <= f) & (f < Q)))
    else:
        assert bool(np.all((0 <= f) & (f < (1 << d))))
    mask = (1 << d) - 1
    big = 0
    for i in range(N):
        big |= (int(f[i]) & mask) << (i * d)
    return big.to_bytes(32 * d, "little")


def byte_decode_d(B, d):
    assert len(B) == 32 * d
    mask = (1 << d) - 1
    big = int.from_bytes(B, "little")
    f = np.zeros(N, dtype=np.int64)
    for i in range(N):
        coeff = (big >> (i * d)) & mask
        if d == 12:
            coeff %= Q
        f[i] = coeff
    return f


rng = np.random.default_rng(seed=20260411)
f = rng.integers(0, Q, size=N, dtype=np.int64)
encoded = byte_encode_d(f, 12)
decoded = byte_decode_d(encoded, 12)
print("encoded length =", len(encoded))
print("round trip equal =", bool(np.array_equal(decoded, f)))
# ==> encoded length = 384
# ==> round trip equal = True
