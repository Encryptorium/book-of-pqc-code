"""RFC 8032 Section 7.1 known-answer tests for Ed25519.

Covers the empty-message vector and the 1-byte and 2-byte message
vectors. Each KAT exercises keygen (seed -> public key) and sign/verify
together.
"""

from hybrid.ed25519 import ed25519_keygen, ed25519_sign, ed25519_verify


def _h(s: str) -> bytes:
    return bytes.fromhex(s.replace(" ", "").replace("\n", ""))


def test_rfc8032_test1_empty_message():
    seed = _h("9d61b19deffd5a60ba844af492ec2cc4 4449c5697b326919703bac031cae7f60")
    expected_pk = _h("d75a980182b10ab7d54bfed3c964073a 0ee172f3daa62325af021a68f707511a")
    expected_sig = _h(
        "e5564300c360ac729086e2cc806e828a 84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46b d25bf5f0595bbe24655141438e7a100b"
    )
    pk, sk = ed25519_keygen(seed)
    assert pk == expected_pk
    sig = ed25519_sign(sk, b"")
    assert sig == expected_sig
    assert ed25519_verify(pk, b"", sig) is True


def test_rfc8032_test2_one_byte_message():
    seed = _h("4ccd089b28ff96da9db6c346ec114e0f 5b8a319f35aba624da8cf6ed4fb8a6fb")
    expected_pk = _h("3d4017c3e843895a92b70aa74d1b7ebc 9c982ccf2ec4968cc0cd55f12af4660c")
    message = _h("72")
    expected_sig = _h(
        "92a009a9f0d4cab8720e820b5f642540 a2b27b5416503f8fb3762223ebdb69da"
        "085ac1e43e15996e458f3613d0f11d8c 387b2eaeb4302aeeb00d291612bb0c00"
    )
    pk, sk = ed25519_keygen(seed)
    assert pk == expected_pk
    sig = ed25519_sign(sk, message)
    assert sig == expected_sig
    assert ed25519_verify(pk, message, sig) is True


def test_rfc8032_test3_two_byte_message():
    seed = _h("c5aa8df43f9f837bedb7442f31dcb7b1 66d38535076f094b85ce3a2e0b4458f7")
    expected_pk = _h("fc51cd8e6218a1a38da47ed00230f058 0816ed13ba3303ac5deb911548908025")
    message = _h("af82")
    expected_sig = _h(
        "6291d657deec24024827e69c3abe01a3 0ce548a284743a445e3680d7db5ac3ac"
        "18ff9b538d16f290ae67f760984dc659 4a7c15e9716ed28dc027beceea1ec40a"
    )
    pk, sk = ed25519_keygen(seed)
    assert pk == expected_pk
    sig = ed25519_sign(sk, message)
    assert sig == expected_sig
    assert ed25519_verify(pk, message, sig) is True


def test_ed25519_verify_rejects_tampered_signature():
    seed = _h("9d61b19deffd5a60ba844af492ec2cc4 4449c5697b326919703bac031cae7f60")
    pk, sk = ed25519_keygen(seed)
    sig = ed25519_sign(sk, b"hello")
    tampered = bytearray(sig)
    tampered[0] ^= 0x01
    assert ed25519_verify(pk, b"hello", bytes(tampered)) is False


def test_ed25519_verify_rejects_tampered_message():
    seed = _h("9d61b19deffd5a60ba844af492ec2cc4 4449c5697b326919703bac031cae7f60")
    pk, sk = ed25519_keygen(seed)
    sig = ed25519_sign(sk, b"hello")
    assert ed25519_verify(pk, b"hell0", sig) is False
