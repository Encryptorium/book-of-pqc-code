"""Per-proof gas-cost arithmetic across candidate verifier configurations.

The chapter compares three verifier configurations on the on-chain
gas budget at chain-tip 2026:

- ``legacy-sha256-stark``: a FRI-based STARK verifier with SHA-256 as
  the L4 Fiat-Shamir hash. The chain-tip 2026 ethSTARK reference
  shape: roughly five million gas per proof on Ethereum L1, dominated
  by the FRI verifier loop and the SHA-256 precompile hash calls.
- ``wider-hash-stark``: the same FRI-based STARK verifier with a
  wider-output Fiat-Shamir construction at L4. SHAKE-256 has no
  EVM opcode or precompile at chain-tip 2026, so the pragmatic
  wider-output construction is a multi-pass Keccak-256 over the
  native opcode. The chapter records the cost increase as a
  multiplicative factor against the legacy configuration (a
  bytecode-implemented SHAKE-256 without precompile support
  would carry a much larger factor; the 30% multiplier here is
  an illustrative sensitivity case, not a benchmark).
- ``recursive-stark-wrapper``: the same FRI-based STARK verifier
  wrapped in a recursive proof that batches multiple inner proofs
  into one outer proof. Amortizes the outer verifier cost across the
  batch. The on-chain per-effective-proof cost is the outer verifier
  cost divided by the batch size.

The figures are illustrative anchors at chain-tip 2026, not precise
benchmark numbers. Any production rollup operator measures against
its own deployed verifier; the chapter's arithmetic shows the shape
of the comparison rather than the exact gas value.

Quantity vocabulary used throughout (defined precisely to avoid the
per-block / per-proof / per-batch / per-rollup-cycle collision the
Ch 39 R1 review caught at the consensus surface):

- ``per_proof_gas``: gas to verify one rollup state-transition proof
  on L1. The unit of work the verifier contract performs in one
  invocation in the legacy and wider-hash configurations.
- ``per_block_gas_limit``: the Ethereum L1 block gas limit. Caps the
  total verifier cost the rollup can land in any single L1 block.
- ``per_batch_proof_count``: the number of inner proofs aggregated
  into one outer recursive proof. The recursive wrapper's
  amortization factor.
- ``per_batch_gas``: gas to verify one outer recursive proof on L1.
  Independent of inner proof count once the wrapper is built.
- ``per_effective_proof_gas``: per-batch gas divided by per-batch
  proof count. The figure that compares apples-to-apples against the
  legacy and wider-hash configurations.
- ``per_rollup_cycle_proof_count``: the number of state-transition
  proofs the rollup commits to L1 in one rollup cycle. ZKsync Era
  commits roughly hourly; Starknet commits roughly every two hours
  at chain-tip 2026. The chapter uses one configurable named
  constant so the calculation is unambiguous about whether a figure
  is per-cycle or per-block.
"""

from typing import Dict, List, TypedDict


# Ethereum L1 block gas limit at chain-tip 2026. Anchor: EIP-7935
# EL-client-default recommendation (Informational; Fusaka cycle,
# December 2025) setting the validator-voted default to 60M gas per
# block. Reused from the Ch 37 anchor
# (l1_migration.byte_budget.ETH_BLOCK_GAS_LIMIT) so the two chapters
# carry the same number. Recorded as a constant so a future revision
# can update one figure rather than recompute every per-block
# calculation.
ETH_BLOCK_GAS_LIMIT = 60_000_000

# Per-proof gas figures for each configuration. The chapter cites
# these as illustrative anchors at chain-tip 2026, not precise
# benchmark numbers. The shape of the comparison (legacy < wider-hash
# < recursive amortized) is the load-bearing pedagogy.

# Legacy SHA-256 STARK verifier on Ethereum L1; ethSTARK-shaped.
LEGACY_SHA256_STARK_GAS_PER_PROOF = 5_000_000

# Wider-hash STARK at a multi-pass Keccak-256 transcript (the
# pragmatic on-chain wider-output construction at chain-tip 2026; SHAKE
# has no EVM opcode or precompile). The wider hash output produces
# longer Fiat-Shamir transcripts and roughly 30% more on-chain hashing
# per proof. The 30% multiplier is an illustrative sensitivity case;
# precise figures depend on the deployed FRI parameter set and the
# exact L1 hash precompile schedule. A bytecode-implemented SHAKE-256
# without precompile support would carry a much larger factor (an
# order of magnitude is plausible).
WIDER_HASH_STARK_GAS_PER_PROOF = 6_500_000

# Recursive STARK wrapper: one outer recursive proof verifies a batch
# of inner proofs. The outer verifier on L1 costs roughly seven million
# gas (similar shape to the legacy verifier; the recursion is in the
# circuit, not the L1 verifier). Amortization brings the per-effective-
# proof cost down dramatically.
RECURSIVE_STARK_OUTER_GAS_PER_PROOF = 7_000_000
RECURSIVE_STARK_BATCH_PROOFS = 100

# Default per-rollup-cycle proof count for the chapter's worked
# example. ZKsync Era and Starknet both batch roughly this many state-
# transition proofs into a recursive aggregator per L1 commitment cycle
# at chain-tip 2026. The number is illustrative; rollup operators tune
# it against their throughput target.
DEFAULT_ROLLUP_CYCLE_PROOFS = 100


CONFIGURATIONS = (
    "legacy-sha256-stark",
    "wider-hash-stark",
    "recursive-stark-wrapper",
)


class ConfigEnvelope(TypedDict):
    configuration: str
    per_proof_gas: int
    per_batch_proof_count: int
    per_batch_gas: int
    per_effective_proof_gas: int
    factor_vs_legacy: float
    proofs_per_block_max: int
    rationale: str


def per_proof_gas(configuration: str) -> int:
    """Return the per-proof gas figure for the configuration.

    For the legacy and wider-hash configurations this is the cost to
    verify one proof on L1. For the recursive wrapper this is the
    per-effective-proof cost (outer-proof gas divided by inner-proof
    batch size).
    """
    # EXERCISE: implement this function.
    #
    # Assert the configuration is known, then three branches.
    # legacy-sha256-stark and wider-hash-stark return their module
    # constants, five million and six and a half million gas.
    # recursive-stark-wrapper returns the outer-proof cost floor-divided by
    # the batch size, 7000000 // 100 = 70000, because one outer verifier
    # invocation covers a hundred inner proofs. That last branch is the
    # amortization the chapter's whole gas argument turns on, and it is why
    # this function is named per-proof rather than per-invocation.
    #
    # Reference: Chapter 40, 'Quantify the per-proof gas-cost change'
    #
    # Proved by:
    #   tests/ch40/test_gas_budget.py
    raise NotImplementedError("exercise: per_proof_gas")


def per_batch_gas(configuration: str) -> int:
    """Return the per-batch gas figure for the configuration.

    The legacy and wider-hash configurations have no batch wrapper;
    the per-batch gas equals the per-proof gas times the batch proof
    count. The recursive wrapper has one outer-proof verifier
    invocation per batch.
    """
    # EXERCISE: implement this function.
    #
    # Assert the configuration, then invert the amortization. The recursive
    # wrapper costs exactly one outer-proof verifier invocation per batch,
    # so return RECURSIVE_STARK_OUTER_GAS_PER_PROOF unchanged, flat in the
    # batch size. The legacy and wider-hash configurations have no wrapper,
    # so a batch of the same nominal size costs per_proof_gas times
    # RECURSIVE_STARK_BATCH_PROOFS. Using the same batch constant on both
    # sides is what makes the two columns comparable.
    #
    # Reference: Chapter 40, 'Quantify the per-proof gas-cost change'
    #
    # Proved by:
    #   tests/ch40/test_gas_budget.py
    raise NotImplementedError("exercise: per_batch_gas")


def per_effective_proof_gas(configuration: str) -> int:
    """Per-effective-proof gas: per-batch gas divided by inner-proof count.

    For the legacy and wider-hash configurations this equals
    per_proof_gas (no amortization). For the recursive wrapper this
    is the per-batch gas divided by the inner-proof batch size, which
    is the apples-to-apples comparison against legacy.
    """
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    return per_batch_gas(configuration) // RECURSIVE_STARK_BATCH_PROOFS


def proofs_per_block_max(
    configuration: str, gas_limit: int = ETH_BLOCK_GAS_LIMIT
) -> int:
    """Maximum proofs the configuration can land in one L1 block.

    For the legacy and wider-hash configurations this is the gas
    budget divided by the per-proof gas. For the recursive wrapper
    this is the gas budget divided by the per-batch gas, then
    multiplied by the inner-proof batch size to give the effective
    proof count the rollup can commit per block.
    """
    # EXERCISE: implement this function.
    #
    # Assert the configuration and that the gas limit is positive, rejecting
    # zero rather than dividing by it. The recursive wrapper fills the block
    # with whole outer proofs first (gas_limit //
    # RECURSIVE_STARK_OUTER_GAS_PER_PROOF) and then multiplies by the batch
    # size, so 60000000 // 7000000 = 8 outer proofs carry 800 effective
    # proofs. The other two divide the limit by per_proof_gas directly,
    # giving 12 for legacy and 9 for wider-hash at the 60M EIP-7935 anchor.
    # Floor division throughout, because a partly funded proof does not
    # land.
    #
    # Reference: Chapter 40, 'Quantify the per-proof gas-cost change'
    #
    # Proved by:
    #   tests/ch40/test_gas_budget.py
    raise NotImplementedError("exercise: proofs_per_block_max")


def factor_vs_legacy(configuration: str) -> float:
    """Per-effective-proof gas divided by the legacy per-proof gas.

    A factor below 1 means the configuration is cheaper than legacy
    per effective proof. The recursive wrapper falls below 1 because
    of the batch amortization; the wider-hash configuration sits above
    1 because of the wider-hash overhead.
    """
    # EXERCISE: implement this function.
    #
    # per_effective_proof_gas divided by LEGACY_SHA256_STARK_GAS_PER_PROOF,
    # kept in floating point. Legacy divides by itself and returns exactly
    # 1.0, wider-hash returns 1.3, and the recursive wrapper returns 0.014.
    # The chapter pins that last value, so the numerator has to be the
    # effective per-proof gas rather than the raw outer-proof cost; using
    # the outer cost would report the wrapper as 1.4 times legacy instead of
    # a seventieth of it.
    #
    # Reference: Chapter 40, 'Quantify the per-proof gas-cost change'
    #
    # Proved by:
    #   tests/ch40/test_gas_budget.py
    raise NotImplementedError("exercise: factor_vs_legacy")


def evaluate(configuration: str) -> ConfigEnvelope:
    """Combined per-configuration envelope at chain-tip 2026.

    Returns an eight-field envelope: the configuration name, per-proof
    gas, per-batch proof count, per-batch gas, per-effective-proof gas,
    multiplicative factor against legacy, proofs-per-block maximum at
    the L1 gas limit, and a one-line rationale. The chapter's inline
    Block 2 prints four of the eight as columns.
    """
    # EXERCISE: implement this function.
    #
    # Assemble the eight-field envelope the chapter's Block 2 prints:
    # configuration, per_proof_gas, per_batch_proof_count, per_batch_gas,
    # per_effective_proof_gas, factor_vs_legacy, proofs_per_block_max, and
    # rationale. Delegate the five computed fields to the functions above
    # rather than recomputing any of them, take per_batch_proof_count
    # straight from RECURSIVE_STARK_BATCH_PROOFS, and keep the rationale
    # strings in a dict keyed by configuration so each row explains its own
    # cell: the Grover-weakened SHA-256 transcript for legacy, the
    # wider-output Fiat-Shamir construction for wider-hash, and batch
    # amortization for the wrapper.
    #
    # Reference: Chapter 40, 'Quantify the per-proof gas-cost change'
    #
    # Proved by:
    #   tests/ch40/test_gas_budget.py
    raise NotImplementedError("exercise: evaluate")


def compare_configurations() -> List[ConfigEnvelope]:
    """Flatten the per-configuration envelopes for a chapter table."""
    return [evaluate(c) for c in CONFIGURATIONS]


def per_rollup_cycle_gas(
    configuration: str,
    cycle_proof_count: int = DEFAULT_ROLLUP_CYCLE_PROOFS,
) -> int:
    """Total L1 gas the rollup spends per rollup cycle.

    A rollup cycle is the interval between L1 commitments. Within one
    cycle the rollup verifies ``cycle_proof_count`` inner proofs on L1
    (under the legacy or wider-hash configurations) or one outer
    recursive proof aggregating the inner batch (under the recursive
    wrapper). The function returns the total L1 gas spend across the
    cycle so the chapter can compare cycle costs apples-to-apples.
    """
    # EXERCISE: implement this function.
    #
    # Total L1 gas across one commitment cycle, a different quantity from
    # the per-block figure above. Assert the configuration and that
    # cycle_proof_count is non-negative, allowing zero. Legacy and
    # wider-hash verify every proof separately, so return cycle_proof_count
    # times per_proof_gas: a hundred proofs under legacy is five hundred
    # million gas, roughly eight full blocks at the 60M limit. The recursive
    # wrapper pays one outer proof per batch, so take the ceiling of
    # cycle_proof_count over RECURSIVE_STARK_BATCH_PROOFS and multiply by
    # the outer cost: a hundred proofs is one invocation at seven million
    # gas, a hundred and fifty is two. Ceiling rather than floor, or the
    # trailing partial batch verifies for free.
    #
    # Reference: Chapter 40, 'Quantify the per-proof gas-cost change'
    #
    # Proved by:
    #   tests/ch40/test_gas_budget.py
    raise NotImplementedError("exercise: per_rollup_cycle_gas")
