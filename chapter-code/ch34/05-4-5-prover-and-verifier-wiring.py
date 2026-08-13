# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 34: STARKs and FRI revisited
# Section: "4.5 Prover and verifier wiring"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch34-starks-fri-revisited/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch34/05-4-5-prover-and-verifier-wiring.py

# Block 5: pedagogical slice of starks.prover.stark_prove and
# starks.verifier.stark_verify (stdlib only).

import sys
sys.path.insert(0, "solutions/ch34-starks/src")
from starks.arithmetization import fibonacci_air, fibonacci_trace
from starks.prover import stark_prove
from starks.verifier import stark_verify

air = fibonacci_air()
trace = fibonacci_trace()
honest_proof = stark_prove(air, trace, num_queries=6, grinding_bits=4)
print("honest proof accepted:", stark_verify(air, honest_proof, num_queries=6, grinding_bits=4))

forged_proof = stark_prove(air, trace, num_queries=6, grinding_bits=4)
forged_proof.trace[4] = (forged_proof.trace[4] + 1) % 97
print("forged proof accepted:", stark_verify(air, forged_proof, num_queries=6, grinding_bits=4))
# ==> honest proof accepted: True
# ==> forged proof accepted: False
