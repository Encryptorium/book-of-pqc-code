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
    # EXERCISE: implement this function.
    #
    # Draw s as n uniform bits from rng, then x and y as weight-w sparse
    # vectors, in that order. The draw order is part of the contract,
    # because the tests and the chapter's printed supports reconstruct keys
    # from a seed. The public key is h = x + s*y in the ring, packaged
    # alongside s, n, and the parameters w_r, w_e, and r that encryption
    # will need; the secret is the pair (x, y) and nothing else. Recovering
    # (x, y) from (s, h) is the quasi-cyclic syndrome decoding problem.
    #
    # Reference: Chapter 21, 'HQC key generation'
    #
    # Proved by:
    #   tests/ch21/test_hqc_keygen.py
    #   tests/ch21/test_hqc_encrypt_decrypt.py
    raise NotImplementedError("exercise: keygen")


def encrypt(
    pk: dict, message: list[int], rng: random.Random
) -> tuple[list[int], list[int]]:
    """Encrypt a message under the HQC public key.

    Returns ciphertext (u, v) where u, v are length-n binary vectors.
    """
    # EXERCISE: implement this function.
    #
    # Draw r1, r2, and e from rng in that order, the first two at weight w_r
    # and e at weight w_e. Then u = r1 + r2*s and v = r2*h +
    # rep_encode(message, r, n) + e. Both halves are length n, so the
    # ciphertext is 2n bits, the same size as the public key. Encode the
    # message before masking rather than after: the repetition code is what
    # gives decryption the slack to absorb the noise term.
    #
    # Reference: Chapter 21, 'HQC encryption'
    #
    # Proved by:
    #   tests/ch21/test_hqc_encrypt_decrypt.py
    #   tests/ch21/test_hqc_noise_budget.py
    raise NotImplementedError("exercise: encrypt")


def decrypt(
    sk: dict, pk: dict, ct: tuple[list[int], list[int]]
) -> list[int]:
    """Decrypt a ciphertext using the HQC secret key.

    Computes v - u*y (over GF(2), subtraction = addition), which equals
    encode(m) + noise.  Decodes the repetition code to recover m.
    """
    # EXERCISE: implement this function.
    #
    # Compute v + u*y in the ring and hand the result to rep_decode.
    # Expanding h = x + s*y and u = r1 + r2*s makes the mask telescope away,
    # leaving rep_encode(m) + (r2*x + r1*y + e). Adding rather than
    # subtracting is correct because a value is its own additive inverse
    # over GF(2). Nothing here inspects the noise: if some repetition block
    # picked up more than floor((r-1)/2) flips, this returns a wrong message
    # rather than raising, which is exactly the decryption failure the noise
    # budget bounds.
    #
    # Reference: Chapter 21, 'HQC decryption and noise cancellation'
    #
    # Proved by:
    #   tests/ch21/test_hqc_encrypt_decrypt.py
    #   tests/ch21/test_hqc_noise_budget.py
    raise NotImplementedError("exercise: decrypt")
