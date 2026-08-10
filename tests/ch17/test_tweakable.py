"""Tests for tweakable hash functions."""

from slh_dsa.adrs import ADRS, WOTS_HASH
from slh_dsa.params import TOY, SLH_DSA_SHAKE_128s
from slh_dsa.tweakable import F, H, T_l, PRF, PRF_msg, H_msg


SEED = b"\x01" * 16
SK_SEED = b"\x02" * 16
SK_PRF = b"\x03" * 16


class TestFFunction:
    def test_output_length(self) -> None:
        a = ADRS()
        a.set_type(WOTS_HASH)
        m = b"\xab" * 16
        out = F(TOY, SEED, a, m)
        assert len(out) == TOY.n

    def test_deterministic(self) -> None:
        a = ADRS()
        a.set_type(WOTS_HASH)
        m = b"\xcd" * 16
        assert F(TOY, SEED, a, m) == F(TOY, SEED, a, m)

    def test_different_adrs_different_output(self) -> None:
        a1 = ADRS()
        a1.set_type(WOTS_HASH)
        a1.set_chain_address(0)
        a2 = ADRS()
        a2.set_type(WOTS_HASH)
        a2.set_chain_address(1)
        m = b"\xef" * 16
        assert F(TOY, SEED, a1, m) != F(TOY, SEED, a2, m)


class TestHFunction:
    def test_output_length(self) -> None:
        a = ADRS()
        m1 = b"\x11" * 16
        m2 = b"\x22" * 16
        out = H(TOY, SEED, a, m1, m2)
        assert len(out) == TOY.n


class TestTlFunction:
    def test_output_length(self) -> None:
        a = ADRS()
        m = b"\xaa" * (TOY.ell * TOY.n)
        out = T_l(TOY, SEED, a, m)
        assert len(out) == TOY.n


class TestPRFFunction:
    def test_output_length(self) -> None:
        a = ADRS()
        out = PRF(TOY, SEED, SK_SEED, a)
        assert len(out) == TOY.n

    def test_different_adrs_different_secret(self) -> None:
        a1 = ADRS()
        a1.set_chain_address(0)
        a2 = ADRS()
        a2.set_chain_address(1)
        assert PRF(TOY, SEED, SK_SEED, a1) != PRF(TOY, SEED, SK_SEED, a2)


class TestPRFMsg:
    def test_output_length(self) -> None:
        opt_rand = b"\x44" * 16
        msg = b"test message"
        out = PRF_msg(TOY, SK_PRF, opt_rand, msg)
        assert len(out) == TOY.n


class TestHMsg:
    def test_output_length(self) -> None:
        r = b"\x55" * 16
        pk_root = b"\x66" * 16
        msg = b"test message"
        out = H_msg(TOY, r, SEED, pk_root, msg)
        assert len(out) == TOY.md_len


class TestSHAKEInstantiation:
    def test_f_shake_output_length(self) -> None:
        a = ADRS()
        a.set_type(WOTS_HASH)
        m = b"\xab" * 16
        out = F(SLH_DSA_SHAKE_128s, SEED, a, m)
        assert len(out) == SLH_DSA_SHAKE_128s.n

    def test_shake_differs_from_sha2(self) -> None:
        a = ADRS()
        a.set_type(WOTS_HASH)
        m = b"\xab" * 16
        sha2_out = F(TOY, SEED, a, m)
        shake_out = F(SLH_DSA_SHAKE_128s, SEED, a, m)
        assert sha2_out != shake_out
