"""Tests for WOTS+ key generation."""

from wots_xmss.wots import _ell_params, chain, wots_keygen


SK_SEED = b"test-keygen-seed-sk"
PK_SEED = b"test-keygen-seed-pk"


def test_keygen_key_lengths_w16():
    """At w=16, n=32: ell=67, each value is 32 bytes."""
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=16, n=32)
    ell_1, ell_2, ell = _ell_params(32, 16)
    assert ell == 67
    assert len(sk) == 67
    assert len(pk) == 67
    assert all(len(s) == 32 for s in sk)
    assert all(len(p) == 32 for p in pk)


def test_keygen_key_lengths_w4():
    """At w=4, n=32: ell_1=128, ell_2=5, ell=133."""
    ell_1, ell_2, ell = _ell_params(32, 4)
    assert ell_1 == 128
    # max_checksum = 128 * 3 = 384, floor(log2(384))+1 = 9, ell_2 = ceil(9/2) = 5
    assert ell_2 == 5
    assert ell == 133
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=4, n=32)
    assert len(sk) == 133


def test_keygen_deterministic():
    """Same seed produces the same keypair."""
    sk1, pk1 = wots_keygen(SK_SEED, PK_SEED)
    sk2, pk2 = wots_keygen(SK_SEED, PK_SEED)
    assert sk1 == sk2
    assert pk1 == pk2


def test_keygen_different_seeds():
    """Different seeds produce different keypairs."""
    sk1, pk1 = wots_keygen(b"sk-a", b"pk-a")
    sk2, pk2 = wots_keygen(b"sk-b", b"pk-b")
    assert sk1 != sk2
    assert pk1 != pk2


def test_pk_is_chain_endpoint():
    """Each pk[i] equals chain(sk[i], 0, w-1, pk_seed, i)."""
    w = 16
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=w)
    for i in range(len(sk)):
        assert pk[i] == chain(sk[i], 0, w - 1, PK_SEED, i)
