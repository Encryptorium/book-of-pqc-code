"""Round-trip tests for the ML-DSA-65+Ed25519 composite signature.

Construction per draft-ietf-lamps-pq-composite-sigs-19. ML-DSA-65 is
stubbed in this package (see ``mldsa_stub.py``), but the AND-mode
composite combiner, the M' message representative, and the
``mldsa_sig || ed_sig`` serialization order are real. These tests
verify the composite sizes, the sign/verify round-trip, and AND-mode
rejection when either component is tampered with.
"""

from hybrid.mldsa_stub import (
    MLDSA65_PK_BYTES,
    MLDSA65_SIG_BYTES,
    MLDSA65_SK_BYTES,
)
from hybrid.sig_combiner import (
    COMPOSITE_PK_BYTES,
    COMPOSITE_SIG_BYTES,
    COMPOSITE_SK_BYTES,
    composite_sig_keygen,
    composite_sig_sign,
    composite_sig_verify,
)


SEED_ED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc4" "4449c5697b326919703bac031cae7f60"
)
SEED_MLDSA = bytes(range(32))


def test_composite_sizes_match_fips_table2():
    assert MLDSA65_PK_BYTES == 1952
    assert MLDSA65_SK_BYTES == 4032
    assert MLDSA65_SIG_BYTES == 3309
    assert COMPOSITE_PK_BYTES == MLDSA65_PK_BYTES + 32
    assert COMPOSITE_SK_BYTES == MLDSA65_SK_BYTES + 32
    assert COMPOSITE_SIG_BYTES == MLDSA65_SIG_BYTES + 64


def test_composite_sig_roundtrip_verifies():
    pk, sk = composite_sig_keygen(SEED_ED, SEED_MLDSA)
    sig = composite_sig_sign(sk, b"hello hybrid world")
    assert len(sig) == COMPOSITE_SIG_BYTES
    assert composite_sig_verify(pk, b"hello hybrid world", sig) is True


def test_composite_sig_rejects_tampered_mldsa_component():
    """Byte 0 lives in the ML-DSA half under draft-19 serialization."""
    pk, sk = composite_sig_keygen(SEED_ED, SEED_MLDSA)
    sig = composite_sig_sign(sk, b"msg")
    tampered = bytearray(sig)
    tampered[0] ^= 0x01
    assert composite_sig_verify(pk, b"msg", bytes(tampered)) is False


def test_composite_sig_rejects_tampered_ed_component():
    """Byte 3309 is the first byte of the Ed25519 half."""
    pk, sk = composite_sig_keygen(SEED_ED, SEED_MLDSA)
    sig = composite_sig_sign(sk, b"msg")
    tampered = bytearray(sig)
    tampered[MLDSA65_SIG_BYTES] ^= 0x01
    assert composite_sig_verify(pk, b"msg", bytes(tampered)) is False


def test_composite_sig_rejects_wrong_message():
    pk, sk = composite_sig_keygen(SEED_ED, SEED_MLDSA)
    sig = composite_sig_sign(sk, b"message A")
    assert composite_sig_verify(pk, b"message B", sig) is False


def test_composite_sig_and_mode_requires_both_components():
    """A valid ML-DSA half paired with a wrong Ed25519 half must fail."""
    pk, sk = composite_sig_keygen(SEED_ED, SEED_MLDSA)
    sig = composite_sig_sign(sk, b"msg")

    other_seed_ed = bytes(range(1, 33))
    _, other_sk = composite_sig_keygen(other_seed_ed, SEED_MLDSA)
    other_sig = composite_sig_sign(other_sk, b"msg")

    # Keep the original ML-DSA half, swap in a different Ed25519 half.
    mixed = sig[:MLDSA65_SIG_BYTES] + other_sig[MLDSA65_SIG_BYTES:]
    assert composite_sig_verify(pk, b"msg", mixed) is False
