"""Tests for ``commitment_schemes.merkle``."""

import hashlib

import pytest

from commitment_schemes import merkle


def test_hash_width_support() -> None:
    for w in merkle.SUPPORTED_WIDTHS:
        digest = merkle.hash_bytes(b"hello", w)
        assert len(digest) == w // 8
    with pytest.raises(ValueError):
        merkle.hash_bytes(b"hello", 100)


def test_commit_open_verify_binary_roundtrip() -> None:
    leaves = [f"leaf-{i}".encode() for i in range(8)]
    commit = merkle.commit_leaves(leaves, arity=2, width_bits=256)
    assert commit.num_leaves == 8
    assert len(commit.root) == 32

    for i, leaf in enumerate(leaves):
        opening = merkle.open_at(commit, i, leaf)
        assert merkle.verify(commit.root, opening, arity=2, width_bits=256)


def test_commit_open_verify_quaternary_roundtrip() -> None:
    leaves = [f"leaf-{i}".encode() for i in range(13)]
    commit = merkle.commit_leaves(leaves, arity=4, width_bits=256)
    # 13 leaves round up to 16 = 4^2
    assert len(commit.levels[0]) == 16
    assert len(commit.root) == 32

    for i, leaf in enumerate(leaves):
        opening = merkle.open_at(commit, i, leaf)
        assert merkle.verify(commit.root, opening, arity=4, width_bits=256)


def test_tampered_leaf_value_rejected() -> None:
    leaves = [f"leaf-{i}".encode() for i in range(8)]
    commit = merkle.commit_leaves(leaves, arity=2, width_bits=256)
    opening = merkle.open_at(commit, 3, leaves[3])

    tampered = merkle.MerkleOpening(
        leaf_index=opening.leaf_index,
        leaf_value=b"tampered",
        siblings=opening.siblings,
    )
    assert not merkle.verify(commit.root, tampered, arity=2, width_bits=256)


def test_tampered_sibling_rejected() -> None:
    leaves = [f"leaf-{i}".encode() for i in range(8)]
    commit = merkle.commit_leaves(leaves, arity=2, width_bits=256)
    opening = merkle.open_at(commit, 3, leaves[3])

    # Flip one byte in the first-level sibling.
    flipped_sibling = bytes([opening.siblings[0][0][0] ^ 0xFF]) + opening.siblings[0][0][1:]
    tampered = merkle.MerkleOpening(
        leaf_index=opening.leaf_index,
        leaf_value=opening.leaf_value,
        siblings=[[flipped_sibling]] + opening.siblings[1:],
    )
    assert not merkle.verify(commit.root, tampered, arity=2, width_bits=256)


def test_configurable_width_384() -> None:
    leaves = [f"leaf-{i}".encode() for i in range(4)]
    commit = merkle.commit_leaves(leaves, arity=2, width_bits=384)
    assert len(commit.root) == 48
    opening = merkle.open_at(commit, 2, leaves[2])
    assert merkle.verify(commit.root, opening, arity=2, width_bits=384)


def test_bht_cnps_bit_helpers() -> None:
    # The canonical table Chapter 32 cites:
    # n = 256: BHT 85, CNPS 102
    # n = 384: BHT 128, CNPS 153
    # n = 512: BHT 170, CNPS 204
    assert merkle.quantum_collision_bits_bht(256) == 85
    assert merkle.quantum_collision_bits_cnps(256) == 102
    assert merkle.quantum_collision_bits_bht(384) == 128
    assert merkle.quantum_collision_bits_cnps(384) == 153
    assert merkle.quantum_collision_bits_bht(512) == 170
    assert merkle.quantum_collision_bits_cnps(512) == 204


def test_commit_rejects_empty_leaves() -> None:
    with pytest.raises(ValueError):
        merkle.commit_leaves([], arity=2, width_bits=256)


def test_commit_rejects_arity_below_two() -> None:
    with pytest.raises(ValueError):
        merkle.commit_leaves([b"x"], arity=1, width_bits=256)


def test_open_at_rejects_out_of_range() -> None:
    leaves = [b"a", b"b"]
    commit = merkle.commit_leaves(leaves, arity=2, width_bits=256)
    with pytest.raises(ValueError):
        merkle.open_at(commit, 5, b"a")


def test_open_at_rejects_mismatched_leaf() -> None:
    leaves = [b"a", b"b"]
    commit = merkle.commit_leaves(leaves, arity=2, width_bits=256)
    with pytest.raises(ValueError):
        merkle.open_at(commit, 0, b"wrong")


def test_hash_bytes_uses_the_primitive_each_width_claims() -> None:
    """Pin the width-to-primitive dispatch, not just the digest length.

    ``hash_bytes`` exists to route 384- and 512-bit widths through
    SHAKE-256, because SHAKE-128's collision-resistance strength caps at
    128 bits however many output bytes it is asked for (FIPS 202
    Appendix A.1). Routing 384 bits through SHAKE-128 would still return
    48 bytes, so every length assertion in this file passes while
    ``quantum_collision_bits_bht(384)`` goes on reporting a 128-bit
    margin the digest does not deliver. This test is what makes that
    substitution fail.
    """
    data = b"width-dispatch"
    assert merkle.hash_bytes(data, 256) == hashlib.sha256(data).digest()
    for narrow in (128, 192):
        assert merkle.hash_bytes(data, narrow) == hashlib.shake_128(data).digest(narrow // 8)
    for wide in (384, 512):
        octets = wide // 8
        assert merkle.hash_bytes(data, wide) == hashlib.shake_256(data).digest(octets)
        assert merkle.hash_bytes(data, wide) != hashlib.shake_128(data).digest(octets)
