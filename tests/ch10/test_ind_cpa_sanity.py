"""IND-CPA sanity check.

Regev encryption is randomized: two encryptions of the same bit under
the same public key produce different ciphertexts. This is a necessary
(not sufficient) condition for IND-CPA security. A deterministic
encryption of the same plaintext would leak the plaintext trivially.
"""

import numpy as np

from regev_pke import keygen, encrypt, decrypt


def test_same_bit_gives_different_ciphertexts(toy):
    rng = np.random.default_rng(seed=0)
    pk, sk = keygen(toy, rng)
    ct_a = encrypt(toy, pk, 0, rng)
    ct_b = encrypt(toy, pk, 0, rng)
    # The two ciphertexts must not be identical. With overwhelming
    # probability the randomness r differs between the two encryptions,
    # so (c1, c2) differs too.
    same_c1 = np.array_equal(ct_a[0], ct_b[0])
    same_c2 = int(ct_a[1]) == int(ct_b[1])
    assert not (same_c1 and same_c2), (
        "same-bit encryptions must not produce identical ciphertexts"
    )
    # Sanity: both still decrypt to the original bit.
    assert decrypt(toy, sk, ct_a) == 0
    assert decrypt(toy, sk, ct_b) == 0


def test_one_bit_same_property(toy):
    rng = np.random.default_rng(seed=1)
    pk, sk = keygen(toy, rng)
    ct_a = encrypt(toy, pk, 1, rng)
    ct_b = encrypt(toy, pk, 1, rng)
    same = (
        np.array_equal(ct_a[0], ct_b[0]) and int(ct_a[1]) == int(ct_b[1])
    )
    assert not same
    assert decrypt(toy, sk, ct_a) == 1
    assert decrypt(toy, sk, ct_b) == 1
