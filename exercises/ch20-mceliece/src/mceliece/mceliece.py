"""McEliece public-key cryptosystem: keygen, encrypt, decrypt.

Hides a binary Goppa code behind a scrambling matrix S and a column
permutation P.  The public key G_pub = S * G * P looks like a random
k-by-n binary matrix.  Encryption adds a weight-t error.  Decryption
inverts P, decodes with Patterson's algorithm, then inverts S.
"""

import random

from mceliece.gf2 import (
    mat_mul, mat_vec_mul, vec_add, weight, transpose,
    identity, gf2_mat_inv, generator_from_parity,
    random_invertible_matrix, random_permutation_matrix,
)
from mceliece.gf2m import gf2m_inv
from mceliece.goppa import (
    find_irreducible_goppa_poly, goppa_parity_check, full_support,
)
from mceliece.patterson import patterson_decode


def keygen(
    m: int, t: int, irred: int, rng: random.Random | None = None,
) -> tuple[dict, dict]:
    """Generate a McEliece key pair.

    Parameters
    ----------
    m : field extension degree (GF(2^m))
    t : error-correcting capacity (degree of Goppa polynomial)
    irred : irreducible polynomial for GF(2^m) as an integer
    rng : random.Random instance for reproducibility

    Returns
    -------
    (public_key, secret_key) where:
      public_key = {"G_pub": k-by-n matrix, "t": int, "n": int, "k": int}
      secret_key = {"S": k-by-k, "S_inv": k-by-k, "g_coeffs": list,
                     "support": list, "perm": list, "perm_inv": list,
                     "m": int, "irred": int, "col_perm": list}
    """
    # EXERCISE: implement this function.
    #
    # Take the full 2^m support, draw an irreducible g of degree t, drop any
    # support element that is a root of g (an irreducible g has none, but
    # the filter keeps n honest), and build H with goppa_parity_check.
    # Derive G and col_perm with generator_from_parity, then sample S with
    # random_invertible_matrix(k) along with its inverse, and P with
    # random_permutation_matrix(n). The public key is G_pub = S * G * P and
    # nothing else. The secret key has to carry S_inv, g, the support, both
    # directions of the permutation, m, irred, and col_perm: without
    # col_perm the support sits in the wrong order for the systematic
    # coordinates and Patterson decodes to noise.
    #
    # Reference: Chapter 20, 'The three algorithms: original McEliece-style PKE'
    #
    # Proved by:
    #   tests/ch20/test_mceliece_keygen.py
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: keygen")


def encrypt(
    public_key: dict,
    message: list[int],
    rng: random.Random | None = None,
) -> list[int]:
    """Encrypt a k-bit message.

    Returns ciphertext c = m * G_pub XOR e, where e has weight t.
    """
    # EXERCISE: implement this function.
    #
    # Reject a message whose length is not k, then XOR together the rows of
    # G_pub that the message bits select, which computes m * G_pub without
    # forming a matrix product. Sample exactly t distinct positions with
    # rng.sample and XOR a weight-t error vector in. The error is what makes
    # this encryption rather than encoding: without it any receiver could
    # invert the linear map, and the trapdoor would buy nothing.
    #
    # Reference: Chapter 20, 'The three algorithms: original McEliece-style PKE'
    #
    # Proved by:
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: encrypt")


def decrypt(secret_key: dict, ciphertext: list[int]) -> list[int]:
    """Decrypt a ciphertext to recover the k-bit message.

    Steps:
    1. Undo column permutation P: c' = c * P^{-1}
    2. Decode c' using Patterson's algorithm to get the codeword
    3. Extract the message bits (first k positions in systematic form)
    4. Undo scrambling: m = m' * S^{-1}
    """
    # EXERCISE: implement this function.
    #
    # Four steps. Undo the permutation by scattering ciphertext position i
    # to position perm_inv[i]. Reorder the support the same way
    # gauss_systematic reordered the columns, so support_sys[i] is
    # support[col_perm[i]], then run patterson_decode on the unpermuted word
    # to recover the codeword. Because G is [B^T | I_k] the scrambled
    # message is the last k bits, not the first. Finally undo S: encryption
    # used the row-vector convention m_scrambled = m * S, so recover m as
    # mat_vec_mul(transpose(S_inv), m_scrambled). Getting either the support
    # reordering or the tail slice wrong produces a clean-looking wrong
    # answer rather than an exception.
    #
    # Reference: Chapter 20, 'The three algorithms: original McEliece-style PKE'
    #
    # Proved by:
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: decrypt")
