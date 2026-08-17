"""Classical scaffolding of the measure-and-reprogram mechanic.

The measure-and-reprogram technique (DFMS19, with the multi-round
generalization in DFMS20) is a QROM proof technique that simulates a
quantum adversary's interaction with a random oracle by measuring one
of the adversary's queries, reprogramming the oracle at the measured
input, and then running the adversary forward. The reduction trades a
factor of ``q`` in the soundness bound (where ``q`` is the adversary's
query budget) for the ability to replace quantum rewinding with a
classical-style extraction.

This module does NOT simulate a quantum adversary. What it does model
is the classical counterpart of the reduction: given a classical
adversary that makes a finite sequence of queries to a ROM and produces
an output, the scaffolding runs the adversary twice against a fresh
oracle and a reprogrammed oracle, respectively, and exhibits the
consistency between the programmed value and the adversary's observed
response at the measured index.

An "adversary" in this module is a Python callable of type
``Callable[[RandomOracle], Any]`` that accepts a random oracle, makes
some number of queries, and returns any value. The scaffolding's
``simulate_classical_extraction`` routine:

1. Runs the adversary against a fresh oracle and records the full
   query log.
2. Picks a measurement index ``i*`` (uniformly at random by default,
   or explicitly for reproducibility).
3. Reads the measured input ``x* = queries[i*]``.
4. Creates a fresh oracle, programs it at ``x*`` to a fresh value
   ``y*`` (uniformly random by default), and runs the adversary again.
5. Confirms that the re-run queried ``x*`` and received exactly ``y*``
   (reprogramming consistency).

The returned dictionary records every piece of information a reduction
would use: the measurement index, the measured input, the reprogrammed
value, and the adversary outputs from both runs.
"""

from __future__ import annotations

import secrets
from typing import Any, Callable

from .rom_simulator import RandomOracle


AdversaryFn = Callable[[RandomOracle], Any]


def run_adversary(
    adversary_fn: AdversaryFn,
    output_modulus: int,
    seed: bytes = b"",
) -> dict:
    """Run an adversary against a fresh RandomOracle and record queries.

    Returns a dict with keys ``"queries"`` (tuple of query inputs in
    order), ``"output"`` (the adversary's return value), and
    ``"oracle"`` (the oracle instance, for inspection).
    """
    # EXERCISE: implement this function.
    #
    # Build a fresh RandomOracle at the given modulus and seed, run the
    # adversary against it, and report the query tuple, the adversary's
    # return value, and the oracle itself for later inspection. Freshness
    # and the shared seed are load-bearing: the scaffolding's second run
    # constructs another oracle from the same seed, so every response
    # outside the reprogrammed point is identical across the two runs, and
    # that is the invariant the comparison rests on.
    #
    # Reference: Chapter 33, 'Multi-round Fiat-Shamir' (Block 3)
    #
    # Proved by:
    #   tests/ch33/test_measure_and_reprogram.py
    raise NotImplementedError("exercise: run_adversary")


def simulate_classical_extraction(
    adversary_fn: AdversaryFn,
    output_modulus: int,
    seed: bytes = b"",
    measured_index: int | None = None,
    reprogrammed_value: int | None = None,
) -> dict:
    """Execute the classical scaffolding of measure-and-reprogram.

    Parameters
    ----------
    adversary_fn
        A callable that takes a RandomOracle, makes queries, and
        returns any value. For reproducibility across runs the
        adversary's query sequence should be a deterministic function
        of its inputs and oracle responses.
    output_modulus
        The ROM response modulus (for Chapter 33 Schnorr this is
        ``DEFAULT_ORDER = 1013``).
    seed
        Seed bytes for ROM lazy sampling.
    measured_index
        Index into the first run's query log at which to perform the
        measurement. If None, an index is chosen uniformly at random.
    reprogrammed_value
        Value to program the oracle with at the measured input. If
        None, a value is drawn uniformly from ``[0, output_modulus)``.

    Returns
    -------
    dict
        A dict with keys:

        - ``"measured_index"``: the index ``i*`` of the measured query.
        - ``"measured_input"``: the input ``x*`` at that index.
        - ``"reprogrammed_value"``: the value ``y*`` programmed at x*.
        - ``"first_queries"``: the full query tuple from the first run.
        - ``"first_output"``: adversary output from the first run.
        - ``"second_queries"``: query tuple from the second run.
        - ``"second_output"``: adversary output from the second run.
        - ``"second_response_at_x_star"``: the oracle's response at x*
          during the second run (equal to ``reprogrammed_value`` iff
          the reprogramming took effect).
        - ``"consistent"``: boolean, True iff
          ``second_response_at_x_star == reprogrammed_value``.

    Raises
    ------
    ValueError
        If the adversary makes no queries in the first run, or if
        ``measured_index`` or ``reprogrammed_value`` is outside the
        valid range.
    """
    # EXERCISE: implement this function.
    #
    # The five steps of the classical shadow of DFMS19. Run the adversary
    # once and keep its query log, raising if it queried nothing. Pick a
    # measurement index, uniformly at random when none is given, and reject
    # one out of range; read x_star at that index. Pick the reprogrammed
    # value y_star, uniformly at random when none is given, and reject one
    # outside [0, output_modulus). Build a second oracle at the same seed,
    # reprogram it at x_star before running anything against it, and run the
    # adversary again. Read the second run's response at x_star and report
    # whether it equals y_star. Raise if the second run never queried
    # x_star: an adversary whose query schedule branches on oracle responses
    # diverges before the measured point, and the scaffolding then has
    # nothing to compare. Note what this is not. The real reduction is
    # single-shot; no post-measurement quantum state can be cloned to
    # support a literal rerun, so the two classical runs exhibit the
    # algebraic invariant the quantum proof builds on rather than the proof
    # itself.
    #
    # Reference: Chapter 33, 'The measure-and-reprogram technique' and 'Multi-round Fiat-Shamir' (Block 3)
    #
    # Proved by:
    #   tests/ch33/test_measure_and_reprogram.py
    raise NotImplementedError("exercise: simulate_classical_extraction")


def reduction_loss_dfms19(query_budget: int, challenge_space_size: int) -> float:
    """DFMS19 reduction loss for three-move sigma protocols.

    Theorem 2 of Don-Fehr-Majenz-Schaffner 2019 is a measure-and-reprogram
    lemma on pairs ``(x, H(x))``. Combined with the classical
    special-soundness extractor it gives, for a three-move sigma
    protocol with soundness error ``epsilon`` and challenge space of
    size ``|C|``, a Fiat-Shamir-compiled soundness error in the QROM of

        epsilon_qrom <= (2q + 1)^2 * epsilon

    where ``q`` is the adversary's quantum query budget. The loss is
    multiplicative: the reduction multiplies ``epsilon`` rather than
    adding a term beside it. DFMS19 states the coefficient as
    ``O(q^2)`` with a negligible additive residue; DFMS20 sharpens it
    to the exact ``(2q + 1)^2`` with no additive term. The two factors
    of ``(2q + 1)`` come from the hybrid's internal combinatorics
    inside a single run of the lemma, not from two runs of the
    adversary and not from the two-transcript extractor, which runs on
    the classical side. This helper returns ``(2q + 1)^2 / |C|``, which
    is the whole bound at Schnorr's ``epsilon = 1 / |C|``; for any
    other ``epsilon`` multiply ``(2q + 1)^2`` by it.

    Parameters
    ----------
    query_budget
        The adversary's quantum oracle query budget ``q``. Must be
        non-negative.
    challenge_space_size
        The challenge space size ``|C|``. Must be positive.

    Returns
    -------
    float
        The reduction loss ``(2q + 1)^2 / |C|`` as a float.
    """
    # EXERCISE: implement this function.
    #
    # Return (2q + 1)^2 / challenge_space_size as a float: the
    # measure-and-reprogram loss factor of DFMS19 Theorem 2, divided by the
    # challenge space. The loss is multiplicative, epsilon_qrom <= (2q +
    # 1)^2 * epsilon, so what this returns is the whole bound at Schnorr's
    # epsilon = 1 / |C| and the caller multiplies (2q + 1)^2 by any other
    # epsilon. The two factors of (2q + 1) come from the hybrid's internal
    # combinatorics inside a single run of the lemma, not from two separate
    # runs of the adversary, which is why the three-move bound is quadratic
    # and not quartic. Reject a negative query budget and a non-positive
    # challenge space.
    #
    # Reference: Chapter 33, 'The measure-and-reprogram technique'
    #
    # Proved by:
    #   tests/ch33/test_measure_and_reprogram.py
    raise NotImplementedError("exercise: reduction_loss_dfms19")


def parameter_bump_bits(
    query_budget_bits: int,
    challenge_space_bits: int,
    target_pq_bits: int,
) -> int:
    """Return the minimum extra challenge-space bits needed in the QROM.

    Given a target post-quantum soundness of ``target_pq_bits`` and a
    quantum query budget of ``2^query_budget_bits``, the DFMS19 bound

        epsilon_qrom <= (2q + 1)^2 * epsilon

    requires ``(2q + 1)^2 / |C|``, which is that bound at Schnorr's
    ``epsilon = 1 / |C|``, to be at most ``2^(-target_pq_bits)``.
    Setting ``(2q + 1)^2 / |C| <= 2^{-k}`` and taking logs (ignoring
    the constant factor 4 absorbed into the big-O) gives
    ``c_bits >= 2 * query_budget_bits + target_pq_bits``. The function
    returns ``max(0, required_bits - challenge_space_bits)``, i.e., the
    extra bits the deployment must add beyond its current challenge
    space.

    A return value of 0 means the current challenge space already
    clears the DFMS19 quadratic loss at the target PQ bound.
    """
    # EXERCISE: implement this function.
    #
    # Set (2q + 1)^2 / |C| <= 2^{-k} and take logs: the challenge space
    # needs at least 2 * query_budget_bits + target_pq_bits bits. Return how
    # many bits short the current space falls, and zero when it already
    # clears the bound. Approximating 2q + 1 by q, which drops the doubling
    # as well as the +1, is what makes this an approximation rather than the
    # exact threshold; at q = 2^80 and k = 128 it reports 288 where the
    # smallest integer width satisfying the strict inequality is 291, so
    # read the result as a floor and not as a sized deployment parameter.
    # Reject a negative query budget in bits and a non-positive challenge
    # space or target.
    #
    # Reference: Chapter 33, 'Cost of the quantum oracle'
    #
    # Proved by:
    #   tests/ch33/test_measure_and_reprogram.py
    raise NotImplementedError("exercise: parameter_bump_bits")
