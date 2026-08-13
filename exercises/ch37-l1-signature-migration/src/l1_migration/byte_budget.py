"""Per-transaction byte budget across a fixed four-element candidate set.

The chapter's running example pins four candidate primitives for the
Strand transaction surface:

- ``ECDSA-secp256k1`` is the legacy baseline. The 64-byte signature
  size matches the BIP-340 canonical 64-byte form used by Taproot
  key-path spends. Pre-Taproot DER-encoded ECDSA signatures range
  70-72 bytes; the chapter prose calls this out and uses 64 bytes
  as the toy-model lower-bound figure for the comparison. Taproot
  key-path spends keep the tweaked public key in the output script
  (on-chain since UTXO funding) and reveal only the signature in
  the witness on spend.
- ``ML-DSA-65`` is the lattice candidate per FIPS 204 (Table 2):
  3309-byte signature, 1952-byte public key.
- ``SLH-DSA-128s`` is the hash-based candidate per FIPS 205 (Table 2):
  7856-byte signature, 32-byte public key. The 's' parameter set is
  the ``small'' tradeoff (smaller signatures than 128f at the cost
  of slower signing).
- ``Ed25519+ML-DSA-65`` is the composite-cutover candidate per the
  Ch 27 framing: classical Ed25519 (64-byte sig, 32-byte public key)
  alongside ML-DSA-65 in a single transaction. The composite buys
  defense-in-depth during the cutover window at the cost of
  additional signature bytes and verification work.

The Bitcoin model assumes any future post-quantum signature soft
fork uses a P2WPKH-style commit-then-reveal output pattern: the
output script hash-commits to the post-quantum public key, and the
witness reveals both the public key and the signature on spend.
BIP-360 (Pay-to-Merkle-Root, P2MR) does not itself define a
post-quantum signature scheme; the PQ-signature soft fork is
treated here as a separate future proposal layered on top of
P2MR-style script outputs. The BIP's draft version is deliberately
not pinned here: it moves faster than this module does, and the
chapter and its bibliography entry are the two places that carry it.

Bitcoin block budget anchored at the 4 MB weight unit limit (1 weight
unit per witness byte, 4 weight units per non-witness byte). Ethereum
block budget anchored to the chain-tip 2026 60-million-gas limit set
by EIP-7935 in the Fusaka upgrade (December 2025), recorded here as
a constant so the chapter can revise the anchor without re-deriving
every figure.
"""

from typing import Dict, TypedDict


class CandidateSizes(TypedDict):
    sig_bytes: int
    pk_bytes: int
    deployment_shape: str
    witness_reveals_pk: bool


CANDIDATES: Dict[str, CandidateSizes] = {
    "ECDSA-secp256k1": {
        "sig_bytes": 64,
        "pk_bytes": 33,
        "deployment_shape": "deployed-baseline",
        "witness_reveals_pk": False,
    },
    "ML-DSA-65": {
        "sig_bytes": 3309,
        "pk_bytes": 1952,
        "deployment_shape": "soft-fork-or-account-abstraction",
        "witness_reveals_pk": True,
    },
    "SLH-DSA-128s": {
        "sig_bytes": 7856,
        "pk_bytes": 32,
        "deployment_shape": "soft-fork-or-account-abstraction",
        "witness_reveals_pk": True,
    },
    "Ed25519+ML-DSA-65": {
        "sig_bytes": 64 + 3309,
        "pk_bytes": 32 + 1952,
        "deployment_shape": "composite-cutover",
        "witness_reveals_pk": True,
    },
}

BTC_BLOCK_WEIGHT_LIMIT = 4_000_000
"""Bitcoin block weight limit in weight units. Witness data weighs 1
weight unit per byte; non-witness data weighs 4 weight units per byte."""

BTC_TX_OVERHEAD_WU = 200
"""Non-signature weight per typical 1-in-1-out segwit transaction
(input scaffolding, output scaffolding, sighash byte, locktime). Used
as a fixed per-tx overhead in the per-block throughput calculation."""

ETH_BLOCK_GAS_LIMIT = 60_000_000
"""Ethereum block gas limit at chain-tip 2026, set by EIP-7935 in the
Fusaka upgrade (December 2025). Recorded as a constant so the chapter's
anchor is unambiguous and so a future revision can update one number
rather than recompute every figure."""

ETH_TX_BASE_GAS = 21_000
"""Base gas cost for any Ethereum transaction. Independent of payload."""

ETH_GAS_PER_NONZERO_CALLDATA_BYTE = 16
"""Gas cost per non-zero calldata byte under the legacy standard path
(the execution-gas-dominant branch of the EIP-7623 max()). Used as
the marginal-model upper bound for the signature-bytes calldata
charge; signature bytes are uniformly random in practice, so a small
fraction of bytes ride at the 4-gas zero-byte rate and the 16-gas
figure overstates calldata cost by a few percent."""

ETH_GAS_TOKENS_PER_NONZERO_BYTE = 4
"""Per-byte EIP-7623 token count for a nonzero calldata byte. The
EIP defines tokens_in_calldata = zero_bytes + 4*nonzero_bytes."""

ETH_GAS_FLOOR_PER_TOKEN = 10
"""EIP-7623 TOTAL_COST_FLOOR_PER_TOKEN. The Pectra-included data
floor is 10 gas per token; when this branch of the max() wins, an
all-nonzero calldata payload effectively costs
ETH_GAS_TOKENS_PER_NONZERO_BYTE * ETH_GAS_FLOOR_PER_TOKEN = 40 gas
per nonzero byte. ERC-4337 UserOperations land in the floor regime
when their verifier executes few EVM operations relative to the
signature size."""


def signature_bytes(primitive: str) -> int:
    """Return the per-signature byte size for the candidate primitive."""
    # EXERCISE: implement this function.
    #
    # Assert the name is a key of CANDIDATES so an unknown primitive crashes
    # with the name echoed back, then return that row's sig_bytes. The four
    # figures are fixed by standards rather than derived: 64 for the BIP-340
    # canonical ECDSA form, 3309 for ML-DSA-65 per FIPS 204 Table 2, 7856
    # for SLH-DSA-128s per FIPS 205 Table 2, and 64 + 3309 for the
    # composite.
    #
    # Reference: Chapter 37, 'Sizes and primitives at chain-tip 2026'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: signature_bytes")


def public_key_bytes(primitive: str) -> int:
    """Return the public-key byte size for the candidate primitive."""
    # EXERCISE: implement this function.
    #
    # The same lookup against pk_bytes, with the same assert. Note how far
    # apart the two hash-based and lattice rows sit: SLH-DSA-128s pairs its
    # 7856-byte signature with a 32-byte public key, while ML-DSA-65 pairs a
    # smaller signature with a 1952-byte key. That asymmetry is what makes
    # the Bitcoin witness model, which reveals both, rank the two
    # differently than signature size alone would.
    #
    # Reference: Chapter 37, 'Sizes and primitives at chain-tip 2026'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: public_key_bytes")


def witness_reveals_pk(primitive: str) -> bool:
    """Return whether the spend witness must reveal the public key.

    The legacy ECDSA-secp256k1 baseline is modeled after Taproot
    key-path spends: the tweaked public key sits in the output
    script, so the witness carries the signature only. The
    post-quantum candidates are modeled after a P2WPKH-style
    commit-then-reveal pattern: the output script hash-commits to
    the public key, and the witness reveals both the public key and
    the signature on spend.
    """
    # EXERCISE: implement this function.
    #
    # Return the row's witness_reveals_pk flag. It is False only for
    # ECDSA-secp256k1, which the chapter models as a Taproot key-path spend:
    # the tweaked public key already sits in the output script, so the spend
    # witness carries the signature alone. The three post-quantum rows are
    # modeled as P2WPKH-style commit-then-reveal, where the output script
    # hash-commits to the public key and the witness reveals both key and
    # signature at spend.
    #
    # Reference: Chapter 37, 'Design the address format'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: witness_reveals_pk")


def witness_bytes(primitive: str) -> int:
    """Return the per-spend witness byte cost for the candidate.

    Sums signature bytes plus public-key bytes when the output type
    hash-commits to the public key (the P2WPKH-style pattern any
    future PQ signature soft fork is assumed to follow).
    """
    # EXERCISE: implement this function.
    #
    # Start from signature_bytes and add public_key_bytes when
    # witness_reveals_pk is true. That one conditional is the whole Bitcoin
    # cost model: ML-DSA-65 costs 5261 witness bytes (3309 of signature plus
    # 1952 of public key) where ECDSA costs 64.
    #
    # Reference: Chapter 37, 'A Strand transaction migrating to ML-DSA-65'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: witness_bytes")


def transactions_per_btc_block(
    primitive: str, tx_overhead_wu: int = BTC_TX_OVERHEAD_WU
) -> int:
    """Per-block transaction throughput on Bitcoin under the candidate.

    Models each transaction as ``tx_overhead_wu`` weight units plus
    the candidate's witness bytes at 1 weight unit per witness byte.
    For ECDSA-secp256k1 (Taproot key-path baseline) the witness is the
    signature alone; for the post-quantum candidates the witness is
    the public key plus the signature, matching a P2WPKH-style
    commit-then-reveal output pattern.
    """
    # EXERCISE: implement this function.
    #
    # Witness data weighs one weight unit per byte, so a spend costs
    # tx_overhead_wu plus witness_bytes(primitive) weight units.
    # Floor-divide BTC_BLOCK_WEIGHT_LIMIT by that total. Use integer
    # division rather than rounding: a partial transaction does not fit in a
    # block. ECDSA lands at 4000000 // 264 = 15151 and ML-DSA-65 at 4000000
    # // 5461 = 732.
    #
    # Reference: Chapter 37, 'Choose the candidate'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    #   tests/ch37/test_throughput_compare.py
    raise NotImplementedError("exercise: transactions_per_btc_block")


def calldata_gas(primitive: str) -> int:
    """Marginal calldata gas cost for one signature on Ethereum.

    Signature bytes ride in calldata at the non-zero-byte cost under
    the execution-gas-dominant branch of the EIP-7623 max(). The
    figure is an upper bound for the marginal regime; in practice a
    small fraction of bytes will be zero and pay 4 gas instead of 16.
    The public key is assumed to live in the smart-contract wallet's
    state (paid at deployment), not in calldata per transaction.
    """
    # EXERCISE: implement this function.
    #
    # Signature bytes ride in calldata at ETH_GAS_PER_NONZERO_CALLDATA_BYTE,
    # so multiply the two. The public key is not charged here: the Ethereum
    # model assumes the smart-contract wallet holds it in contract state,
    # paid once at deployment rather than per user operation, which is why
    # the Ethereum column drops less steeply than the Bitcoin one.
    #
    # Reference: Chapter 37, 'Choose the candidate'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: calldata_gas")


def calldata_floor_gas(primitive: str) -> int:
    """EIP-7623 calldata-floor gas cost for one all-nonzero signature.

    Applies the Pectra-included data floor: per-tx gas = base +
    TOTAL_COST_FLOOR_PER_TOKEN * tokens_in_calldata, with each
    nonzero byte counting as four tokens. For an all-nonzero
    signature payload this returns 40 * sig_bytes, which is the
    effective per-byte cost when the floor branch of the EIP-7623
    max() wins (calldata-dominant transactions).
    """
    # EXERCISE: implement this function.
    #
    # The EIP-7623 floor branch prices tokens rather than bytes: each
    # nonzero byte counts as ETH_GAS_TOKENS_PER_NONZERO_BYTE tokens and each
    # token costs ETH_GAS_FLOOR_PER_TOKEN. Multiply signature bytes by the
    # first constant to get tokens, then by the second to get gas. For an
    # all-nonzero payload that works out to 40 gas per byte against the
    # marginal model's 16.
    #
    # Reference: Chapter 37, 'Choose the candidate'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: calldata_floor_gas")


def transactions_per_eth_block_calldata(
    primitive: str, gas_limit: int = ETH_BLOCK_GAS_LIMIT
) -> int:
    """Per-block tx throughput under the EIP-7623 marginal model.

    Models each transaction as ``ETH_TX_BASE_GAS`` + signature
    calldata at the legacy 16-gas-per-nonzero-byte standard rate.
    Assumes the smart-contract wallet stores the public key in
    contract state at deployment, so only the signature rides in
    calldata per user operation. Applies on the execution-gas-
    dominant branch of the EIP-7623 max(); ERC-4337 UserOperations
    whose PQ-verifier consumes substantial EVM gas land here.
    Excludes the verification cost itself; PQ verification without
    a precompile dominates this figure once it lands.
    """
    # EXERCISE: implement this function.
    #
    # Per-transaction gas is ETH_TX_BASE_GAS plus calldata_gas(primitive);
    # floor-divide gas_limit by that. The 21000-gas base is why Ethereum's
    # throughput drop is shallower than Bitcoin's: it dwarfs ECDSA's 1024
    # gas of signature calldata, so the baseline row is base-dominated while
    # the post-quantum rows are calldata-dominated.
    #
    # Reference: Chapter 37, 'Choose the candidate'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    #   tests/ch37/test_throughput_compare.py
    raise NotImplementedError("exercise: transactions_per_eth_block_calldata")


def transactions_per_eth_block_calldata_floor(
    primitive: str, gas_limit: int = ETH_BLOCK_GAS_LIMIT
) -> int:
    """Per-block tx throughput under the EIP-7623 data-floor model.

    Models each transaction as ``ETH_TX_BASE_GAS`` + the EIP-7623
    calldata floor (effectively 40 gas per nonzero byte for an
    all-nonzero signature payload). Applies when the floor branch
    of the max() wins, which is the calldata-dominant regime for
    ERC-4337 UserOperations whose verifier executes few EVM
    operations relative to the signature size.
    """
    # EXERCISE: implement this function.
    #
    # The same shape as the marginal model with calldata_floor_gas
    # substituted for calldata_gas. Because 40 gas per byte exceeds 16, this
    # branch admits strictly fewer transactions per block for every
    # candidate, which is the bound an ERC-4337 UserOperation actually pays
    # when its verifier executes few EVM operations relative to the
    # signature size.
    #
    # Reference: Chapter 37, 'Choose the candidate'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: transactions_per_eth_block_calldata_floor")


def evaluate(primitive: str) -> dict:
    """Combined per-tx and per-block envelope for the candidate.

    Returns a dict with the pedagogical numbers the chapter's
    inline Block 1 prints (signature bytes, public key bytes,
    witness bytes, per-Bitcoin-block throughput, per-Ethereum-block
    throughput under both the marginal calldata model and the
    EIP-7623 data-floor model).
    """
    # EXERCISE: implement this function.
    #
    # Assemble the dict the chapter's Block 1 prints: primitive, sig_bytes,
    # pk_bytes, witness_bytes, btc_tx_per_block, eth_tx_per_block_calldata,
    # eth_tx_per_block_calldata_floor, deployment_shape. Every numeric field
    # delegates to the function that computes it rather than re-deriving
    # from CANDIDATES, so a change to the witness model propagates in one
    # place; deployment_shape is read straight off the table.
    #
    # Reference: Chapter 37, 'Choose the candidate'
    #
    # Proved by:
    #   tests/ch37/test_byte_budget.py
    raise NotImplementedError("exercise: evaluate")
