"""Tests for the L1 arithmetization module of Chapter 31."""

import pytest

from zk_layers.r1cs import GATES, check_r1cs, dot, gate_constraints

# The toy system Chapter 31 prints: a * b = 35 and a + b = 12 over F_97.
# Columns of z are (one, a, b, a*b, a+b).
A = [[0, 1, 0, 0, 0], [0, 1, 1, 0, 0]]
B = [[0, 0, 1, 0, 0], [1, 0, 0, 0, 0]]
C = [[0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]


def test_printed_witness_satisfies_the_printed_system():
    assert check_r1cs(A, B, C, (1, 5, 7, 35, 12)) is True


def test_dot_reduces_modulo_the_field_prime():
    # 1 * 96 + 1 * 96 = 192, which is 192 - 97 = 95 in F_97.
    assert dot([1, 1], (96, 96)) == 95


def test_a_witness_that_breaks_the_product_names_the_failing_constraint():
    # a = 5, b = 7, but the claimed product is 34 rather than 35.
    with pytest.raises(ValueError, match="constraint 0 failed"):
        check_r1cs(A, B, C, (1, 5, 7, 34, 12))


def test_a_witness_that_breaks_the_sum_names_the_second_constraint():
    with pytest.raises(ValueError, match="constraint 1 failed"):
        check_r1cs(A, B, C, (1, 5, 7, 35, 11))


def test_a_witness_congruent_modulo_the_prime_still_satisfies():
    # 35 + 97 = 132 is the same field element as 35, so the constraint
    # holds. This is a property of the field, not a gap in the check.
    assert check_r1cs(A, B, C, (1, 5, 7, 132, 12)) is True


def test_xor_of_two_boolean_constrained_words_costs_one_constraint_per_bit():
    # Appendix D Exercise 2: one 32-bit XOR on already-boolean inputs.
    assert gate_constraints("XOR", 32) == 32


def test_xor_on_unconstrained_inputs_also_pays_booleanity_on_both_operands():
    # 32 products, plus 32 booleanity constraints on each of two operands.
    assert gate_constraints("XOR", 32, inputs_already_boolean=False) == 96


def test_and_costs_the_same_as_xor_because_both_encode_one_product():
    assert gate_constraints("AND", 32) == gate_constraints("XOR", 32)


@pytest.mark.parametrize("gate", ["NOT", "ROTR", "SHR"])
def test_linear_and_relabeling_gates_are_free(gate):
    assert gate_constraints(gate, 32) == 0


def test_a_free_gate_still_pays_booleanity_when_its_input_is_not_constrained():
    # ROTR adds nothing itself, but a wire has to be boolean before it can
    # be rotated as bits at all. Arity 1, so one operand's worth.
    assert gate_constraints("ROTR", 32, inputs_already_boolean=False) == 32


def test_an_unknown_gate_is_rejected():
    with pytest.raises(ValueError, match="unknown gate"):
        gate_constraints("NAND", 32)


def test_a_non_positive_width_is_rejected():
    with pytest.raises(ValueError, match="width must be positive"):
        gate_constraints("XOR", 0)


def test_each_gate_carries_its_own_cost_and_arity():
    """Pin every gate to its own row, not just the set of rows.

    A test that checked only the key set, or only the sum of the costs,
    would survive a permutation of two gates' costs. Swapping XOR's cost
    with NOT's leaves both of those unchanged and makes the cost model
    wrong. This is the test that fails.
    """
    expected = {
        "XOR": (1, 2),
        "AND": (1, 2),
        "NOT": (0, 1),
        "ROTR": (0, 1),
        "SHR": (0, 1),
        "BOOLEANITY": (1, 1),
    }
    assert set(GATES) == set(expected)
    for name, (cost, arity) in expected.items():
        assert GATES[name].name == name
        assert GATES[name].constraints_per_bit == cost
        assert GATES[name].arity == arity
