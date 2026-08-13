# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 34: STARKs and FRI revisited
# Section: "Eight Fibonacci steps, one non-interactive proof"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch34-starks-fri-revisited/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch34/01-fibonacci-trace.py

# Block 1: pedagogical slice of starks.arithmetization.fibonacci_air and
# evaluate_air (stdlib only).

PRIME = 97
TRACE_LENGTH = 8

def fibonacci_trace(length, prime):
    if length < 2:
        raise ValueError("length must be at least two")
    trace = [1, 1]
    for _ in range(length - 2):
        trace.append((trace[-1] + trace[-2]) % prime)
    return trace

def transition_residue(trace, i, prime):
    return (trace[i + 2] - trace[i + 1] - trace[i]) % prime

def boundary_residues(trace, prime):
    return [(trace[0] - 1) % prime, (trace[1] - 1) % prime]

trace = fibonacci_trace(TRACE_LENGTH, PRIME)
transitions = [transition_residue(trace, i, PRIME) for i in range(TRACE_LENGTH - 2)]
boundaries = boundary_residues(trace, PRIME)

print("trace:", trace)
print("transition residues:", transitions)
print("boundary residues:", boundaries)
# ==> trace: [1, 1, 2, 3, 5, 8, 13, 21]
# ==> transition residues: [0, 0, 0, 0, 0, 0]
# ==> boundary residues: [0, 0]
