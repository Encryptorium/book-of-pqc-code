"""Tests for hypertree with ADRS."""

from slh_dsa.adrs import ADRS
from slh_dsa.params import TOY
from slh_dsa.hypertree import ht_sign, ht_verify, xmss_node


SK_SEED = b"\x01" * 16
PK_SEED = b"\x02" * 16


def _compute_pk_root() -> bytes:
    """Compute the top-layer XMSS tree root (the public key root)."""
    adrs = ADRS()
    adrs.set_layer_address(TOY.d - 1)
    return xmss_node(TOY, SK_SEED, 0, TOY.hp, PK_SEED, adrs)


class TestHypertreeRoundTrip:
    def test_sign_verify_leaf_0(self) -> None:
        pk_root = _compute_pk_root()
        msg = b"\xab" * TOY.n
        sig = ht_sign(TOY, SK_SEED, PK_SEED, msg, idx_tree=0, idx_leaf=0)
        assert ht_verify(TOY, PK_SEED, pk_root, msg, sig, idx_tree=0, idx_leaf=0)

    def test_sign_verify_nonzero_leaf(self) -> None:
        pk_root = _compute_pk_root()
        msg = b"\xcd" * TOY.n
        sig = ht_sign(TOY, SK_SEED, PK_SEED, msg, idx_tree=0, idx_leaf=3)
        assert ht_verify(TOY, PK_SEED, pk_root, msg, sig, idx_tree=0, idx_leaf=3)

    def test_sign_verify_nonzero_tree(self) -> None:
        pk_root = _compute_pk_root()
        msg = b"\xef" * TOY.n
        sig = ht_sign(TOY, SK_SEED, PK_SEED, msg, idx_tree=1, idx_leaf=2)
        assert ht_verify(TOY, PK_SEED, pk_root, msg, sig, idx_tree=1, idx_leaf=2)

    def test_wrong_message_rejected(self) -> None:
        pk_root = _compute_pk_root()
        msg = b"\xab" * TOY.n
        sig = ht_sign(TOY, SK_SEED, PK_SEED, msg, idx_tree=0, idx_leaf=0)
        wrong_msg = b"\xba" * TOY.n
        assert not ht_verify(TOY, PK_SEED, pk_root, wrong_msg, sig, idx_tree=0, idx_leaf=0)

    def test_wrong_tree_index_rejected(self) -> None:
        pk_root = _compute_pk_root()
        msg = b"\xab" * TOY.n
        sig = ht_sign(TOY, SK_SEED, PK_SEED, msg, idx_tree=0, idx_leaf=0)
        assert not ht_verify(TOY, PK_SEED, pk_root, msg, sig, idx_tree=1, idx_leaf=0)

    def test_signature_length(self) -> None:
        msg = b"\xab" * TOY.n
        sig = ht_sign(TOY, SK_SEED, PK_SEED, msg, idx_tree=0, idx_leaf=0)
        expected = TOY.d * (TOY.ell + TOY.hp) * TOY.n
        assert len(sig) == expected
