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


def test_sis_binding_witness_computes_the_coordinatewise_difference() -> None:
    """The routine subtracts two openings, whatever they open.

    This pins the arithmetic alone. The two openings here are arbitrary,
    so the returned pair is a difference vector and NOT an exhibited SIS
    solution: nothing in this fixture supplies the premise the reduction
    needs, which is that both openings reach the same commitment. The
    test below supplies it.
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


def test_two_openings_to_one_commitment_give_a_short_sis_solution() -> None:
    """The real reduction, with the same-commitment premise supplied.

    A matrix with two equal columns admits two distinct short messages
    with the same image, so both open the same commitment under the same
    error. The difference is then a nonzero short solution of the
    homogeneous instance A*x + y = 0 mod q, which is what Module-SIS is
    assumed to make hard to find. Here it is easy, because the matrix was
    chosen to make it easy; that is the point of exhibiting it rather
    than asserting it.
    """
    params = lattice_pcs.default_params()
    base = lattice_pcs.sample_public_matrix(params, seed=b"sis-witness")
    rows = [list(row) for row in base.rows]
    for row in rows:
        row[1] = row[0]  # columns 0 and 1 now coincide
    matrix = lattice_pcs.PublicMatrix(
        params=params, rows=[tuple(row) for row in rows]
    )

    error = [0] * params.commit_size
    message_a = [1] + [0] * (params.dimension - 1)
    message_b = [0, 1] + [0] * (params.dimension - 2)

    commitment = lattice_pcs.commit(matrix, message_a, error)
    assert lattice_pcs.verify(matrix, commitment, message_a, error)
    assert lattice_pcs.verify(matrix, commitment, message_b, error)
    assert message_a != message_b

    diff_m, diff_e = lattice_pcs.sis_binding_witness(
        message_a, error, message_b, error, params.modulus
    )
    assert any(diff_m), "the witness must be nonzero to be a solution"

    # A*diff_m + diff_e == 0 mod q, coordinate by coordinate.
    for row, y in zip(matrix.rows, diff_e):
        acc = sum(a * x for a, x in zip(row, diff_m)) + y
        assert acc % params.modulus == 0

    # And it is short, which is the half that makes SIS hard.
    bound = params.error_bound
    assert max(abs(v) for v in diff_m) <= max(1, bound)
    assert max(abs(v) for v in diff_e) <= max(1, bound)


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
