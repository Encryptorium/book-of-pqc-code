"""Tests for XMSS sign/verify round-trip at d=3."""

from wots_xmss.xmss import xmss_keygen, xmss_sign, xmss_verify


SK_SEED = b"xmss-roundtrip-seed-sk"
PK_SEED = b"xmss-roundtrip-seed-pk"
D = 3  # 8 leaves, fast enough for tests.


def test_sign_verify_first_leaf():
    """Sign and verify with the first leaf."""
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)
    message = b"first message"
    wots_sig, wots_pk, path, leaf_idx = xmss_sign(
        all_sk, all_pk, tree, state, message, PK_SEED
    )
    assert leaf_idx == 0
    assert xmss_verify(root_hash, message, wots_sig, wots_pk, path, leaf_idx, PK_SEED)


def test_sign_verify_multiple_leaves():
    """Sign and verify across several leaves."""
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)
    for i in range(4):
        msg = f"message-{i}".encode()
        wots_sig, wots_pk, path, leaf_idx = xmss_sign(
            all_sk, all_pk, tree, state, msg, PK_SEED
        )
        assert leaf_idx == i
        assert xmss_verify(
            root_hash, msg, wots_sig, wots_pk, path, leaf_idx, PK_SEED
        )


def test_wrong_message_rejected():
    """Verification fails on a different message."""
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)
    wots_sig, wots_pk, path, leaf_idx = xmss_sign(
        all_sk, all_pk, tree, state, b"correct", PK_SEED
    )
    assert not xmss_verify(
        root_hash, b"wrong", wots_sig, wots_pk, path, leaf_idx, PK_SEED
    )


def test_wrong_root_rejected():
    """Verification fails against a different root."""
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)
    wots_sig, wots_pk, path, leaf_idx = xmss_sign(
        all_sk, all_pk, tree, state, b"test", PK_SEED
    )
    fake_root = b"\x00" * 32
    assert not xmss_verify(
        fake_root, b"test", wots_sig, wots_pk, path, leaf_idx, PK_SEED
    )


def test_state_increments():
    """Signing increments the next_leaf counter."""
    all_sk, all_pk, tree, root_hash, state = xmss_keygen(d=D, sk_seed=SK_SEED, pk_seed=PK_SEED)
    assert state["next_leaf"] == 0
    xmss_sign(all_sk, all_pk, tree, state, b"msg-0", PK_SEED)
    assert state["next_leaf"] == 1
    xmss_sign(all_sk, all_pk, tree, state, b"msg-1", PK_SEED)
    assert state["next_leaf"] == 2
