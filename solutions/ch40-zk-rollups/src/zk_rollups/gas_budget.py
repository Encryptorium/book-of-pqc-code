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
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    if configuration == "legacy-sha256-stark":
        return LEGACY_SHA256_STARK_GAS_PER_PROOF
    if configuration == "wider-hash-stark":
        return WIDER_HASH_STARK_GAS_PER_PROOF
    return RECURSIVE_STARK_OUTER_GAS_PER_PROOF // RECURSIVE_STARK_BATCH_PROOFS


def per_batch_gas(configuration: str) -> int:
    """Return the per-batch gas figure for the configuration.

    The legacy and wider-hash configurations have no batch wrapper;
    the per-batch gas equals the per-proof gas times the batch proof
    count. The recursive wrapper has one outer-proof verifier
    invocation per batch.
    """
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    if configuration == "recursive-stark-wrapper":
        return RECURSIVE_STARK_OUTER_GAS_PER_PROOF
    return per_proof_gas(configuration) * RECURSIVE_STARK_BATCH_PROOFS


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
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    assert gas_limit > 0, "gas limit must be positive"
    if configuration == "recursive-stark-wrapper":
        outer_proofs = gas_limit // RECURSIVE_STARK_OUTER_GAS_PER_PROOF
        return outer_proofs * RECURSIVE_STARK_BATCH_PROOFS
    return gas_limit // per_proof_gas(configuration)


def factor_vs_legacy(configuration: str) -> float:
    """Per-effective-proof gas divided by the legacy per-proof gas.

    A factor below 1 means the configuration is cheaper than legacy
    per effective proof. The recursive wrapper falls below 1 because
    of the batch amortization; the wider-hash configuration sits above
    1 because of the wider-hash overhead.
    """
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    legacy = LEGACY_SHA256_STARK_GAS_PER_PROOF
    return per_effective_proof_gas(configuration) / legacy


def evaluate(configuration: str) -> ConfigEnvelope:
    """Combined per-configuration envelope at chain-tip 2026.

    Returns an eight-field envelope: the configuration name, per-proof
    gas, per-batch proof count, per-batch gas, per-effective-proof gas,
    multiplicative factor against legacy, proofs-per-block maximum at
    the L1 gas limit, and a one-line rationale. The chapter's inline
    Block 2 prints four of the eight as columns.
    """
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    rationales = {
        "legacy-sha256-stark": (
            "ethSTARK-shaped FRI verifier with SHA-256 at L4; "
            "Grover-weakened on the L4 hash"
        ),
        "wider-hash-stark": (
            "FRI verifier with a wider-output Fiat-Shamir at L4 "
            "(multi-pass Keccak-256 over the native opcode at chain-"
            "tip 2026; SHAKE-256 only via a future EIP precompile); "
            "~30% wider-hash illustrative sensitivity against legacy"
        ),
        "recursive-stark-wrapper": (
            "outer recursive proof aggregating an inner batch; "
            "per-effective-proof cost falls under amortization"
        ),
    }
    return {
        "configuration": configuration,
        "per_proof_gas": per_proof_gas(configuration),
        "per_batch_proof_count": RECURSIVE_STARK_BATCH_PROOFS,
        "per_batch_gas": per_batch_gas(configuration),
        "per_effective_proof_gas": per_effective_proof_gas(configuration),
        "factor_vs_legacy": factor_vs_legacy(configuration),
        "proofs_per_block_max": proofs_per_block_max(configuration),
        "rationale": rationales[configuration],
    }


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
    assert configuration in CONFIGURATIONS, (
        f"unknown configuration: {configuration!r}"
    )
    assert cycle_proof_count >= 0, "cycle_proof_count must be non-negative"
    if configuration == "recursive-stark-wrapper":
        # Each batch of RECURSIVE_STARK_BATCH_PROOFS inner proofs costs
        # one outer-proof verifier invocation.
        batches = (cycle_proof_count + RECURSIVE_STARK_BATCH_PROOFS - 1) // RECURSIVE_STARK_BATCH_PROOFS
        return batches * RECURSIVE_STARK_OUTER_GAS_PER_PROOF
    return cycle_proof_count * per_proof_gas(configuration)
