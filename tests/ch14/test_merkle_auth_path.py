"""Tests for Merkle tree authentication paths."""

import hashlib

from lamport_merkle.merkle import auth_path, build_tree, root, verify_path


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _make_leaves(n: int) -> list[bytes]:
    return [_sha256(i.to_bytes(4, "big")) for i in range(n)]


def test_auth_path_length_equals_depth():
    for depth in (1, 2, 3, 5):
        leaves = _make_leaves(1 << depth)
        tree = build_tree(leaves)
        path = auth_path(tree, 0)
        assert len(path) == depth


def test_verify_path_roundtrip_all_leaves_d3():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    r = root(tree)
    for i in range(8):
        path = auth_path(tree, i)
        assert verify_path(leaves[i], i, path, r)


def test_verify_path_roundtrip_d5():
    leaves = _make_leaves(32)
    tree = build_tree(leaves)
    r = root(tree)
    for i in range(32):
        path = auth_path(tree, i)
        assert verify_path(leaves[i], i, path, r)


def test_verify_path_roundtrip_d10():
    leaves = _make_leaves(1024)
    tree = build_tree(leaves)
    r = root(tree)
    # Spot-check a few leaves instead of all 1024.
    for i in [0, 1, 511, 512, 1023]:
        path = auth_path(tree, i)
        assert verify_path(leaves[i], i, path, r)


def test_verify_path_rejects_wrong_leaf():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    r = root(tree)
    path = auth_path(tree, 3)
    wrong_leaf = _sha256(b"wrong")
    assert not verify_path(wrong_leaf, 3, path, r)


def test_verify_path_rejects_wrong_root():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    path = auth_path(tree, 3)
    wrong_root = _sha256(b"wrong root")
    assert not verify_path(leaves[3], 3, path, wrong_root)


def test_verify_path_rejects_wrong_index():
    leaves = _make_leaves(8)
    tree = build_tree(leaves)
    r = root(tree)
    path = auth_path(tree, 3)
    # Use leaf 3's path but claim it is leaf 4.
    assert not verify_path(leaves[3], 4, path, r)
