"""Deterministic rank ordering of the candidate primitives by per-block
transaction throughput under either the Bitcoin weight budget or the
Ethereum calldata-gas budget.

The chapter's inline Block 2 calls ``rank("btc")`` and ``rank("eth")``
to print the two orderings side by side. The same candidate set is
shared with ``byte_budget``; this module imports the candidate names
and the budget anchors (4 MB weight limit on Bitcoin, 60 million gas
on Ethereum per EIP-7935 in the Fusaka upgrade) from there.
"""

from typing import List, Tuple

from .byte_budget import (
    CANDIDATES,
    transactions_per_btc_block,
    transactions_per_eth_block_calldata,
)


VALID_BUDGETS = ("btc", "eth")


def rank(budget: str = "btc") -> List[Tuple[str, int]]:
    """Rank candidates by transactions per block, descending.

    ``budget`` is either ``"btc"`` (Bitcoin 4 MB weight) or ``"eth"``
    (Ethereum post-Pectra calldata gas). Ties break alphabetically by
    primitive name so the ordering is deterministic across Python
    runtimes.
    """
    assert budget in VALID_BUDGETS, f"unknown budget: {budget!r}"
    if budget == "btc":
        scored = [(p, transactions_per_btc_block(p)) for p in CANDIDATES]
    else:
        scored = [(p, transactions_per_eth_block_calldata(p)) for p in CANDIDATES]
    return sorted(scored, key=lambda pair: (-pair[1], pair[0]))


def relative_throughput(primitive: str, baseline: str, budget: str = "btc") -> float:
    """Throughput of the candidate as a fraction of the baseline.

    A return value of 0.05 means the candidate processes 5% as many
    transactions per block as the baseline. The chapter uses this
    against ``ECDSA-secp256k1`` to size the migration tax on each
    PQ candidate.
    """
    assert budget in VALID_BUDGETS, f"unknown budget: {budget!r}"
    assert primitive in CANDIDATES, f"unknown primitive: {primitive!r}"
    assert baseline in CANDIDATES, f"unknown baseline: {baseline!r}"
    fn = (
        transactions_per_btc_block
        if budget == "btc"
        else transactions_per_eth_block_calldata
    )
    base = fn(baseline)
    assert base > 0, f"baseline {baseline} has zero throughput on {budget}"
    return fn(primitive) / base
