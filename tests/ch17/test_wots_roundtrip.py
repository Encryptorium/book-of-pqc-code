"""Tests for WOTS+ with ADRS."""

from slh_dsa.adrs import ADRS
from slh_dsa.params import TOY
from slh_dsa.wots import wots_pkgen, wots_sign, wots_pk_from_sig


SK_SEED = b"\x01" * 16
PK_SEED = b"\x02" * 16


def _make_adrs(kp: int = 0) -> ADRS:
    a = ADRS()
    a.set_layer_address(0)
    a.set_tree_address(0)
    a.set_keypair_address(kp)
    return a


class TestWOTSRoundTrip:
    def test_sign_verify_roundtrip(self) -> None:
        adrs = _make_adrs()
        pk = wots_pkgen(TOY, SK_SEED, PK_SEED, adrs)
        msg = b"\xab" * TOY.n
        sig = wots_sign(TOY, SK_SEED, PK_SEED, adrs, msg)
        recovered_pk = wots_pk_from_sig(TOY, PK_SEED, adrs, sig, msg)
        assert recovered_pk == pk

    def test_wrong_message_rejected(self) -> None:
        adrs = _make_adrs()
        pk = wots_pkgen(TOY, SK_SEED, PK_SEED, adrs)
        msg = b"\xab" * TOY.n
        sig = wots_sign(TOY, SK_SEED, PK_SEED, adrs, msg)
        wrong_msg = b"\xcd" * TOY.n
        recovered_pk = wots_pk_from_sig(TOY, PK_SEED, adrs, sig, wrong_msg)
        assert recovered_pk != pk

    def test_signature_length(self) -> None:
        adrs = _make_adrs()
        msg = b"\xab" * TOY.n
        sig = wots_sign(TOY, SK_SEED, PK_SEED, adrs, msg)
        assert len(sig) == TOY.ell * TOY.n

    def test_pk_length(self) -> None:
        adrs = _make_adrs()
        pk = wots_pkgen(TOY, SK_SEED, PK_SEED, adrs)
        assert len(pk) == TOY.n

    def test_different_keypair_different_pk(self) -> None:
        pk0 = wots_pkgen(TOY, SK_SEED, PK_SEED, _make_adrs(0))
        pk1 = wots_pkgen(TOY, SK_SEED, PK_SEED, _make_adrs(1))
        assert pk0 != pk1

    def test_deterministic(self) -> None:
        adrs = _make_adrs()
        pk1 = wots_pkgen(TOY, SK_SEED, PK_SEED, adrs)
        pk2 = wots_pkgen(TOY, SK_SEED, PK_SEED, adrs)
        assert pk1 == pk2
