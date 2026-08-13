"""Tests for the L2 Merkle commitment module of Chapter 31."""

import pytest

from zk_layers.merkle import (
    LEAF_TAG,
    NODE_TAG,
    commit,
    hash_leaf,
    hash_node,
    open_path,
    verify_path,
)

LEAVES = [b"x0", b"x1", b"x2", b"x3"]


@pytest.mark.parametrize("index", [0, 1, 2, 3])
def test_every_leaf_opens_against_the_root(index):
    root = commit(LEAVES)
    path = open_path(LEAVES, index)
    assert verify_path(LEAVES[index], index, path, root) is True


def test_an_opening_proof_is_one_sibling_per_level():
    assert len(open_path(LEAVES, 2)) == 2
    assert len(open_path([b"a", b"b"], 0)) == 1


def test_a_substituted_leaf_fails_against_the_root():
    root = commit(LEAVES)
    path = open_path(LEAVES, 2)
    assert verify_path(b"forged", 2, path, root) is False


def test_a_leafs_own_path_does_not_verify_at_another_index():
    root = commit(LEAVES)
    path = open_path(LEAVES, 2)
    # Leaf 2 sits on the left of its sibling; leaf 3 sits on the right.
    # Replaying leaf 2's path for leaf 3's value recomputes a different
    # root, so the check fails.
    assert verify_path(LEAVES[3], 3, path, root) is False


def test_a_single_leaf_commits_to_its_own_leaf_digest():
    assert commit([b"only"]) == hash_leaf(b"only")


@pytest.mark.parametrize("count", [0, 3, 5, 6])
def test_a_leaf_count_that_is_not_a_power_of_two_is_rejected(count):
    with pytest.raises(ValueError, match="nonempty power of two"):
        commit([b"x"] * count)


def test_the_two_domain_tags_differ():
    assert LEAF_TAG != NODE_TAG


def test_an_internal_node_cannot_be_presented_as_a_leaf():
    """The attack domain separation exists to stop.

    Concatenate the two leaf digests of a two-leaf tree and offer the
    result as a single leaf. Without domain separation the one-leaf tree
    and the two-leaf tree hash to the same root, so a prover can claim
    either depth for one commitment. Tagging the leaf and internal cases
    apart makes the two roots different values.

    This is the test the block printed in Chapter 31 does not pass, which
    is why the printed block says production trees domain-separate and
    this module does it.
    """
    two_leaf_root = commit([b"x0", b"x1"])
    forged_leaf = hash_leaf(b"x0") + hash_leaf(b"x1")
    assert commit([forged_leaf]) != two_leaf_root


def test_leaf_and_node_hashing_disagree_on_the_same_bytes():
    left, right = hash_leaf(b"x0"), hash_leaf(b"x1")
    assert hash_leaf(left + right) != hash_node(left, right)


def test_hash_node_is_not_symmetric_in_its_arguments():
    left, right = hash_leaf(b"x0"), hash_leaf(b"x1")
    assert hash_node(left, right) != hash_node(right, left)
