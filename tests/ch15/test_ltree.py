"""Tests for L-tree compression of WOTS+ public keys."""

import hashlib

from wots_xmss.ltree import ltree


SEED = b"ltree-test-seed"


def _make_values(count: int) -> list[bytes]:
    """Generate *count* deterministic 32-byte values."""
    return [
        hashlib.sha256(SEED + i.to_bytes(4, "big")).digest()
        for i in range(count)
    ]


def test_ltree_power_of_two():
    """L-tree of 4 values produces a single 32-byte root."""
    values = _make_values(4)
    root = ltree(values, SEED)
    assert len(root) == 32


def _node(level: int, pair_index: int, left: bytes, right: bytes) -> bytes:
    """One L-tree interior node, written out independently of the module."""
    return hashlib.sha256(
        SEED
        + level.to_bytes(4, "big")
        + pair_index.to_bytes(4, "big")
        + left
        + right
    ).digest()


def test_ltree_odd_count_3_promotes_rather_than_drops():
    """Three leaves: the unpaired third is carried up, not discarded.

    A length check cannot see this. An implementation that DROPS the
    unpaired node at every level still returns 32 bytes and still passes
    the length, determinism, seed-separation, single-value and two-value
    checks in this file, so the expected root is constructed here by
    hand: pair (0, 1) at level 0, promote leaf 2, then pair the two
    survivors at level 1. That mutant fails this test and the five-leaf
    one below; the other six pass.
    """
    v = _make_values(3)
    level0 = _node(0, 0, v[0], v[1])
    expected = _node(1, 0, level0, v[2])
    assert ltree(v, SEED) == expected
    # The promoted leaf is load-bearing: dropping it gives a different root.
    assert ltree(v, SEED) != ltree(v[:2], SEED)


def test_ltree_odd_count_5_promotes_at_the_first_level():
    """Five leaves: promotion at level 0, then again at level 1.

    Level 0 pairs (0,1) and (2,3) and promotes leaf 4. Level 1 pairs the
    two nodes and promotes leaf 4 again. Level 2 pairs those two.
    """
    v = _make_values(5)
    a = _node(0, 0, v[0], v[1])
    b = _node(0, 1, v[2], v[3])
    c = _node(1, 0, a, b)
    expected = _node(2, 0, c, v[4])
    assert ltree(v, SEED) == expected
    assert ltree(v, SEED) != ltree(v[:4], SEED)


def test_ltree_67_values():
    """L-tree of 67 values (the WOTS+ ell at w=16, n=32)."""
    values = _make_values(67)
    root = ltree(values, SEED)
    assert len(root) == 32


def test_ltree_deterministic():
    """Same inputs produce the same root."""
    values = _make_values(67)
    r1 = ltree(values, SEED)
    r2 = ltree(values, SEED)
    assert r1 == r2


def test_ltree_different_seed():
    """Different seeds produce different roots."""
    values = _make_values(67)
    r1 = ltree(values, b"seed-a")
    r2 = ltree(values, b"seed-b")
    assert r1 != r2


def test_ltree_single_value():
    """L-tree of 1 value returns that value unchanged."""
    values = _make_values(1)
    root = ltree(values, SEED)
    assert root == values[0]


def test_ltree_two_values():
    """L-tree of 2 values is a single hash of the pair."""
    values = _make_values(2)
    root = ltree(values, SEED)
    expected = hashlib.sha256(
        SEED
        + (0).to_bytes(4, "big")
        + (0).to_bytes(4, "big")
        + values[0]
        + values[1]
    ).digest()
    assert root == expected
