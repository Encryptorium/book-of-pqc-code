"""L1 arithmetization: the rank-1 constraint system format, for Chapter 31.

A rank-1 constraint system expresses a computation as a list of
constraints of the form ``(A_i . z) * (B_i . z) = C_i . z`` over a prime
field, where ``z`` is the witness vector and ``A_i``, ``B_i``, ``C_i``
are coefficient rows. Chapter 31 prints ``dot`` and ``check_r1cs``
against the toy system "I know a, b such that a * b = 35 and
a + b = 12".

The second half of the module is the part the chapter describes but does
not print: the per-gate cost model that decides how expensive a boolean
computation is to arithmetize. R1CS constraints are multiplicative, so a
gate costs constraints in proportion to how much multiplication its
algebraic encoding needs. That is why Chapter 31 can say a full SHA-256
unrolls into tens of thousands of constraints without unrolling one.

Nothing in this module is a cryptographic assumption. L1 is a statement
about finite-field arithmetic, and Chapter 31's cryptanalysis section
records that it is quantum-safe for that reason.
"""

from __future__ import annotations

from dataclasses import dataclass

P = 97  # small prime; a real SNARK uses a ~256-bit prime field.


def dot(row, z):
    return sum(r * v for r, v in zip(row, z)) % P


def check_r1cs(A, B, C, z):
    for i, (a_row, b_row, c_row) in enumerate(zip(A, B, C)):
        lhs = (dot(a_row, z) * dot(b_row, z)) % P
        rhs = dot(c_row, z)
        if lhs != rhs:
            raise ValueError(f"constraint {i} failed: {lhs} != {rhs}")
    return True


@dataclass(frozen=True)
class Gate:
    """One boolean gate's R1CS cost, per bit of operand width.

    ``constraints_per_bit`` is the number of multiplication constraints
    the gate's algebraic encoding needs for each bit of its output.
    ``arity`` is how many operands the gate takes, which is what decides
    the booleanity bill when the operands are not already constrained to
    ``{0, 1}``.
    """

    name: str
    constraints_per_bit: int
    arity: int


# The cost of each boolean gate, in multiplication constraints per bit.
#
# XOR encodes as a XOR b = a + b - 2ab, so the single product ab is the
# only multiplication and the rest is linear. AND is the product itself.
# NOT encodes as 1 - a, which is linear and free. ROTR and SHR are wire
# relabelings on an already bit-decomposed operand: the constraint system
# reads the same wires in a different order and adds nothing.
#
# BOOLEANITY is the odd one out. It is not a gate but the constraint
# a(1 - a) = 0 that pins a wire to {0, 1} in the first place, charged
# once per input bit when a value first enters the circuit as bits.
GATES: dict[str, Gate] = {
    "XOR": Gate("XOR", constraints_per_bit=1, arity=2),
    "AND": Gate("AND", constraints_per_bit=1, arity=2),
    "NOT": Gate("NOT", constraints_per_bit=0, arity=1),
    "ROTR": Gate("ROTR", constraints_per_bit=0, arity=1),
    "SHR": Gate("SHR", constraints_per_bit=0, arity=1),
    "BOOLEANITY": Gate("BOOLEANITY", constraints_per_bit=1, arity=1),
}


def gate_constraints(gate: str, width: int, inputs_already_boolean: bool = True) -> int:
    """Multiplication constraints for one ``width``-bit ``gate``.

    With ``inputs_already_boolean`` true, the count is the gate's own
    encoding cost and nothing else: ``constraints_per_bit * width``. That
    is the usual case inside a hash circuit, where a bit is constrained
    once when it first appears and then reused across every gate it
    feeds.

    With it false, each of the gate's ``arity`` operands is billed
    ``width`` booleanity constraints on top, because a wire that is not
    pinned to ``{0, 1}`` makes the gate's encoding unsound rather than
    merely unconstrained.

    Raises ``ValueError`` for an unknown gate or a non-positive width.
    """
    if gate not in GATES:
        raise ValueError(f"unknown gate {gate!r}; known gates: {sorted(GATES)}")
    if width <= 0:
        raise ValueError("width must be positive")
    spec = GATES[gate]
    total = spec.constraints_per_bit * width
    if not inputs_already_boolean:
        total += spec.arity * width * GATES["BOOLEANITY"].constraints_per_bit
    return total
