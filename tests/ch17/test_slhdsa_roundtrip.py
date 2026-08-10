"""Tests for full SLH-DSA keygen/sign/verify."""

from slh_dsa.params import TOY
from slh_dsa.slh import slh_keygen, slh_sign, slh_verify, slh_keygen_internal, slh_sign_internal


SK_SEED = b"\x01" * 16
SK_PRF = b"\x02" * 16
PK_SEED = b"\x03" * 16


class TestSLHDSARoundTrip:
    def test_sign_verify(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        msg = b"test message for SLH-DSA"
        sig = slh_sign(TOY, sk, msg, randomize=False)
        assert slh_verify(TOY, pk, msg, sig)

    def test_wrong_message_rejected(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        msg = b"test message for SLH-DSA"
        sig = slh_sign(TOY, sk, msg, randomize=False)
        assert not slh_verify(TOY, pk, b"wrong message", sig)

    def test_wrong_pk_rejected(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        _, pk2 = slh_keygen_internal(TOY, b"\xff" * 16, SK_PRF, PK_SEED)
        msg = b"test message"
        sig = slh_sign(TOY, sk, msg, randomize=False)
        assert not slh_verify(TOY, pk2, msg, sig)

    def test_signature_size(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        msg = b"hello"
        sig = slh_sign(TOY, sk, msg, randomize=False)
        assert len(sig) == TOY.sig_bytes()

    def test_key_sizes(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        assert len(sk) == TOY.sk_bytes()
        assert len(pk) == TOY.pk_bytes()

    def test_deterministic_sign(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        msg = b"deterministic"
        opt_rand = PK_SEED
        sig1 = slh_sign_internal(TOY, sk, msg, opt_rand)
        sig2 = slh_sign_internal(TOY, sk, msg, opt_rand)
        assert sig1 == sig2

    def test_random_keygen_roundtrip(self) -> None:
        sk, pk = slh_keygen(TOY)
        msg = b"random key test"
        sig = slh_sign(TOY, sk, msg, randomize=False)
        assert slh_verify(TOY, pk, msg, sig)

    def test_truncated_signature_rejected(self) -> None:
        sk, pk = slh_keygen_internal(TOY, SK_SEED, SK_PRF, PK_SEED)
        msg = b"test"
        sig = slh_sign(TOY, sk, msg, randomize=False)
        assert not slh_verify(TOY, pk, msg, sig[:-1])
