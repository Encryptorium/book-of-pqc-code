"""Tests for the SHA-3 auxiliary functions (FIPS 203 §4.1).

Covers output lengths and determinism for H, G, PRF, and XOF, plus a
cross-check against the known SHA-3 empty-input digests from the FIPS
202 standard.
"""

import pytest

from mlkem import H, G, PRF, XOF


# FIPS 202 Appendix A test vectors for the empty-string input.
# SHA3-256('') and SHA3-512(''):
SHA3_256_EMPTY = bytes.fromhex(
    "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
)
SHA3_512_EMPTY = bytes.fromhex(
    "a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a6"
    "15b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26"
)


class TestH:
    def test_output_length(self) -> None:
        assert len(H(b"anything")) == 32

    def test_deterministic(self) -> None:
        assert H(b"abc") == H(b"abc")

    def test_distinct_inputs_produce_distinct_outputs(self) -> None:
        assert H(b"a") != H(b"b")

    def test_empty_input_matches_fips_202(self) -> None:
        assert H(b"") == SHA3_256_EMPTY


class TestG:
    def test_output_lengths(self) -> None:
        k, r = G(b"anything")
        assert len(k) == 32
        assert len(r) == 32

    def test_deterministic(self) -> None:
        assert G(b"abc") == G(b"abc")

    def test_halves_concat_is_sha3_512(self) -> None:
        k, r = G(b"")
        assert k + r == SHA3_512_EMPTY

    def test_distinct_inputs_produce_distinct_halves(self) -> None:
        assert G(b"a") != G(b"b")


class TestPRF:
    @pytest.mark.parametrize("eta", [2, 3])
    def test_output_length(self, eta: int) -> None:
        seed = b"\x00" * 32
        out = PRF(eta, seed, nonce=0)
        assert len(out) == 64 * eta

    def test_nonce_acts_as_domain_separator(self) -> None:
        seed = b"\x01" * 32
        a = PRF(2, seed, nonce=0)
        b = PRF(2, seed, nonce=1)
        assert a != b

    def test_seed_acts_as_key(self) -> None:
        a = PRF(2, b"\x00" * 32, nonce=0)
        b = PRF(2, b"\x01" * 32, nonce=0)
        assert a != b

    def test_deterministic(self) -> None:
        seed = b"\x02" * 32
        assert PRF(3, seed, nonce=7) == PRF(3, seed, nonce=7)

    def test_bad_eta_rejected(self) -> None:
        with pytest.raises(AssertionError, match="eta must be 2 or 3"):
            PRF(1, b"\x00" * 32, nonce=0)

    def test_bad_seed_length_rejected(self) -> None:
        with pytest.raises(AssertionError, match="seed must be 32 bytes"):
            PRF(2, b"\x00" * 31, nonce=0)

    def test_bad_nonce_rejected(self) -> None:
        with pytest.raises(AssertionError, match="nonce must be a byte"):
            PRF(2, b"\x00" * 32, nonce=256)


class TestXOF:
    def test_output_length(self) -> None:
        out = XOF(b"\x00" * 34, outlen=168)
        assert len(out) == 168

    def test_deterministic(self) -> None:
        assert XOF(b"abc", outlen=64) == XOF(b"abc", outlen=64)

    def test_distinct_seeds_produce_distinct_outputs(self) -> None:
        a = XOF(b"\x00" * 34, outlen=64)
        b = XOF(b"\x01" * 34, outlen=64)
        assert a != b

    def test_longer_output_extends_shorter(self) -> None:
        short = XOF(b"seed", outlen=64)
        long = XOF(b"seed", outlen=128)
        assert long[:64] == short
