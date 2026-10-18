# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 34: STARKs and FRI revisited
# Section: "4.5 Prover and verifier wiring"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch34-starks-fri-revisited/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch34/06-seeded-transcript.py

# Block 6: the honest trace sent with the LDE of another trace committed
# (stdlib only).

import sys
sys.path.insert(0, "solutions/ch34-starks/src")
from starks.arithmetization import (evaluate_air, fibonacci_air, fibonacci_trace,
                                    interpolate_trace)
from starks.fri_full import fri_prove, fri_verify
from starks.lde import eval_poly, extend_polynomial, lde_domain, trace_domain
from starks.prover import STARKProof
from starks.transcript import Transcript
from starks.verifier import stark_verify

air, trace = fibonacci_air(), fibonacci_trace()
other = list(trace)
other[4] = (other[4] + 1) % 97    # the trace Block 5 forged
t_dom, l_dom = trace_domain(), lde_domain()
honest_word = extend_polynomial(interpolate_trace(trace, t_dom, 97), l_dom, 97)
swapped_word = extend_polynomial(interpolate_trace(other, t_dom, 97), l_dom, 97)

def seeded_transcript():
    # What stark_prove and stark_verify absorb before FRI starts.
    tx = Transcript(domain_sep=b"ch34-stark")
    for label, value in [(b"prime", 97), (b"trace-length", 8), (b"lde-size", 32)]:
        tx.absorb_int(label, value, num_bytes=8)
    for v in trace:
        tx.absorb_int(b"trace-value", v, num_bytes=8)
    return tx

fri = fri_prove(initial_codeword=swapped_word, initial_domain=l_dom, prime=97,
                transcript=seeded_transcript(), num_queries=6, grinding_bits=4,
                degree_bound=8)
proof = STARKProof(trace=list(trace), trace_commitment=fri.commitments[0], fri_proof=fri)

fri_ok = fri_verify(proof=fri, initial_domain=l_dom, prime=97,
                    transcript=seeded_transcript(), num_queries=6, grinding_bits=4,
                    degree_bound=8)
coeffs = interpolate_trace(trace, t_dom, 97)
mismatches = sum(eval_poly(coeffs, l_dom[o.leaf_index], 97) != o.leaf_value
                 for o in fri.query_openings[0])
differ = sum(a != b for a, b in zip(honest_word, swapped_word))

print("AIR residues on the sent trace all zero:", not any(evaluate_air(air, proof.trace)))
print("FRI accepts the committed word:", fri_ok)
print("consistency fails at", mismatches, "of 6 query positions")
print("the two words differ at", differ, "of 32 LDE points")
print("proof accepted:", stark_verify(air, proof, num_queries=6, grinding_bits=4))
# ==> AIR residues on the sent trace all zero: True
# ==> FRI accepts the committed word: True
# ==> consistency fails at 6 of 6 query positions
# ==> the two words differ at 32 of 32 LDE points
# ==> proof accepted: False
