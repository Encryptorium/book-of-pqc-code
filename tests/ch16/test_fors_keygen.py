"""Tests for FORS key generation."""

import hashlib
from fors_hypertree.fors import fors_keygen, _build_tree, _sha256


def test_keygen_returns_correct_shapes():
    """sk_leaves has k lists of t leaves, each n bytes; pk is n bytes."""
    k, t, n = 6, 16, 32
    seed = b"test-fors-keygen"
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    assert len(sk_leaves) == k
    for j in range(k):
        assert len(sk_leaves[j]) == t
        for leaf in sk_leaves[j]:
            assert len(leaf) == n

    assert len(trees) == k
    for tree in trees:
        assert len(tree) == 2 * t

    assert len(pk) == n


def test_keygen_deterministic():
    """Same seed produces identical keys."""
    seed = b"deterministic-seed"
    sk1, trees1, pk1 = fors_keygen(seed, k=4, t=8, n=32)
    sk2, trees2, pk2 = fors_keygen(seed, k=4, t=8, n=32)

    assert pk1 == pk2
    for j in range(4):
        assert sk1[j] == sk2[j]
        assert trees1[j] == trees2[j]


def test_tree_roots_match_manual_computation():
    """Manually build one tree and verify the root matches."""
    seed = b"manual-root-check"
    k, t, n = 3, 4, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    # Manually build tree 0
    leaves = sk_leaves[0]
    manual_tree = _build_tree(leaves)
    assert manual_tree[1] == trees[0][1]


def test_pk_is_hash_of_roots():
    """pk = SHA-256(root_0 || root_1 || ... || root_{k-1}) truncated to n."""
    seed = b"pk-hash-check"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    roots = b""
    for j in range(k):
        roots += trees[j][1]
    expected_pk = hashlib.sha256(roots).digest()[:n]
    assert pk == expected_pk


def test_different_seeds_different_keys():
    """Different seeds produce different keypairs."""
    _, _, pk1 = fors_keygen(b"seed-a", k=3, t=4, n=32)
    _, _, pk2 = fors_keygen(b"seed-b", k=3, t=4, n=32)
    assert pk1 != pk2
