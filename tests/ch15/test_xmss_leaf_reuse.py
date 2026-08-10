"""Tests for XMSS leaf exhaustion and the backup hazard."""

import pytest

from wots_xmss.xmss import xmss_keygen, xmss_sign, xmss_verify


SK_SEED = b"xmss-leaf-reuse-seed-sk"
PK_SEED = b"xmss-leaf-reuse-seed-pk"
D = 2  # 4 leaves, minimal for exhaustion tests.


def test_leaf_exhaustion():
    """Signing after all leaves are used raises RuntimeError."""
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)
    for i in range(4):
        xmss_sign(all_sk, all_pk, tree, state, f"msg-{i}".encode(), PK_SEED)

    with pytest.raises(RuntimeError, match="leaf exhaustion"):
        xmss_sign(all_sk, all_pk, tree, state, b"one-too-many", PK_SEED)


def test_backup_hazard_same_leaf():
    """Copying state before signing produces two signatures at the same leaf.

    This demonstrates the backup hazard from Chapter 6 Exercise 4:
    a backup freezes the counter, and both copies sign with the same
    leaf index.
    """
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)

    # Sign once to advance to leaf 1.
    xmss_sign(all_sk, all_pk, tree, state, b"warmup", PK_SEED)
    assert state["next_leaf"] == 1

    # Simulate a backup by copying the state.
    state_backup = dict(state)

    # Original signs a message.
    sig1, pk1, path1, idx1 = xmss_sign(
        all_sk, all_pk, tree, state, b"message-A", PK_SEED
    )

    # Backup signs a different message (same leaf index!).
    sig2, pk2, path2, idx2 = xmss_sign(
        all_sk, all_pk, tree, state_backup, b"message-B", PK_SEED
    )

    # Both used leaf index 1.
    assert idx1 == idx2 == 1

    # Both signatures verify individually.
    assert xmss_verify(root_hash, b"message-A", sig1, pk1, path1, idx1, PK_SEED)
    assert xmss_verify(root_hash, b"message-B", sig2, pk2, path2, idx2, PK_SEED)

    # The WOTS+ key at leaf 1 has now been used twice, degrading its
    # one-time security.  The two WOTS+ signatures on different messages
    # leak intermediate chain values that an adversary can exploit.
    # (The full forgery walk is in the chapter prose and in
    # test_wots_checksum_forgery.py.)
