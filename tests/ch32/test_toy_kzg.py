"""Tests for ``commitment_schemes.toy_kzg``."""

import pytest

from commitment_schemes import toy_kzg


def test_setup_rejects_bad_inputs() -> None:
    with pytest.raises(ValueError):
        toy_kzg.setup(degree=-1, tau=5)
    with pytest.raises(ValueError):
        toy_kzg.setup(degree=4, tau=0)
    with pytest.raises(ValueError):
        toy_kzg.setup(degree=4, tau=toy_kzg.DEFAULT_ORDER)


def test_default_generator_has_prime_order() -> None:
    """Sanity check that the default generator spans the prime-order subgroup."""
    assert pow(toy_kzg.DEFAULT_GENERATOR, toy_kzg.DEFAULT_ORDER, toy_kzg.DEFAULT_PRIME) == 1
    assert toy_kzg.DEFAULT_GENERATOR != 1


def test_roundtrip_commit_open_verify_with_trapdoor() -> None:
    tau = 500
    srs = toy_kzg.setup(degree=4, tau=tau)
    coeffs = [7, 11, 13, 17, 19]  # all < DEFAULT_ORDER = 1013
    z = 100
    commitment = toy_kzg.commit(coeffs, srs)
    y, witness = toy_kzg.open_at(coeffs, z, srs)
    assert toy_kzg.verify_with_trapdoor(commitment, z, y, witness, srs, tau)


def test_quotient_degree_and_remainder() -> None:
    order = toy_kzg.DEFAULT_ORDER
    coeffs = [1, 2, 3, 4]  # p(x) = 1 + 2x + 3x^2 + 4x^3 in F_order
    z = 5
    y = toy_kzg.eval_poly(coeffs, z, order)
    q = toy_kzg.quotient(coeffs, z, order)
    assert len(q) == len(coeffs) - 1
    # p(x) = q(x) * (x - z) + y in F_order[x]
    for x in (1, 2, 3, 7, 13, 100, 500, 900):
        p_x = toy_kzg.eval_poly(coeffs, x, order)
        q_x = toy_kzg.eval_poly(q, x, order)
        expected = (q_x * (x - z) + y) % order
        assert p_x == expected


def test_commit_beyond_srs_raises() -> None:
    srs = toy_kzg.setup(degree=3, tau=500)
    with pytest.raises(ValueError):
        toy_kzg.commit([1, 2, 3, 4, 5], srs)


def test_shor_recovers_tau() -> None:
    tau = 777
    srs = toy_kzg.setup(degree=4, tau=tau)
    recovered = toy_kzg.shor_recover_tau(srs)
    assert recovered == tau


def test_post_shor_forgery_accepts_wrong_evaluation() -> None:
    """After Shor recovers tau, the adversary forges an opening at any y.

    This exhibits the binding break: the verify-with-trapdoor oracle
    accepts the forged witness for an arbitrary evaluation claim, even
    though the true p(z) is a different value.
    """
    tau = 777
    srs = toy_kzg.setup(degree=4, tau=tau)
    coeffs = [2, 3, 5, 7, 11]
    z = 100

    commitment = toy_kzg.commit(coeffs, srs)
    honest_y = toy_kzg.eval_poly(coeffs, z, toy_kzg.DEFAULT_ORDER)

    # Adversary recovers tau (in practice via Shor) and chooses any
    # target evaluation value.
    recovered_tau = toy_kzg.shor_recover_tau(srs)
    assert recovered_tau == tau

    fake_y = (honest_y + 17) % toy_kzg.DEFAULT_ORDER
    assert fake_y != honest_y

    fake_witness = toy_kzg.forge_opening(commitment, z, fake_y, srs, recovered_tau)
    assert toy_kzg.verify_with_trapdoor(
        commitment, z, fake_y, fake_witness, srs, recovered_tau
    )


def test_classical_verifier_rejects_tampered_opening() -> None:
    """Without trapdoor recovery, a tampered y fails verification."""
    tau = 777
    srs = toy_kzg.setup(degree=4, tau=tau)
    coeffs = [2, 3, 5, 7, 11]
    z = 100
    commitment = toy_kzg.commit(coeffs, srs)
    y, witness = toy_kzg.open_at(coeffs, z, srs)

    tampered_y = (y + 1) % toy_kzg.DEFAULT_ORDER
    assert not toy_kzg.verify_with_trapdoor(
        commitment, z, tampered_y, witness, srs, tau
    )


def test_shor_recover_tau_requires_at_least_two_powers() -> None:
    """Degenerate SRS with only g should raise rather than silently returning."""
    degenerate_srs = toy_kzg.SRS(
        prime=toy_kzg.DEFAULT_PRIME,
        order=toy_kzg.DEFAULT_ORDER,
        generator=toy_kzg.DEFAULT_GENERATOR,
        powers=[toy_kzg.DEFAULT_GENERATOR],
    )
    with pytest.raises(ValueError):
        toy_kzg.shor_recover_tau(degenerate_srs)


def test_quotient_rejects_empty_coefficients() -> None:
    with pytest.raises(ValueError):
        toy_kzg.quotient([], z=1, order=toy_kzg.DEFAULT_ORDER)


def test_forge_opening_rejects_z_equals_tau() -> None:
    """At z == tau the forgery formula divides by zero; the verifier forces y = p(tau)."""
    tau = 777
    srs = toy_kzg.setup(degree=4, tau=tau)
    commitment = toy_kzg.commit([2, 3, 5, 7, 11], srs)
    with pytest.raises(ValueError):
        toy_kzg.forge_opening(commitment, z=tau, y_fake=42, srs=srs, tau=tau)


def test_default_group_constants_match_the_chapter() -> None:
    """Pin the toy group, which two chapters print and one reuses by name.

    ``test_default_generator_has_prime_order`` only checks that the
    generator lands in the order-1013 subgroup, which 16 and every other
    square also do, so the generator can drift away from the printed
    ``GEN = 4`` with the whole suite green. Chapter 33 reuses this group
    by value in its Schnorr example, so a drift here silently falsifies
    prose in another chapter.
    """
    assert toy_kzg.DEFAULT_PRIME == 2027
    assert toy_kzg.DEFAULT_ORDER == 1013
    assert toy_kzg.DEFAULT_GENERATOR == 4
    # The safe-prime structure the module docstring calls load-bearing:
    # p = 2q + 1, which is what makes every nonzero exponent invertible.
    assert toy_kzg.DEFAULT_PRIME == 2 * toy_kzg.DEFAULT_ORDER + 1
