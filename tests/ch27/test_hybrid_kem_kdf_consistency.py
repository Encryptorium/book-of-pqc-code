"""HKDF-consistency tests for the X25519MLKEM768 combiner.

Verifies that the combiner output is a deterministic function of the
two component shared secrets and that the transcript hash produced
by the combiner is stable across re-runs.
"""

import hashlib

from hybrid.kem_combiner import (
    X25519MLKEM768_NAMED_GROUP,
    X25519MLKEM768_SS_BYTES,
    hybrid_kem_decaps,
    hybrid_kem_encaps,
    hybrid_kem_keygen,
)


def test_named_group_codepoint_is_0x11ec():
    assert X25519MLKEM768_NAMED_GROUP == 0x11EC


def test_combiner_output_is_32_bytes():
    pk, sk = hybrid_kem_keygen()
    _, ss = hybrid_kem_encaps(pk)
    assert len(ss) == X25519MLKEM768_SS_BYTES == 32


def test_combiner_output_is_pinned_against_fixed_inputs():
    """Pin the derived secret to a constant, not just to itself.

    Every other assertion in this file is relative: a length, a
    determinism check, a difference. All of them survive a combiner that
    concatenates the two shared secrets in the wrong order, or that
    changes the label. This one does not, which is what makes the
    chapter's claim about test vectors true.
    """
    d = b"\x01" * 32
    z = b"\x02" * 32
    x = b"\x03" * 32
    m = b"\x04" * 32
    e = b"\x05" * 32
    pk, sk = hybrid_kem_keygen(seed_mlkem_d=d, seed_mlkem_z=z, seed_x25519=x)
    ct, ss = hybrid_kem_encaps(pk, seed_mlkem=m, seed_x25519_ephemeral=e)
    assert ss.hex() == (
        "843868a64d79e0b3b42f24164f790ed9dbacc1b520d94055c77e3ee5ab988b4e"
    )
    assert hybrid_kem_decaps(sk, ct) == ss


def test_combiner_output_stable_for_same_inputs():
    d = b"\x01" * 32
    z = b"\x02" * 32
    x = b"\x03" * 32
    m = b"\x04" * 32
    e = b"\x05" * 32
    pk, sk = hybrid_kem_keygen(seed_mlkem_d=d, seed_mlkem_z=z, seed_x25519=x)
    _, ss_run1 = hybrid_kem_encaps(pk, seed_mlkem=m, seed_x25519_ephemeral=e)
    _, ss_run2 = hybrid_kem_encaps(pk, seed_mlkem=m, seed_x25519_ephemeral=e)
    assert ss_run1 == ss_run2


def test_transcript_hash_stable_under_repeated_runs():
    d = b"\x11" * 32
    z = b"\x22" * 32
    x = b"\x33" * 32
    pk, sk = hybrid_kem_keygen(seed_mlkem_d=d, seed_mlkem_z=z, seed_x25519=x)
    digests = []
    for i in range(3):
        m = bytes([i]) + b"\x00" * 31
        e = bytes([i]) + b"\xff" * 31
        ct, ss = hybrid_kem_encaps(pk, seed_mlkem=m, seed_x25519_ephemeral=e)
        digest = hashlib.sha256(ct + ss).hexdigest()
        digests.append(digest)
    ct0, ss0 = hybrid_kem_encaps(
        pk,
        seed_mlkem=b"\x00" + b"\x00" * 31,
        seed_x25519_ephemeral=b"\x00" + b"\xff" * 31,
    )
    assert hashlib.sha256(ct0 + ss0).hexdigest() == digests[0]


def test_different_seeds_produce_different_shared_secrets():
    pk, sk = hybrid_kem_keygen(
        seed_mlkem_d=b"a" * 32, seed_mlkem_z=b"b" * 32, seed_x25519=b"c" * 32
    )
    _, ss1 = hybrid_kem_encaps(
        pk, seed_mlkem=b"m1" + b"\x00" * 30, seed_x25519_ephemeral=b"e1" + b"\x00" * 30
    )
    _, ss2 = hybrid_kem_encaps(
        pk, seed_mlkem=b"m2" + b"\x00" * 30, seed_x25519_ephemeral=b"e2" + b"\x00" * 30
    )
    assert ss1 != ss2
