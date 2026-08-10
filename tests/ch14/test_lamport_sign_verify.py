"""Tests for Lamport OTS sign and verify."""

from lamport_merkle.lamport import keygen, sign, verify


SEED = b"ch14-sign-verify-test"


def test_sign_verify_roundtrip():
    sk, pk = keygen(rng=SEED)
    msg = b"test message"
    sig = sign(sk, msg)
    assert verify(pk, msg, sig)


def test_signature_length_is_256():
    sk, _ = keygen(rng=SEED)
    sig = sign(sk, b"msg")
    assert len(sig) == 256


def test_each_signature_element_is_32_bytes():
    sk, _ = keygen(rng=SEED)
    sig = sign(sk, b"msg")
    for s in sig:
        assert len(s) == 32


def test_verify_rejects_wrong_message():
    sk, pk = keygen(rng=SEED)
    sig = sign(sk, b"message A")
    assert not verify(pk, b"message B", sig)


def test_verify_rejects_corrupted_signature():
    sk, pk = keygen(rng=SEED)
    msg = b"test"
    sig = sign(sk, msg)
    # Flip one byte in the first element.
    corrupted = list(sig)
    bad = bytearray(corrupted[0])
    bad[0] ^= 0xFF
    corrupted[0] = bytes(bad)
    assert not verify(pk, msg, corrupted)


def test_verify_rejects_wrong_length_signature():
    sk, pk = keygen(rng=SEED)
    msg = b"test"
    sig = sign(sk, msg)
    assert not verify(pk, msg, sig[:255])
