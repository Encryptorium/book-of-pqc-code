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
    oracle = RandomOracle(output_modulus=output_modulus, seed=seed)
    output = adversary_fn(oracle)
    return {
        "queries": oracle.queries,
        "output": output,
        "oracle": oracle,
    }


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
    first_run = run_adversary(adversary_fn, output_modulus, seed)
    queries = first_run["queries"]
    if len(queries) == 0:
        raise ValueError("adversary made no queries in the first run")

    if measured_index is None:
        measured_index = secrets.randbelow(len(queries))
    if measured_index < 0 or measured_index >= len(queries):
        raise ValueError("measured_index out of range")

    measured_input = queries[measured_index]

    if reprogrammed_value is None:
        reprogrammed_value = secrets.randbelow(output_modulus)
    if reprogrammed_value < 0 or reprogrammed_value >= output_modulus:
        raise ValueError("reprogrammed_value out of range")

    second_oracle = RandomOracle(output_modulus=output_modulus, seed=seed)
    second_oracle.reprogram(measured_input, reprogrammed_value)
    second_output = adversary_fn(second_oracle)

    if not second_oracle.is_queried(measured_input):
        raise ValueError(
            "second run did not query the measured input; "
            "the adversary's query schedule diverged before x*"
        )
    second_response = second_oracle.cached_response(measured_input)

    return {
        "measured_index": measured_index,
        "measured_input": measured_input,
        "reprogrammed_value": reprogrammed_value,
        "first_queries": first_run["queries"],
        "first_output": first_run["output"],
        "second_queries": second_oracle.queries,
        "second_output": second_output,
        "second_response_at_x_star": second_response,
        "consistent": second_response == reprogrammed_value,
    }


def reduction_loss_dfms19(query_budget: int, challenge_space_size: int) -> float:
    """DFMS19 reduction loss for three-move sigma protocols.

    Theorem 2 of Don-Fehr-Majenz-Schaffner 2019 (informal): for a
    three-move sigma protocol with soundness error ``epsilon`` and
    challenge space of size ``|C|``, the Fiat-Shamir-compiled protocol
    in the QROM has soundness error

        epsilon_qrom <= epsilon + (2q + 1)^2 / |C|

    where ``q`` is the adversary's quantum query budget. The quadratic
    term is the measure-and-reprogram loss factor, arising from two
    independent index-guesses in the two-transcript Sigma-protocol
    extractor. This helper returns the quadratic loss term only;
    callers add the interactive soundness error ``epsilon`` to obtain
    the full bound.

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
        The reduction loss term ``(2q + 1)^2 / |C|`` as a float.
    """
    if query_budget < 0:
        raise ValueError("query_budget must be non-negative")
    if challenge_space_size <= 0:
        raise ValueError("challenge_space_size must be positive")
    return ((2 * query_budget + 1) ** 2) / challenge_space_size


def parameter_bump_bits(
    query_budget_bits: int,
    challenge_space_bits: int,
    target_pq_bits: int,
) -> int:
    """Return the minimum extra challenge-space bits needed in the QROM.

    Given a target post-quantum soundness of ``target_pq_bits`` and a
    quantum query budget of ``2^query_budget_bits``, the DFMS19 bound

        epsilon_qrom <= epsilon + (2q + 1)^2 / |C|

    requires the leading term to be at most ``2^(-target_pq_bits)``.
    Setting ``(2q + 1)^2 / |C| <= 2^{-k}`` and taking logs (ignoring
    the constant factor 4 absorbed into the big-O) gives
    ``c_bits >= 2 * query_budget_bits + target_pq_bits``. The function
    returns ``max(0, required_bits - challenge_space_bits)``, i.e., the
    extra bits the deployment must add beyond its current challenge
    space.

    A return value of 0 means the current challenge space already
    clears the DFMS19 quadratic loss at the target PQ bound.
    """
    if query_budget_bits < 0:
        raise ValueError("query_budget_bits must be non-negative")
    if challenge_space_bits <= 0:
        raise ValueError("challenge_space_bits must be positive")
    if target_pq_bits <= 0:
        raise ValueError("target_pq_bits must be positive")
    required = 2 * query_budget_bits + target_pq_bits
    if required <= challenge_space_bits:
        return 0
    return required - challenge_space_bits
