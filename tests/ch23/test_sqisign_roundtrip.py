"""Tests for the toy SQIsign protocol at p = 431."""

from sqisign.sqisign import keygen, sign, verify


def test_keygen_deterministic():
    """keygen with the same seed produces the same key."""
    sk1 = keygen(b"alice")
    sk2 = keygen(b"alice")
    assert sk1.pk.a == sk2.pk.a
    assert sk1.pk.b == sk2.pk.b
    assert sk1.walk == sk2.walk


def test_keygen_different_seeds():
    """Different seeds give different keys (with high probability)."""
    sk1 = keygen(b"alice")
    sk2 = keygen(b"bob")
    # Walks should differ even if final j-invariants happen to coincide.
    assert sk1.walk != sk2.walk


def test_sign_verify_roundtrip():
    """A valid signature verifies."""
    sk = keygen(b"alice")
    message = b"the quick brown fox"
    sig = sign(message, sk)
    assert verify(message, sig, sk.pk)


def test_verify_rejects_wrong_message():
    """A signature for one message does not verify another."""
    sk = keygen(b"alice")
    sig = sign(b"original message", sk)
    assert not verify(b"different message", sig, sk.pk)


def test_verify_rejects_wrong_key():
    """A signature from one signer does not verify under a different public key."""
    sk_alice = keygen(b"alice")
    sk_bob = keygen(b"bob")
    message = b"test message"
    sig_alice = sign(message, sk_alice)
    # If Bob's pk happens to match Alice's pk (very unlikely), skip.
    if sk_alice.pk.a == sk_bob.pk.a and sk_alice.pk.b == sk_bob.pk.b:
        return
    assert not verify(message, sig_alice, sk_bob.pk)


def test_sign_two_messages_different_signatures():
    """Signing two different messages yields two different signatures."""
    sk = keygen(b"alice")
    sig1 = sign(b"message one", sk)
    sig2 = sign(b"message two", sk)
    # The signatures differ at least in length or in some step.
    assert sig1 != sig2
