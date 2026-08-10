"""Tests for Merkle tree construction and root computation."""

import hashlib

from lamport_merkle.merkle import build_tree, root


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _make_leaves(n: int) -> list[bytes]:
    return [_sha256(i.to_bytes(4, "big")) for i in range(n)]


def test_tree_size_is_double_leaves():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    assert len(tree) == 16  # 2 * 8


def test_root_is_sha256_of_children():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    expected_root = _sha256(tree[2] + tree[3])
    assert root(tree) == expected_root


def test_internal_nodes_are_sha256_of_children():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    for i in range(1, 8):  # Internal nodes 1..7
        assert tree[i] == _sha256(tree[2 * i] + tree[2 * i + 1])


def test_deterministic_root():
    leaves = _make_leaves(8)
    tree1 = build_tree(leaves)
    tree2 = build_tree(leaves)
    assert root(tree1) == root(tree2)


def test_different_leaves_different_root():
    leaves_a = _make_leaves(8)
    leaves_b = [_sha256((i + 100).to_bytes(4, "big")) for i in range(8)]
    assert root(build_tree(leaves_a)) != root(build_tree(leaves_b))


def test_single_leaf_tree():
    leaves = _make_leaves(1)
    tree = build_tree(leaves)
    assert len(tree) == 2
    assert root(tree) == leaves[0]


def test_rejects_non_power_of_two():
    import pytest

    with pytest.raises(ValueError):
        build_tree(_make_leaves(3))
