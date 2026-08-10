"""The [7,4,3] Hamming code: encode, syndrome, decode.

The parity-check matrix H is 3-by-7 and is in systematic form [A | I_3],
so its columns run 110, 101, 011, 111, 100, 010, 001.  Those are the seven
nonzero vectors of GF(2)^3 in a different order from the ascending-binary
convention 001, 010, 011, ...; both orderings give a valid [7,4,3] Hamming
code, and the systematic one is chosen here because it pairs directly with
the systematic generator matrix G = [I_4 | A^T] so that G * H^T = 0
over GF(2).
"""

from coding_theory.gf2 import mat_vec_mul, weight


def parity_check_matrix() -> list[list[int]]:
    """Return the 3-by-7 parity-check matrix H for the [7,4,3] Hamming code.

    Systematic form H = [A | I_3].  The first four columns (A) are the
    four nonzero 3-bit vectors with weight >= 2, and the last three
    columns form I_3.  Every column is distinct and nonzero, so the
    columns are exactly the seven nonzero vectors of GF(2)^3.

    This pairs with G = [I_4 | A^T] so that G * H^T = 0 over GF(2).
    """
    return [
        [1, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 1],
    ]


def generator_matrix() -> list[list[int]]:
    """Return the 4-by-7 systematic generator matrix G for the [7,4,3] Hamming code.

    G = [I_4 | P] where P = A^T from the parity-check matrix H = [A | I_3].
    The message occupies positions 0..3 and the parity bits occupy 4..6.
    """
    return [
        [1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 1],
        [0, 0, 1, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ]


def encode(message: list[int]) -> list[int]:
    """Encode a 4-bit message into a 7-bit Hamming codeword.

    c = m * G computed as the linear combination of G's rows selected
    by the message bits.
    """
    G = generator_matrix()
    codeword = [0] * 7
    for i, bit in enumerate(message):
        if bit:
            codeword = [(c ^ g) for c, g in zip(codeword, G[i])]
    return codeword


def syndrome(received: list[int]) -> list[int]:
    """Compute the syndrome s = H * r^T for a received 7-bit word."""
    H = parity_check_matrix()
    return mat_vec_mul(H, received)


def syndrome_table() -> dict[tuple[int, ...], int]:
    """Build the syndrome-to-error-position lookup table.

    Returns a dict mapping each nonzero syndrome (as a tuple) to the
    0-indexed error position.  The zero syndrome maps to -1 (no error).
    """
    H = parity_check_matrix()
    table: dict[tuple[int, ...], int] = {(0, 0, 0): -1}
    for j in range(7):
        col = tuple(H[r][j] for r in range(3))
        table[col] = j
    return table


def decode(received: list[int]) -> list[int]:
    """Syndrome-decode a received 7-bit word, correcting at most one error.

    Returns the 4-bit message (positions 0..3 of the corrected codeword).
    """
    s = syndrome(received)
    table = syndrome_table()
    s_key = tuple(s)
    corrected = list(received)
    pos = table.get(s_key, -1)
    if pos >= 0:
        corrected[pos] ^= 1
    return corrected[:4]
