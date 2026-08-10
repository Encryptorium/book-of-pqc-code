"""Tests for FORS sign and verify."""

from fors_hypertree.fors import (
    fors_keygen,
    fors_sign,
    fors_verify,
    message_indices,
    _verify_path,
)


def test_sign_verify_roundtrip():
    """Sign a message and verify succeeds."""
    seed = b"fors-roundtrip"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    message = b"hello FORS"
    sig = fors_sign(sk_leaves, trees, message, k=k, t=t, n=n)
    assert fors_verify(pk, message, sig, k=k, t=t, n=n)


def test_wrong_message_rejected():
    """Verification with a different message fails."""
    seed = b"fors-wrong-msg"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    sig = fors_sign(sk_leaves, trees, b"correct", k=k, t=t, n=n)
    assert not fors_verify(pk, b"wrong", sig, k=k, t=t, n=n)


def test_wrong_pk_rejected():
    """Verification against a different pk fails."""
    k, t, n = 6, 16, 32
    sk1, trees1, pk1 = fors_keygen(b"seed-1", k=k, t=t, n=n)
    _, _, pk2 = fors_keygen(b"seed-2", k=k, t=t, n=n)

    sig = fors_sign(sk1, trees1, b"test", k=k, t=t, n=n)
    assert fors_verify(pk1, b"test", sig, k=k, t=t, n=n)
    assert not fors_verify(pk2, b"test", sig, k=k, t=t, n=n)


def test_signature_contains_correct_leaves():
    """The revealed leaf at each position matches sk_leaves[j][index_j]."""
    seed = b"leaf-check"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    message = b"check leaves"
    indices = message_indices(message, k, t)
    sig = fors_sign(sk_leaves, trees, message, k=k, t=t, n=n)

    for j in range(k):
        revealed_leaf, _ = sig[j]
        assert revealed_leaf == sk_leaves[j][indices[j]]


def test_auth_paths_reconstruct_roots():
    """Each auth path reconstructs the correct tree root."""
    seed = b"path-check"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    message = b"auth path test"
    indices = message_indices(message, k, t)
    sig = fors_sign(sk_leaves, trees, message, k=k, t=t, n=n)

    for j in range(k):
        leaf, path = sig[j]
        root = trees[j][1]
        assert _verify_path(leaf, indices[j], path, root)


def test_multiple_messages():
    """Multiple different messages all verify correctly."""
    seed = b"multi-msg"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    for i in range(10):
        msg = f"message-{i}".encode()
        sig = fors_sign(sk_leaves, trees, msg, k=k, t=t, n=n)
        assert fors_verify(pk, msg, sig, k=k, t=t, n=n)


def test_small_parameters():
    """Verify at toy parameters k=3, t=4, n=32."""
    seed = b"toy-fors"
    k, t, n = 3, 4, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    sig = fors_sign(sk_leaves, trees, b"toy", k=k, t=t, n=n)
    assert fors_verify(pk, b"toy", sig, k=k, t=t, n=n)
