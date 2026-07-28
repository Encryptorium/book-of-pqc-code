"""Tests for ``prelim_algebra.linear``.

The expected values are the ones Chapter 2 and its Appendix D page print. If
one of these tests fails, either the code or the book is wrong, and the two
cannot be reconciled by changing this file.
"""

from prelim_algebra import gauss_eliminate


CHAPTER_MATRIX = [
    [1, 2, 3],
    [0, 1, 4],
    [2, 0, 0],
]

EXERCISE_MATRIX = [
    [1, 2, 3, 4],
    [2, 3, 4, 5],
    [3, 4, 5, 6],
    [4, 5, 6, 7],
]


def test_chapter_example_matches_the_printed_output() -> None:
    # The chapter prints the three reduced rows and "rank = 2".
    reduced, rank = gauss_eliminate(CHAPTER_MATRIX, 5)
    assert reduced == [[1, 0, 0], [0, 1, 4], [0, 0, 0]]
    assert rank == 2


def test_the_chapter_dependency_is_the_one_the_prose_states() -> None:
    # The prose derives the rank from 2 * row 1 + row 2 == row 3 over F_5.
    combination = [
        (2 * CHAPTER_MATRIX[0][c] + CHAPTER_MATRIX[1][c]) % 5 for c in range(3)
    ]
    assert combination == CHAPTER_MATRIX[2]


def test_exercise_four_matrix_has_rank_two_over_f7() -> None:
    # Exercise 4 asks for the rank of the arithmetic-progression matrix.
    _reduced, rank = gauss_eliminate(EXERCISE_MATRIX, 7)
    assert rank == 2


def test_exercise_four_rows_differ_by_the_all_ones_vector() -> None:
    # Appendix D's structural argument: successive rows differ by (1,1,1,1)
    # over F_7. The last entry only works modulo 7, since 7 - 6 == 1 there
    # while the integer difference in that column is 7 - 6 == 1 as well for
    # rows 1 to 3 and 0 - 6 == 1 mod 7 for the last.
    for i in range(1, 4):
        diff = [(EXERCISE_MATRIX[i][j] - EXERCISE_MATRIX[i - 1][j]) % 7 for j in range(4)]
        assert diff == [1, 1, 1, 1]


def test_exercise_four_has_two_independent_dependencies() -> None:
    # Four rows spanning a two-dimensional space means the space of
    # dependencies is two-dimensional, so there are two independent relations,
    # not one. Both hold over the integers as well as modulo 7.
    r1, r2, r3, r4 = EXERCISE_MATRIX
    assert [r3[j] - 2 * r2[j] + r1[j] for j in range(4)] == [0, 0, 0, 0]
    assert [r4[j] - 2 * r3[j] + r2[j] for j in range(4)] == [0, 0, 0, 0]


def test_rank_is_the_number_of_nonzero_rows() -> None:
    for matrix, p in ((CHAPTER_MATRIX, 5), (EXERCISE_MATRIX, 7)):
        reduced, rank = gauss_eliminate(matrix, p)
        assert sum(1 for row in reduced if any(x % p for x in row)) == rank


def test_identity_has_full_rank(small_primes: list[int]) -> None:
    identity = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    for p in small_primes:
        reduced, rank = gauss_eliminate(identity, p)
        assert reduced == identity
        assert rank == 4


def test_zero_matrix_has_rank_zero() -> None:
    zero = [[0] * 3 for _ in range(3)]
    reduced, rank = gauss_eliminate(zero, 7)
    assert reduced == zero
    assert rank == 0


def test_pivot_search_skips_a_zero_leading_column() -> None:
    # The first column is all zeros, so no pivot is placed there and the
    # routine moves on rather than failing.
    reduced, rank = gauss_eliminate([[0, 1, 2], [0, 2, 4]], 7)
    assert rank == 1
    assert reduced[0] == [0, 1, 2]
    assert reduced[1] == [0, 0, 0]


def test_rectangular_input_is_handled() -> None:
    _reduced, rank = gauss_eliminate([[1, 2, 3, 4], [2, 4, 6, 8]], 7)
    assert rank == 1


def test_the_input_matrix_is_not_mutated() -> None:
    # The routine copies each row before it starts, so a caller can reuse the
    # matrix afterwards.
    original = [row[:] for row in CHAPTER_MATRIX]
    gauss_eliminate(CHAPTER_MATRIX, 5)
    assert CHAPTER_MATRIX == original


def test_rank_never_exceeds_the_smaller_dimension() -> None:
    for matrix, p in ((CHAPTER_MATRIX, 5), (EXERCISE_MATRIX, 7)):
        _reduced, rank = gauss_eliminate(matrix, p)
        assert rank <= min(len(matrix), len(matrix[0]))
