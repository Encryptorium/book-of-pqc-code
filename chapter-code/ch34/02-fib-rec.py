# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 34: STARKs and FRI revisited
# Section: "4.1 Arithmetization"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch34-starks-fri-revisited/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch34/02-fib-rec.py

# Block 2: pedagogical slice of starks.arithmetization.AIR and
# TransitionConstraint (stdlib only).

from collections import namedtuple

TransitionConstraint = namedtuple("TransitionConstraint", ["window", "evaluator", "name"])
BoundaryConstraint = namedtuple("BoundaryConstraint", ["row", "expected", "name"])

def fib_rec(trace, i, p):
    return (trace[i + 2] - trace[i + 1] - trace[i]) % p

fibonacci_transition = TransitionConstraint(window=3, evaluator=fib_rec, name="fib_rec")
fibonacci_boundaries = [
    BoundaryConstraint(row=0, expected=1, name="fib_init_0"),
    BoundaryConstraint(row=1, expected=1, name="fib_init_1"),
]

def evaluate_air(trace, transitions, boundaries, prime):
    if len(trace) < max((t.window for t in transitions), default=0):
        raise ValueError("trace shorter than largest window")
    residues = []
    for t in transitions:
        for i in range(len(trace) - t.window + 1):
            residues.append(t.evaluator(trace, i, prime))
    for b in boundaries:
        residues.append((trace[b.row] - b.expected) % prime)
    return residues

trace = [1, 1, 2, 3, 5, 8, 13, 21]
residues = evaluate_air(trace, [fibonacci_transition], fibonacci_boundaries, 97)
print(len(residues), "constraints;", "all zero" if not any(residues) else "violations")
# ==> 8 constraints; all zero
