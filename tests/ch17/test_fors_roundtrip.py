"""Tests for FORS with ADRS."""

from slh_dsa.adrs import ADRS
from slh_dsa.params import TOY
from slh_dsa.fors import fors_sign, fors_pk_from_sig, _fors_node


SK_SEED = b"\x01" * 16
PK_SEED = b"\x02" * 16


def _make_adrs() -> ADRS:
    a = ADRS()
    a.set_layer_address(0)
    a.set_tree_address(0)
    a.set_keypair_address(0)
    return a


def _compute_fors_pk(params, sk_seed, pk_seed, adrs) -> bytes:
    """Compute the FORS public key by building all k trees."""
    from slh_dsa.adrs import FORS_ROOTS
    from slh_dsa.tweakable import T_l
    k, a, t = params.k, params.a, params.t
    roots = b""
    for j in range(k):
        roots += _fors_node(params, sk_seed, pk_seed, adrs, j, a)
    pk_adrs = adrs.copy()
    pk_adrs.set_type(FORS_ROOTS)
    pk_adrs.set_keypair_address(adrs.get_keypair_address())
    return T_l(params, pk_seed, pk_adrs, roots)


class TestFORSRoundTrip:
    def test_sign_verify_roundtrip(self) -> None:
        adrs = _make_adrs()
        pk = _compute_fors_pk(TOY, SK_SEED, PK_SEED, adrs)
        # TOY: k=3, a=3, so we need ceil(3*3/8) = 2 bytes for md
        md = b"\x5a\x00"
        sig = fors_sign(TOY, SK_SEED, PK_SEED, adrs, md)
        recovered_pk = fors_pk_from_sig(TOY, PK_SEED, adrs, sig, md)
        assert recovered_pk == pk

    def test_wrong_digest_rejected(self) -> None:
        adrs = _make_adrs()
        pk = _compute_fors_pk(TOY, SK_SEED, PK_SEED, adrs)
        md = b"\x5a\x00"
        sig = fors_sign(TOY, SK_SEED, PK_SEED, adrs, md)
        wrong_md = b"\xa5\x00"
        recovered_pk = fors_pk_from_sig(TOY, PK_SEED, adrs, sig, wrong_md)
        assert recovered_pk != pk

    def test_signature_length(self) -> None:
        adrs = _make_adrs()
        md = b"\x5a\x00"
        sig = fors_sign(TOY, SK_SEED, PK_SEED, adrs, md)
        expected = TOY.k * (1 + TOY.a) * TOY.n
        assert len(sig) == expected

    def test_deterministic(self) -> None:
        adrs = _make_adrs()
        md = b"\x5a\x00"
        sig1 = fors_sign(TOY, SK_SEED, PK_SEED, adrs, md)
        sig2 = fors_sign(TOY, SK_SEED, PK_SEED, adrs, md)
        assert sig1 == sig2
