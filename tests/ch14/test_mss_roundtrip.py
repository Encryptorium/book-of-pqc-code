"""Tests for the Merkle signature scheme (Lamport + Merkle tree)."""

from lamport_merkle.mss import mss_keygen, mss_sign, mss_verify


MSS_SEED = b"ch14-mss-test"


def test_mss_sign_verify_all_leaves_d3():
    all_sk, all_pk, tree, root_hash = mss_keygen(d=3, rng_seed=MSS_SEED)
    for i in range(8):
        msg = f"message-{i}".encode()
        lsig, lpk, path = mss_sign(all_sk, all_pk, tree, i, msg)
        assert mss_verify(root_hash, msg, lsig, lpk, path, i)


def test_mss_verify_rejects_wrong_message():
    all_sk, all_pk, tree, root_hash = mss_keygen(d=3, rng_seed=MSS_SEED)
    lsig, lpk, path = mss_sign(all_sk, all_pk, tree, 0, b"original")
    assert not mss_verify(root_hash, b"tampered", lsig, lpk, path, 0)


def test_mss_verify_rejects_wrong_root():
    all_sk, all_pk, tree, root_hash = mss_keygen(d=3, rng_seed=MSS_SEED)
    lsig, lpk, path = mss_sign(all_sk, all_pk, tree, 0, b"msg")
    wrong_root = b"\x00" * 32
    assert not mss_verify(wrong_root, b"msg", lsig, lpk, path, 0)


def test_mss_verify_rejects_cross_leaf_auth_path():
    """Sign with leaf 0 but present the auth path for leaf 1."""
    all_sk, all_pk, tree, root_hash = mss_keygen(d=3, rng_seed=MSS_SEED)
    msg = b"cross-leaf"
    lsig0, lpk0, path0 = mss_sign(all_sk, all_pk, tree, 0, msg)
    _, _, path1 = mss_sign(all_sk, all_pk, tree, 1, msg)
    # Use leaf 0's Lamport sig but leaf 1's auth path.
    assert not mss_verify(root_hash, msg, lsig0, lpk0, path1, 1)


def test_mss_deterministic_root():
    _, _, _, root1 = mss_keygen(d=3, rng_seed=MSS_SEED)
    _, _, _, root2 = mss_keygen(d=3, rng_seed=MSS_SEED)
    assert root1 == root2


def test_mss_different_seeds_different_roots():
    _, _, _, root1 = mss_keygen(d=3, rng_seed=b"seed-a")
    _, _, _, root2 = mss_keygen(d=3, rng_seed=b"seed-b")
    assert root1 != root2
