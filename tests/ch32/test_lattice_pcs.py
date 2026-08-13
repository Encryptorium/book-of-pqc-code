"""Tests for ``commitment_schemes.lattice_pcs``."""

import pytest

from commitment_schemes import lattice_pcs


def test_default_params_shape() -> None:
    params = lattice_pcs.default_params()
    assert params.modulus == 257
    assert params.dimension == 8
    assert params.commit_size == 4


def test_sample_public_matrix_seeded_is_deterministic() -> None:
    params = lattice_pcs.default_params()
    a1 = lattice_pcs.sample_public_matrix(params, seed=b"seed-a")
    a2 = lattice_pcs.sample_public_matrix(params, seed=b"seed-a")
    assert a1.rows == a2.rows
    a3 = lattice_pcs.sample_public_matrix(params, seed=b"seed-b")
    assert a3.rows != a1.rows


def test_commit_verify_roundtrip() -> None:
    params = lattice_pcs.default_params()
    matrix = lattice_pcs.sample_public_matrix(params, seed=b"round-trip")
    message = [3, -2, 1, 0, -4, 2, -1, 5]
    error = [1, -1, 0, 2]
    commitment = lattice_pcs.commit(matrix, message, error)
    assert lattice_pcs.verify(matrix, commitment, message, error)


def test_tampered_message_fails_verification() -> None:
    params = lattice_pcs.default_params()
    matrix = lattice_pcs.sample_public_matrix(params, seed=b"tamper")
    message = [3, -2, 1, 0, -4, 2, -1, 5]
    error = [1, -1, 0, 2]
    commitment = lattice_pcs.commit(matrix, message, error)

    bad_message = list(message)
    bad_message[0] = (bad_message[0] + 1) % params.modulus
    assert not lattice_pcs.verify(matrix, commitment, bad_message, error)


def test_tampered_error_fails_verification() -> None:
    params = lattice_pcs.default_params()
    matrix = lattice_pcs.sample_public_matrix(params, seed=b"tamper-err")
    message = [3, -2, 1, 0, -4, 2, -1, 5]
    error = [1, -1, 0, 2]
    commitment = lattice_pcs.commit(matrix, message, error)

    bad_error = list(error)
    bad_error[0] = bad_error[0] + 1
    assert not lattice_pcs.verify(matrix, commitment, message, bad_error)


def test_commit_rejects_wrong_dimension_message() -> None:
    params = lattice_pcs.default_params()
    matrix = lattice_pcs.sample_public_matrix(params, seed=b"dim")
    short_message = [1, 2, 3]
    error = [0, 0, 0, 0]
    with pytest.raises(ValueError):
        lattice_pcs.commit(matrix, short_message, error)


def test_commit_rejects_wrong_dimension_error() -> None:
    params = lattice_pcs.default_params()
    matrix = lattice_pcs.sample_public_matrix(params, seed=b"dim")
    message = [1] * params.dimension
    short_error = [0, 0]
    with pytest.raises(ValueError):
        lattice_pcs.commit(matrix, message, short_error)


def test_sis_binding_witness_recovers_difference() -> None:
    """Two openings to the same commitment yield a Module-SIS witness.

    In Module-SIS terms: if A*m_a + e_a = A*m_b + e_b mod q, then
    A*(m_a - m_b) + (e_a - e_b) = 0 mod q, which is a short solution
    to the homogeneous SIS instance. Ch 32 cites this as the binding
    reduction. The routine here extracts the solution vector; the
    solution's shortness is the part that makes SIS hard.
    """
    params = lattice_pcs.default_params()
    message_a = [1, 2, 3, 4, 5, 6, 7, 8]
    message_b = [2, 2, 3, 4, 5, 6, 7, 8]
    error_a = [1, 1, 1, 1]
    error_b = [2, 1, 1, 1]

    diff_m, diff_e = lattice_pcs.sis_binding_witness(
        message_a, error_a, message_b, error_b, params.modulus
    )
    assert diff_m == [-1, 0, 0, 0, 0, 0, 0, 0]
    assert diff_e == [-1, 0, 0, 0]


def test_default_params_pins_the_error_bound_the_chapter_prints() -> None:
    """The error bound is a labelled constant the chapter quotes as ``beta_e = 2``.

    ``test_default_params_shape`` checks the modulus and the two
    dimensions and leaves ``error_bound`` unread, so raising it to 5
    passes every other test in this file while the module stops agreeing
    with the paragraph that introduces Block 5.
    """
    assert lattice_pcs.default_params().error_bound == 2
    assert lattice_pcs.DEFAULT_ERROR_BOUND == 2


def test_sample_error_stays_inside_the_bound() -> None:
    """``sample_error`` is stubbed in the manifest, so something must reach it.

    Before this test the manifest's ``Proved by:`` line named a file that
    never called the function, which told a reader implementing the stub
    that a green suite meant a correct implementation.
    """
    params = lattice_pcs.default_params()
    for _ in range(50):
        error = lattice_pcs.sample_error(params)
        assert len(error) == params.commit_size
        assert all(-params.error_bound <= e <= params.error_bound for e in error)
