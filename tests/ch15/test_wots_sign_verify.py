"""Tests for WOTS+ sign and verify round-trip."""

from wots_xmss.wots import wots_keygen, wots_sign, wots_verify


SK_SEED = b"test-sign-verify-sk"
PK_SEED = b"test-sign-verify-pk"


def test_roundtrip():
    """Sign then verify returns True."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED)
    message = b"hello wots+"
    sig = wots_sign(sk, message, PK_SEED)
    assert wots_verify(pk, message, sig, PK_SEED)


def test_wrong_message_rejected():
    """Verification fails on a different message."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED)
    sig = wots_sign(sk, b"message-a", PK_SEED)
    assert not wots_verify(pk, b"message-b", sig, PK_SEED)


def test_tampered_signature_rejected():
    """Flipping a byte in one chain value breaks verification."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED)
    message = b"tamper test"
    sig = wots_sign(sk, message, PK_SEED)

    tampered = list(sig)
    bad_value = bytearray(sig[0])
    bad_value[0] ^= 0xFF
    tampered[0] = bytes(bad_value)
    assert not wots_verify(pk, message, tampered, PK_SEED)


def test_wrong_seed_rejected():
    """Verification with a different public seed fails."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED)
    message = b"seed mismatch"
    sig = wots_sign(sk, message, PK_SEED)
    assert not wots_verify(pk, message, sig, b"wrong-seed")


def test_signature_length():
    """Signature has ell=67 entries at w=16."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=16)
    sig = wots_sign(sk, b"length check", PK_SEED, w=16)
    assert len(sig) == 67
    assert all(len(s) == 32 for s in sig)


def test_roundtrip_w4():
    """Round-trip at w=4."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=4)
    message = b"w=4 test"
    sig = wots_sign(sk, message, PK_SEED, w=4)
    assert wots_verify(pk, message, sig, PK_SEED, w=4)
