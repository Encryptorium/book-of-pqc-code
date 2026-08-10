"""Tests for hypertree sign and verify round-trip."""

from fors_hypertree.hypertree import hypertree_keygen, hypertree_sign, hypertree_verify


SEED = b"hypertree-test-seed"


def test_sign_verify_leaf_zero():
    """Sign and verify at leaf index 0."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)
    message = b"leaf zero"
    sig = hypertree_sign(sk, 0, message, SEED, d=d, h_prime=h_prime)
    assert hypertree_verify(pk, 0, message, sig, SEED, d=d, h_prime=h_prime)


def test_sign_verify_last_leaf():
    """Sign and verify at the maximum leaf index."""
    d, h_prime = 2, 4
    max_leaf = (1 << (d * h_prime)) - 1
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)
    message = b"last leaf"
    sig = hypertree_sign(sk, max_leaf, message, SEED, d=d, h_prime=h_prime)
    assert hypertree_verify(pk, max_leaf, message, sig, SEED, d=d, h_prime=h_prime)


def test_sign_verify_multiple_leaves():
    """Sign and verify at several different leaf indices."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)

    for leaf_idx in [0, 7, 15, 128, 200, 255]:
        message = f"leaf-{leaf_idx}".encode()
        sig = hypertree_sign(sk, leaf_idx, message, SEED, d=d, h_prime=h_prime)
        assert hypertree_verify(
            pk, leaf_idx, message, sig, SEED, d=d, h_prime=h_prime
        ), f"Verification failed at leaf {leaf_idx}"


def test_wrong_message_rejected():
    """Verification fails for the wrong message."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)

    sig = hypertree_sign(sk, 42, b"correct", SEED, d=d, h_prime=h_prime)
    assert not hypertree_verify(pk, 42, b"wrong", sig, SEED, d=d, h_prime=h_prime)


def test_wrong_root_rejected():
    """Verification fails against a different pk."""
    d, h_prime = 2, 4
    sk1, pk1 = hypertree_keygen(b"seed-1", d=d, h_prime=h_prime)
    _, pk2 = hypertree_keygen(b"seed-2", d=d, h_prime=h_prime)

    sig = hypertree_sign(sk1, 10, b"test", b"seed-1", d=d, h_prime=h_prime)
    assert hypertree_verify(pk1, 10, b"test", sig, b"seed-1", d=d, h_prime=h_prime)
    assert not hypertree_verify(pk2, 10, b"test", sig, b"seed-1", d=d, h_prime=h_prime)


def test_wrong_leaf_index_rejected():
    """Verification fails if the leaf index is altered."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)

    sig = hypertree_sign(sk, 10, b"test", SEED, d=d, h_prime=h_prime)
    assert hypertree_verify(pk, 10, b"test", sig, SEED, d=d, h_prime=h_prime)
    assert not hypertree_verify(pk, 11, b"test", sig, SEED, d=d, h_prime=h_prime)
