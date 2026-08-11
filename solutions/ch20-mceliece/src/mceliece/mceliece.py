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
    if rng is None:
        rng = random.Random()

    support = full_support(m)
    n = len(support)

    # find an irreducible Goppa polynomial g(x) of degree t
    g_coeffs = find_irreducible_goppa_poly(m, irred, t, rng)

    # filter support: remove roots of g(x) (should be none for irreducible g)
    # but keep the check for safety
    from mceliece.gf2m import poly_eval
    support = [a for a in support if poly_eval(g_coeffs, a, m, irred) != 0]
    n = len(support)

    # build parity-check matrix H (m*t-by-n binary)
    H = goppa_parity_check(m, irred, g_coeffs, support)

    # derive generator matrix G and column permutation from systematic form
    G, col_perm = generator_from_parity(H)
    k = len(G)

    # random invertible k-by-k scrambling matrix S
    S = random_invertible_matrix(k, rng)
    S_inv = gf2_mat_inv(S)

    # random column permutation P
    P, perm = random_permutation_matrix(n, rng)

    # public key: G_pub = S * G * P
    SG = mat_mul(S, G)
    G_pub = mat_mul(SG, P)

    # inverse permutation for decryption
    perm_inv = [0] * n
    for i, j in enumerate(perm):
        perm_inv[j] = i

    public_key = {"G_pub": G_pub, "t": t, "n": n, "k": k}
    secret_key = {
        "S": S, "S_inv": S_inv,
        "g_coeffs": g_coeffs, "support": support,
        "perm": perm, "perm_inv": perm_inv,
        "m": m, "irred": irred, "col_perm": col_perm,
    }
    return public_key, secret_key


def encrypt(
    public_key: dict,
    message: list[int],
    rng: random.Random | None = None,
) -> list[int]:
    """Encrypt a k-bit message.

    Returns ciphertext c = m * G_pub XOR e, where e has weight t.
    """
    if rng is None:
        rng = random.Random()

    G_pub = public_key["G_pub"]
    t = public_key["t"]
    n = public_key["n"]
    k = public_key["k"]

    if len(message) != k:
        raise ValueError(f"message must be {k} bits, got {len(message)}")

    # c_0 = m * G_pub  (message times generator, a length-n vector)
    # mat_vec_mul does A*v; we need m*G_pub = G_pub^T * m as a column op
    # or equivalently: sum of rows of G_pub where m[i]=1
    c = [0] * n
    for i, mi in enumerate(message):
        if mi:
            c = vec_add(c, G_pub[i])

    # add weight-t error
    error_positions = rng.sample(range(n), t)
    e = [0] * n
    for pos in error_positions:
        e[pos] = 1
    c = vec_add(c, e)
    return c


def decrypt(secret_key: dict, ciphertext: list[int]) -> list[int]:
    """Decrypt a ciphertext to recover the k-bit message.

    Steps:
    1. Undo column permutation P: c' = c * P^{-1}
    2. Decode c' using Patterson's algorithm to get the codeword
    3. Extract the message bits (first k positions in systematic form)
    4. Undo scrambling: m = m' * S^{-1}
    """
    perm_inv = secret_key["perm_inv"]
    S_inv = secret_key["S_inv"]
    g_coeffs = secret_key["g_coeffs"]
    m = secret_key["m"]
    irred = secret_key["irred"]
    col_perm = secret_key["col_perm"]

    n = len(ciphertext)
    k = len(S_inv)

    # Step 1: undo column permutation P
    c_unperm = [0] * n
    for i in range(n):
        c_unperm[perm_inv[i]] = ciphertext[i]

    # c_unperm is now in the systematic coordinate system (the one G lives in).
    # Reorder support to match: position i in systematic form corresponds
    # to original column col_perm[i].
    support = secret_key["support"]
    support_sys = [support[col_perm[i]] for i in range(n)]

    # Step 2: Patterson decode in systematic coordinates
    codeword = patterson_decode(c_unperm, g_coeffs, support_sys, m, irred)

    # Step 3: extract message bits.  G = [B^T | I_k], so the message
    # (scrambled by S) occupies the last k positions of the codeword.
    m_scrambled = codeword[n - k:]

    # Step 4: undo scrambling.  m_scrambled = m * S (row vector convention),
    # so m = m_scrambled * S^{-1} = S^{-T} * m_scrambled (column convention).
    message = mat_vec_mul(transpose(S_inv), m_scrambled)
    return message
