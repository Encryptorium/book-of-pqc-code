"""Round-trip tests for the X25519MLKEM768 hybrid KEM.

Exercises: keygen produces wire-format byte sizes; encaps+decaps
agree on the shared secret; tampering the ciphertext breaks the
round-trip.
"""

import os

from hybrid.kem_combiner import (
    X25519MLKEM768_CT_BYTES,
    X25519MLKEM768_PK_BYTES,
    X25519MLKEM768_SS_BYTES,
    hybrid_kem_decaps,
    hybrid_kem_encaps,
    hybrid_kem_keygen,
)


def test_hybrid_kem_keygen_wire_format_sizes():
    pk, sk = hybrid_kem_keygen()
    assert len(pk) == X25519MLKEM768_PK_BYTES == 1216
    assert len(sk) == 2400 + 32


def test_hybrid_kem_roundtrip_matches_shared_secret():
    pk, sk = hybrid_kem_keygen()
    ct, ss_alice = hybrid_kem_encaps(pk)
    assert len(ct) == X25519MLKEM768_CT_BYTES == 1120
    assert len(ss_alice) == X25519MLKEM768_SS_BYTES == 32
    ss_bob = hybrid_kem_decaps(sk, ct)
    assert ss_alice == ss_bob


def test_hybrid_kem_roundtrip_deterministic_with_fixed_seeds():
    d = b"d" * 32
    z = b"z" * 32
    x = b"x" * 32
    m = b"m" * 32
    e = b"e" * 32
    pk, sk = hybrid_kem_keygen(seed_mlkem_d=d, seed_mlkem_z=z, seed_x25519=x)
    ct1, ss1 = hybrid_kem_encaps(pk, seed_mlkem=m, seed_x25519_ephemeral=e)
    ct2, ss2 = hybrid_kem_encaps(pk, seed_mlkem=m, seed_x25519_ephemeral=e)
    assert ct1 == ct2
    assert ss1 == ss2
    assert hybrid_kem_decaps(sk, ct1) == ss1


def test_hybrid_kem_rejects_tampered_x25519_component():
    pk, sk = hybrid_kem_keygen()
    ct, ss_alice = hybrid_kem_encaps(pk)
    tampered = bytearray(ct)
    tampered[-1] ^= 0x01
    ss_bob = hybrid_kem_decaps(sk, bytes(tampered))
    assert ss_bob != ss_alice


def test_the_high_bit_of_the_x25519_component_is_not_bound():
    """A distinct ciphertext that decapsulates to the same shared secret.

    RFC 7748 masks bit 255 of the u-coordinate before scalar
    multiplication, so flipping it changes the ciphertext without
    changing the X25519 output. The combiner derives from the two
    shared secrets and a fixed label only, so the derived key follows
    the secret rather than the ciphertext. This is the standalone
    ciphertext-binding gap the chapter discusses: TLS closes it later
    through the transcript hash, and the analysed combiner of Bindel et
    al. closes it by keying its second PRF with ``c1 || c2``.
    """
    pk, sk = hybrid_kem_keygen()
    ct, ss_alice = hybrid_kem_encaps(pk)
    tampered = bytearray(ct)
    tampered[-1] ^= 0x80
    assert bytes(tampered) != ct
    assert hybrid_kem_decaps(sk, bytes(tampered)) == ss_alice


def test_hybrid_kem_with_random_urandom_seeds_produces_32_byte_secret():
    pk, sk = hybrid_kem_keygen()
    ct, ss = hybrid_kem_encaps(pk, seed_mlkem=os.urandom(32))
    assert len(ss) == 32
    assert hybrid_kem_decaps(sk, ct) == ss
