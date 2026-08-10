"""Signature component accounting, and the multi-target preimage reduction.

Two counts run through Chapter 18 and they are not the same count, which is the
distinction this module exists to keep straight.

**Signature components** are the `n`-byte strings a verifier receives. They set
the signature size, and `signature_bytes` reproduces all six FIPS 205 published
sizes from the component formula alone. That agreement is the evidence the
accounting is right: the chapter checks it at SLH-DSA-SHA2-128s only, and
`tests/ch18/test_signature_accounting.py` checks it at all six.

**Preimage targets** are the hash images an adversary could try to invert. The
two counts overlap but neither contains the other. Authentication-path nodes are
signature components and *not* preimage targets: substituting one is a
second-preimage problem on a Merkle node, priced separately. FORS leaf hashes are
preimage targets and *not* signature components: the verifier recomputes each
leaf from a revealed secret, so the leaf hash never travels. Adding the two
populations, or reading the 491 strings of a 128s signature as 491 targets, is
the error the split guards against.

The target population here is an intuition model scoped to one FORS instance and
its hypertree layer, not the term the SPHINCS+/SLH-DSA proof carries. Chapter 18
says so in the prose that introduces it, and the point of the arithmetic is the
size of the reduction ADRS removes, not a security claim of its own.

Standard library only.
"""

from __future__ import annotations

import math

from .params import ParameterSet


def fors_signature_elements(ps: ParameterSet) -> int:
    """FORS `n`-byte strings in one signature: `k` secrets and `k * a` nodes."""
    return ps.k * (1 + ps.a)


def wots_signature_elements(ps: ParameterSet) -> int:
    """WOTS+ chain values in one signature: one `ell`-chain signature per layer."""
    return ps.d * ps.ell


def xmss_auth_elements(ps: ParameterSet) -> int:
    """XMSS authentication nodes in one signature.

    Each of the `d` layers contributes `h_prime` nodes, and `h = d * h_prime`,
    so the total is `h`. Written as the product rather than as `h` so that a
    parameter set with an inexact division fails here instead of silently
    agreeing.
    """
    return ps.d * ps.h_prime


def signature_elements(ps: ParameterSet) -> int:
    """Total `n`-byte strings in one signature, randomizer `R` included."""
    return (
        1
        + fors_signature_elements(ps)
        + wots_signature_elements(ps)
        + xmss_auth_elements(ps)
    )


def signature_bytes(ps: ParameterSet) -> int:
    """Signature size in bytes. Matches FIPS 205 Table 2 at all six SHA-2 sets."""
    return signature_elements(ps) * ps.n_bytes


def fors_instance_targets(ps: ParameterSet) -> int:
    """FORS leaf hashes in one instance's position space, `k * t`.

    Every leaf of every FORS tree is a candidate, not only the `k` a signature
    reveals: the adversary picks which message to forge, so it picks which
    indices it needs. This is why the `s` sets, with their large `t`, expose the
    larger population despite using fewer trees.
    """
    return ps.k * ps.t


def wots_layer_targets(ps: ParameterSet) -> int:
    """WOTS+ revealed chain values across the hypertree layers, `d * ell`."""
    return ps.d * ps.ell


def preimage_target_population(ps: ParameterSet) -> int:
    """The intuition-model preimage target count, `k * t + d * ell`."""
    return fors_instance_targets(ps) + wots_layer_targets(ps)


def multi_target_advantage_bits(ps: ParameterSet) -> float:
    """`log2(N)`: the exponent a shared-function multi-target attack would save.

    With `N` targets under one untweaked hash, each evaluation hits some target
    with probability `N / 2**n` rather than `1 / 2**n`, so the work factor falls
    from `2**n` to `2**n / N`.
    """
    return math.log2(preimage_target_population(ps))


def effective_preimage_bits(ps: ParameterSet) -> float:
    """Classical preimage security if every target shared one hash function.

    This is the number ADRS removes. It is what the chapter's `no_adrs` column
    reports, and it is a counterfactual: SLH-DSA binds each hash call to a
    position address, so the deployed scheme sits at `ps.n_bits`.
    """
    return ps.n_bits - multi_target_advantage_bits(ps)


def effective_quantum_preimage_bits(ps: ParameterSet) -> float:
    """Grover preimage security against the same undefended target population.

    Grover searches a space of size `2**n` holding `N` marked items in about
    `sqrt(2**n / N)` evaluations, so the classical exponent `n - log2(N)` is
    halved rather than reduced by `log2(N)`. Halving after the subtraction is
    the whole content of the function, and getting the order wrong understates
    the quantum cost by `log2(N) / 2` bits.
    """
    return effective_preimage_bits(ps) / 2
