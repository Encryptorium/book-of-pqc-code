"""HQC key generation, encryption, and decryption (IND-CPA core).

This is a toy implementation for pedagogy.  It demonstrates the
quasi-cyclic structure that compresses code-based public keys and
the repetition inner code that absorbs decryption noise.
"""

import random

from hqc.poly_gf2 import poly_add, poly_mul
from hqc.sparse import sample_sparse
from hqc.repetition import rep_encode, rep_decode


def keygen(
    n: int, w: int, w_r: int, w_e: int, r: int, rng: random.Random
) -> tuple[dict, dict]:
    """Generate an HQC key pair.

    Parameters
    ----------
    n : int      -- polynomial ring degree (x^n - 1)
    w : int      -- secret key sparse weight
    w_r : int    -- encryption sparse weight (for r1, r2)
    w_e : int    -- error vector sparse weight
    r : int      -- repetition factor for the inner code
    rng          -- seeded Random instance

    Returns (public_key, secret_key) where
      public_key = {"s": list, "h": list, "n": int, "w_r": int, "w_e": int, "r": int}
      secret_key = {"x": list, "y": list}
    """
    # Sample uniform random polynomial s
    s = [rng.randint(0, 1) for _ in range(n)]

    # Sample sparse secret vectors
    x = sample_sparse(n, w, rng)
    y = sample_sparse(n, w, rng)

    # Public key: h = x + s * y  in GF(2)[x]/(x^n - 1)
    h = poly_add(x, poly_mul(s, y, n))

    public_key = {"s": s, "h": h, "n": n, "w_r": w_r, "w_e": w_e, "r": r}
    secret_key = {"x": x, "y": y}
    return public_key, secret_key


def encrypt(
    pk: dict, message: list[int], rng: random.Random
) -> tuple[list[int], list[int]]:
    """Encrypt a message under the HQC public key.

    Returns ciphertext (u, v) where u, v are length-n binary vectors.
    """
    n = pk["n"]
    w_r = pk["w_r"]
    w_e = pk["w_e"]
    r = pk["r"]
    s = pk["s"]
    h = pk["h"]

    # Sample sparse encryption vectors
    r1 = sample_sparse(n, w_r, rng)
    r2 = sample_sparse(n, w_r, rng)
    e = sample_sparse(n, w_e, rng)

    # u = r1 + r2 * s
    u = poly_add(r1, poly_mul(r2, s, n))

    # v = r2 * h + encode(m) + e
    codeword = rep_encode(message, r, n)
    v = poly_add(poly_add(poly_mul(r2, h, n), codeword), e)

    return u, v


def decrypt(
    sk: dict, pk: dict, ct: tuple[list[int], list[int]]
) -> list[int]:
    """Decrypt a ciphertext using the HQC secret key.

    Computes v - u*y (over GF(2), subtraction = addition), which equals
    encode(m) + noise.  Decodes the repetition code to recover m.
    """
    n = pk["n"]
    r = pk["r"]
    u, v = ct
    y = sk["y"]

    # v + u*y = encode(m) + (r2*x + r1*y + e)
    noisy_code = poly_add(v, poly_mul(u, y, n))

    # Decode the repetition code
    message = rep_decode(noisy_code, r, n)
    return message
