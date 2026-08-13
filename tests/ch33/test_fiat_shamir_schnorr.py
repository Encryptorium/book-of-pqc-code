"""Tests for ``fiat_shamir_qrom.fiat_shamir``."""

import pytest

from fiat_shamir_qrom import fiat_shamir, rom_simulator


def test_keygen_explicit_witness_and_pk_consistency() -> None:
    kp = fiat_shamir.keygen(sk=7)
    assert kp.sk == 7
    assert kp.pk == pow(
        fiat_shamir.DEFAULT_GENERATOR,
        7,
        fiat_shamir.DEFAULT_PRIME,
    )


def test_keygen_rejects_bad_witness() -> None:
    with pytest.raises(ValueError):
        fiat_shamir.keygen(sk=0)
    with pytest.raises(ValueError):
        fiat_shamir.keygen(sk=fiat_shamir.DEFAULT_ORDER)
    with pytest.raises(ValueError):
        fiat_shamir.keygen(sk=-1)


def test_keygen_random_is_in_range() -> None:
    kp = fiat_shamir.keygen()
    assert 1 <= kp.sk < fiat_shamir.DEFAULT_ORDER
    assert 1 <= kp.pk < fiat_shamir.DEFAULT_PRIME


def test_interactive_roundtrip_accepts() -> None:
    kp = fiat_shamir.keygen(sk=123)
    transcript = fiat_shamir.interactive_prove(kp, challenge=456, nonce=789)
    assert fiat_shamir.interactive_verify(kp.pk, transcript)


def test_interactive_prove_rejects_bad_inputs() -> None:
    kp = fiat_shamir.keygen(sk=123)
    with pytest.raises(ValueError):
        fiat_shamir.interactive_prove(kp, challenge=-1)
    with pytest.raises(ValueError):
        fiat_shamir.interactive_prove(kp, challenge=fiat_shamir.DEFAULT_ORDER)
    with pytest.raises(ValueError):
        fiat_shamir.interactive_prove(kp, challenge=5, nonce=0)
    with pytest.raises(ValueError):
        fiat_shamir.interactive_prove(
            kp, challenge=5, nonce=fiat_shamir.DEFAULT_ORDER
        )


def test_interactive_verify_rejects_tampered_transcript() -> None:
    kp = fiat_shamir.keygen(sk=123)
    good = fiat_shamir.interactive_prove(kp, challenge=456, nonce=789)
    tampered = fiat_shamir.InteractiveTranscript(
        commitment=good.commitment,
        challenge=good.challenge,
        response=(good.response + 1) % fiat_shamir.DEFAULT_ORDER,
    )
    assert not fiat_shamir.interactive_verify(kp.pk, tampered)


def test_interactive_verify_rejects_wrong_commitment() -> None:
    kp = fiat_shamir.keygen(sk=123)
    good = fiat_shamir.interactive_prove(kp, challenge=456, nonce=789)
    tampered = fiat_shamir.InteractiveTranscript(
        commitment=(good.commitment * 2) % fiat_shamir.DEFAULT_PRIME,
        challenge=good.challenge,
        response=good.response,
    )
    assert not fiat_shamir.interactive_verify(kp.pk, tampered)


def test_interactive_verify_rejects_bad_pk() -> None:
    kp = fiat_shamir.keygen(sk=123)
    good = fiat_shamir.interactive_prove(kp, challenge=456, nonce=789)
    with pytest.raises(ValueError):
        fiat_shamir.interactive_verify(0, good)
    with pytest.raises(ValueError):
        fiat_shamir.interactive_verify(fiat_shamir.DEFAULT_PRIME, good)


def test_interactive_verify_rejects_wrong_witness_public_key() -> None:
    kp_real = fiat_shamir.keygen(sk=123)
    kp_wrong = fiat_shamir.keygen(sk=124)
    good = fiat_shamir.interactive_prove(kp_real, challenge=456, nonce=789)
    assert not fiat_shamir.interactive_verify(kp_wrong.pk, good)


def test_fs_prove_roundtrip_accepts() -> None:
    kp = fiat_shamir.keygen(sk=42)
    oracle = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER, seed=b"fs-test"
    )
    proof = fiat_shamir.fs_prove(kp, oracle, nonce=200)
    # Verifier uses the same oracle; the cached challenge is reused.
    assert fiat_shamir.fs_verify(kp.pk, proof, oracle)


def test_fs_prove_rejects_wrong_oracle_range() -> None:
    kp = fiat_shamir.keygen(sk=42)
    wrong_oracle = rom_simulator.RandomOracle(output_modulus=31, seed=b"x")
    with pytest.raises(ValueError):
        fiat_shamir.fs_prove(kp, wrong_oracle, nonce=200)


def test_fs_prove_rejects_bad_nonce() -> None:
    kp = fiat_shamir.keygen(sk=42)
    oracle = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER
    )
    with pytest.raises(ValueError):
        fiat_shamir.fs_prove(kp, oracle, nonce=0)
    with pytest.raises(ValueError):
        fiat_shamir.fs_prove(kp, oracle, nonce=fiat_shamir.DEFAULT_ORDER)


def test_fs_verify_rejects_tampered_response() -> None:
    kp = fiat_shamir.keygen(sk=42)
    oracle = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER, seed=b"tamper"
    )
    proof = fiat_shamir.fs_prove(kp, oracle, nonce=200)
    tampered = fiat_shamir.FiatShamirProof(
        commitment=proof.commitment,
        response=(proof.response + 1) % fiat_shamir.DEFAULT_ORDER,
    )
    assert not fiat_shamir.fs_verify(kp.pk, tampered, oracle)


def test_fs_verify_rejects_wrong_oracle_range() -> None:
    kp = fiat_shamir.keygen(sk=42)
    oracle = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER
    )
    proof = fiat_shamir.fs_prove(kp, oracle, nonce=200)
    wrong_oracle = rom_simulator.RandomOracle(output_modulus=31)
    with pytest.raises(ValueError):
        fiat_shamir.fs_verify(kp.pk, proof, wrong_oracle)


def test_fs_verify_rejects_bad_pk() -> None:
    kp = fiat_shamir.keygen(sk=42)
    oracle = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER
    )
    proof = fiat_shamir.fs_prove(kp, oracle, nonce=200)
    with pytest.raises(ValueError):
        fiat_shamir.fs_verify(0, proof, oracle)
    with pytest.raises(ValueError):
        fiat_shamir.fs_verify(fiat_shamir.DEFAULT_PRIME, proof, oracle)


def test_rewind_extract_recovers_witness() -> None:
    kp = fiat_shamir.keygen(sk=321)
    nonce = 456  # shared across both transcripts
    a = fiat_shamir.interactive_prove(kp, challenge=100, nonce=nonce)
    b = fiat_shamir.interactive_prove(kp, challenge=200, nonce=nonce)
    # Same nonce => same commitment.
    assert a.commitment == b.commitment
    recovered = fiat_shamir.rewind_extract(kp.pk, a, b)
    assert recovered == kp.sk


def test_rewind_extract_rejects_mismatched_commitments() -> None:
    kp = fiat_shamir.keygen(sk=321)
    a = fiat_shamir.interactive_prove(kp, challenge=100, nonce=456)
    b = fiat_shamir.interactive_prove(kp, challenge=200, nonce=457)  # different nonce
    with pytest.raises(ValueError):
        fiat_shamir.rewind_extract(kp.pk, a, b)


def test_rewind_extract_rejects_equal_challenges() -> None:
    kp = fiat_shamir.keygen(sk=321)
    a = fiat_shamir.interactive_prove(kp, challenge=100, nonce=456)
    b = fiat_shamir.interactive_prove(kp, challenge=100, nonce=456)
    with pytest.raises(ValueError):
        fiat_shamir.rewind_extract(kp.pk, a, b)


def test_rewind_extract_rejects_nonverifying_transcripts() -> None:
    kp = fiat_shamir.keygen(sk=321)
    a = fiat_shamir.interactive_prove(kp, challenge=100, nonce=456)
    bad = fiat_shamir.InteractiveTranscript(
        commitment=a.commitment,
        challenge=200,
        response=(a.response + 5) % fiat_shamir.DEFAULT_ORDER,  # broken
    )
    with pytest.raises(ValueError):
        fiat_shamir.rewind_extract(kp.pk, a, bad)


def test_fs_proof_verifies_across_fresh_oracle_with_same_seed() -> None:
    kp = fiat_shamir.keygen(sk=42)
    oracle_a = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER, seed=b"fresh"
    )
    proof = fiat_shamir.fs_prove(kp, oracle_a, nonce=100)
    # A fresh oracle with the same seed must accept the same proof;
    # the FS compilation's determinism is exactly this property.
    oracle_b = rom_simulator.RandomOracle(
        output_modulus=fiat_shamir.DEFAULT_ORDER, seed=b"fresh"
    )
    assert fiat_shamir.fs_verify(kp.pk, proof, oracle_b)


def test_default_group_constants_match_the_chapter() -> None:
    """Pin the toy group, which the chapter prints and Ch 32 also owns.

    Chapter 33 reuses Chapter 32's ``toy_kzg`` group by value: this
    module imports nothing from ch32, and the chapter's prose, the
    printed blocks and this package's docstring all assert the two
    agree. Nothing else binds them, and the order check every other
    test relies on passes for 16 and for every other square in the
    order-1013 subgroup, so the generator can drift away from the
    printed ``G = 4`` with the whole suite green. ``tests/ch32``
    pins the same three literals on its own side; a drift on either
    side now fails there.
    """
    assert fiat_shamir.DEFAULT_PRIME == 2027
    assert fiat_shamir.DEFAULT_ORDER == 1013
    assert fiat_shamir.DEFAULT_GENERATOR == 4


def test_random_sampling_excludes_the_zero_witness() -> None:
    """The sampled witness and nonce start at 1, never 0.

    ``x = 0`` forces ``h = 1`` and trivializes the relation, which the
    chapter states outright. The sampling branch is
    ``1 + randbelow(n - 1)``; dropping the offset makes keygen raise
    roughly one call in 1013, which no unmocked draw reliably catches.
    """
    monkey = {"n": 0}

    def fake_randbelow(upper: int) -> int:
        assert upper == fiat_shamir.DEFAULT_ORDER - 1
        return monkey["n"]

    import fiat_shamir_qrom.fiat_shamir as mod

    original = mod.secrets.randbelow
    mod.secrets.randbelow = fake_randbelow
    try:
        assert mod.keygen().sk == 1
        assert mod.interactive_prove(mod.keygen(sk=5), challenge=3).commitment == pow(
            mod.DEFAULT_GENERATOR, 1, mod.DEFAULT_PRIME
        )
    finally:
        mod.secrets.randbelow = original


def test_transcript_encoding_is_four_bytes_per_element() -> None:
    """The oracle input is two fixed-width four-byte big-endian fields.

    The chapter prints this width and its caveat paragraph reasons
    about it: the encoding is unambiguous only because the toy ``p``
    fits the field. A narrower width still round-trips every proof, so
    no other test sees it.
    """
    encoded = fiat_shamir._transcript_bytes(1, 2)
    assert len(encoded) == 8
    assert encoded == (1).to_bytes(4, "big") + (2).to_bytes(4, "big")
