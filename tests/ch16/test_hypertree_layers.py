"""Tests for hypertree layer structure and correctness."""

from fors_hypertree.hypertree import (
    hypertree_keygen,
    hypertree_sign,
    hypertree_verify,
    _wots_verify,
    _ltree,
    _sha256,
    _verify_path,
)


SEED = b"hypertree-layer-test"


def test_layer_count_matches_d():
    """Signature has exactly d layers."""
    for d in [1, 2, 3]:
        h_prime = 3
        sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)
        sig = hypertree_sign(sk, 0, b"test", SEED, d=d, h_prime=h_prime)
        assert len(sig) == d, f"Expected {d} layers, got {len(sig)}"


def test_bottom_layer_signs_message():
    """The bottom WOTS+ signature verifies against the original message."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)

    message = b"bottom layer test"
    leaf_index = 5
    sig = hypertree_sign(sk, leaf_index, message, SEED, d=d, h_prime=h_prime)

    wots_sig, wots_pk, path = sig[0]
    within_subtree = leaf_index & ((1 << h_prime) - 1)
    subtree_pos = leaf_index >> h_prime

    subtree_seed = _sha256(
        SEED + b"ht" + (0).to_bytes(4, "big") + subtree_pos.to_bytes(4, "big")
    )
    leaf_seed = subtree_seed + b"leaf" + within_subtree.to_bytes(4, "big")

    assert _wots_verify(wots_pk, message, wots_sig, leaf_seed)


def test_upper_layer_signs_subtree_root():
    """Each layer j > 0 signs the root of the layer-(j-1) subtree."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)

    leaf_index = 20
    message = b"upper layer test"
    sig = hypertree_sign(sk, leaf_index, message, SEED, d=d, h_prime=h_prime)

    # Reconstruct layer 0 subtree root
    wots_sig_0, wots_pk_0, path_0 = sig[0]
    within_0 = leaf_index & ((1 << h_prime) - 1)
    subtree_pos_0 = leaf_index >> h_prime

    subtree_seed_0 = _sha256(
        SEED + b"ht" + (0).to_bytes(4, "big") + subtree_pos_0.to_bytes(4, "big")
    )
    leaf_seed_0 = subtree_seed_0 + b"leaf" + within_0.to_bytes(4, "big")

    leaf_hash_0 = _ltree(wots_pk_0, leaf_seed_0)
    # Walk the auth path to get the root
    current = leaf_hash_0
    idx = within_0
    for sibling in path_0:
        if idx % 2 == 0:
            current = _sha256(current + sibling)
        else:
            current = _sha256(sibling + current)
        idx //= 2
    subtree_root_0 = current

    # Layer 1 should sign this root
    wots_sig_1, wots_pk_1, path_1 = sig[1]
    within_1 = subtree_pos_0 & ((1 << h_prime) - 1)
    subtree_pos_1 = subtree_pos_0 >> h_prime

    subtree_seed_1 = _sha256(
        SEED + b"ht" + (1).to_bytes(4, "big") + subtree_pos_1.to_bytes(4, "big")
    )
    leaf_seed_1 = subtree_seed_1 + b"leaf" + within_1.to_bytes(4, "big")

    assert _wots_verify(wots_pk_1, subtree_root_0, wots_sig_1, leaf_seed_1)


def test_top_root_matches_pk():
    """The root reconstructed from the top layer's auth path matches pk."""
    d, h_prime = 2, 4
    sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)

    leaf_index = 100
    message = b"top root test"
    sig = hypertree_sign(sk, leaf_index, message, SEED, d=d, h_prime=h_prime)

    # Full verification should succeed
    assert hypertree_verify(pk, leaf_index, message, sig, SEED, d=d, h_prime=h_prime)


def test_different_d_values():
    """Test with d=1 (flat, XMSS-like) and d=3 for generality."""
    for d in [1, 3]:
        h_prime = 3
        sk, pk = hypertree_keygen(SEED, d=d, h_prime=h_prime)
        max_leaf = (1 << (d * h_prime)) - 1
        for leaf_idx in [0, max_leaf // 2, max_leaf]:
            msg = f"d={d}-leaf={leaf_idx}".encode()
            sig = hypertree_sign(sk, leaf_idx, msg, SEED, d=d, h_prime=h_prime)
            assert hypertree_verify(
                pk, leaf_idx, msg, sig, SEED, d=d, h_prime=h_prime
            ), f"Failed at d={d}, leaf={leaf_idx}"
