"""FRI proximity with per-round Fiat-Shamir challenges for Chapter 34.

Chapter 32 built the FRI folding and consistency mechanics as a bare
interactive oracle proof: the verifier sent the fold challenges. This
module carries the same mechanics into the non-interactive setting.
Each round's beta challenge is squeezed from a transcript. Each
round's folded codeword is Merkle-committed; the commitment's root is
absorbed into the transcript before the next squeeze. Once every
commitment is absorbed, the prover searches for a grinding nonce whose
transcript hash has a configurable number of trailing zero bits and
absorbs it; only then are the query positions squeezed, so each query
set a forger sees costs a fresh proof-of-work (Track 2 round 12,
P1-02: grinding drawn after the queries priced nothing, because the
positions were already fixed before the nonce existed).

Every query opens both members of its fold pair against the round's
Merkle root: the queried leaf and the sibling at ``leaf_index + half``
each carry their own authentication path (Track 2 round 12, P1-01: an
unauthenticated sibling let a prover choose the fold's second input
freely, and a codeword of degree 8 passed a degree-below-8 claim with
every leaf and path genuine).

Symbols (reserved per Chapter 34's symbol table):

- ``N`` is the LDE domain size (``len(initial_domain)``).
- ``r_FRI`` is the number of folding rounds, ``log_2(L)`` for a
  codeword claimed to have degree below the trace length ``L`` (3 for
  the toy: 32 points fold to 4, on which the honest codeword is
  constant). One fold more would accept degree below ``2L``.
- ``mu`` is the number of queries per round (``num_queries``).
- ``g`` is the grinding-bit count.

The module does not import from Chapter 32's package. It re-implements
the fold mechanic in place, both so the chapter remains self-contained
and so Chapter 34 can adapt field arithmetic to the LDE coset without
coupling to Chapter 32's choices.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .lde import mod_inv
from .transcript import Transcript


@dataclass
class QueryOpening:
    """One round's opening at a single query index.

    ``leaf_index`` names the position in the round's codeword.
    ``leaf_value`` is the field element stored at that position.
    ``sibling_value`` is the field element at the paired index
    ``(leaf_index + half) mod size`` (the sibling required for
    fold-consistency). ``merkle_path`` is the list of sibling digests
    from the leaf up to the round's Merkle root, and ``sibling_path``
    is the same for the paired index. Both values are authenticated:
    the fold-consistency equation has two inputs, and a verifier that
    binds only one of them lets the prover choose the other.
    """

    leaf_index: int
    leaf_value: int
    sibling_value: int
    merkle_path: list[bytes]
    sibling_path: list[bytes]


@dataclass
class FRIProof:
    """FRI proof produced by ``fri_prove``.

    ``commitments[j]`` is the Merkle root of round ``j``'s codeword,
    for ``j`` in ``range(r_FRI + 1)``. ``query_openings[j][k]`` is the
    opening of round ``j`` at the ``k``-th query. ``final_value`` is
    the folded codeword after the last round (a single field element
    when the protocol folds to a constant; otherwise the first element
    of the final domain, along with the implicit rest of the codeword
    that the verifier checks against the final Merkle root).
    ``grinding_nonce`` is the nonce whose transcript hash has the
    required trailing-zero bit count; it is absorbed before the query
    positions are squeezed, so it decides which positions are queried.
    """

    commitments: list[bytes]
    query_openings: list[list[QueryOpening]]
    final_codeword: list[int]
    grinding_nonce: int


def _encode_field(value: int, prime: int) -> bytes:
    """Serialize a field element to a fixed 8-byte big-endian integer."""
    if prime < 2:
        raise ValueError("prime must be at least two")
    return (value % prime).to_bytes(8, "big")


def _hash_leaf(value: int, prime: int) -> bytes:
    """SHA-256 of the 8-byte-encoded field element."""
    return hashlib.sha256(_encode_field(value, prime)).digest()


def _merkle_tree(codeword: list[int], prime: int) -> list[list[bytes]]:
    """Build a binary Merkle tree over the codeword. Pads to a power of two."""
    n = len(codeword)
    if n == 0:
        raise ValueError("codeword must be non-empty")
    if n & (n - 1):
        raise ValueError("codeword length must be a power of two")
    leaves = [_hash_leaf(v, prime) for v in codeword]
    levels = [leaves]
    while len(levels[-1]) > 1:
        current = levels[-1]
        next_level = [
            hashlib.sha256(current[i] + current[i + 1]).digest()
            for i in range(0, len(current), 2)
        ]
        levels.append(next_level)
    return levels


def commit_codeword(codeword: list[int], prime: int) -> tuple[bytes, list[list[bytes]]]:
    """Merkle-commit a codeword; returns (root, full_tree_levels)."""
    # EXERCISE: implement this function.
    #
    # Delegate the tree construction to the module's _merkle_tree helper and
    # return the pair (root, levels): the root is the single digest on the
    # last level. Returning every level rather than the root alone is what
    # lets an opening be cut later without rebuilding the tree, which is why
    # the prover keeps one tree per round alongside each commitment. The
    # input validation the helper performs (non-empty, power-of-two length)
    # is the whole of this routine's error contract.
    #
    # Reference: Chapter 34, '4.3 FRI with Fiat-Shamir challenges'
    #
    # Proved by:
    #   tests/ch34/test_fri_full.py
    raise NotImplementedError("exercise: commit_codeword")


def _merkle_path(tree: list[list[bytes]], index: int) -> list[bytes]:
    """Return the sibling-digest path from leaf ``index`` to the root."""
    path: list[bytes] = []
    idx = index
    for level in tree[:-1]:
        sibling_idx = idx ^ 1
        path.append(level[sibling_idx])
        idx //= 2
    return path


def _verify_merkle_path(
    root: bytes, leaf_digest: bytes, index: int, path: list[bytes]
) -> bool:
    """Reconstruct the Merkle root from a leaf digest and the sibling path."""
    current = leaf_digest
    idx = index
    for sibling in path:
        if idx % 2 == 0:
            current = hashlib.sha256(current + sibling).digest()
        else:
            current = hashlib.sha256(sibling + current).digest()
        idx //= 2
    return current == root


def _fold_codeword(
    codeword: list[int],
    domain: list[int],
    beta: int,
    prime: int,
) -> tuple[list[int], list[int]]:
    """Fold one round: f'(x^2) = even + beta * odd / x, for paired (x, -x).

    The domain is assumed to be laid out so that ``domain[i]`` and
    ``domain[i + half]`` are a negation pair. This is the same layout
    as Chapter 32's ``fri.fold_once``.
    """
    # EXERCISE: implement this function.
    #
    # One FRI round. Pair domain[i] with domain[i + half], which is
    # -domain[i] in a cyclic domain laid out as consecutive powers of one
    # generator, and replace the pair with a single value at x^2. With even
    # = (f(x) + f(-x))/2 and odd = (f(x) - f(-x))/(2x), the folded value is
    # even + beta * odd. Divide by inverting 2 and x modulo prime rather
    # than by literal division. The new domain is the squares of the first
    # half, so each round halves both the codeword and its degree bound.
    # Reject a domain and codeword of different lengths, and a size that is
    # not a power of two above one.
    #
    # Reference: Chapter 34, '4.3 FRI with Fiat-Shamir challenges' (Block 4)
    #
    # Proved by:
    #   tests/ch34/test_fri_full.py
    raise NotImplementedError("exercise: _fold_codeword")


def _squeeze_beta(transcript: Transcript, prime: int, round_index: int) -> int:
    """Draw a FRI fold challenge from the transcript."""
    return transcript.squeeze_int(b"fri-beta-" + round_index.to_bytes(4, "big"), prime)


def _check_grinding(state: bytes, nonce: int, grinding_bits: int) -> bool:
    """Return True if ``sha256(state || nonce)`` has ``grinding_bits`` trailing zero bits."""
    # EXERCISE: implement this function.
    #
    # Return whether sha256(state || nonce) has at least grinding_bits
    # trailing zero bits, with the nonce encoded as 8 big-endian bytes. Read
    # the digest as one big-endian integer and mask it against (1 <<
    # grinding_bits) - 1; the result is zero exactly when the low bits are
    # clear. Zero grinding bits accepts every nonce. Reject a negative bit
    # count. The point is cost, not secrecy: each forging attempt that
    # reaches the query-selection phase pays 2^g hashes, which is the factor
    # by which grinding attenuates the query-miss term of the soundness
    # budget and nothing else.
    #
    # Reference: Chapter 34, '4.4 Transcript and grinding'
    #
    # Proved by:
    #   tests/ch34/test_fri_full.py
    raise NotImplementedError("exercise: _check_grinding")


def _find_grinding_nonce(state: bytes, grinding_bits: int) -> int:
    """Search for the smallest nonce satisfying the grinding condition."""
    if grinding_bits < 0:
        raise ValueError("grinding_bits must be non-negative")
    if grinding_bits == 0:
        return 0
    nonce = 0
    while not _check_grinding(state, nonce, grinding_bits):
        nonce += 1
    return nonce


def _rounds_for_degree_bound(n: int, degree_bound: int | None) -> int:
    """Number of folds that turn "degree < degree_bound" into "constant".

    Each fold halves the degree bound, so log_2(degree_bound) folds reduce
    a polynomial of degree less than degree_bound to a constant on the final
    domain of n / degree_bound points. One fold more would also fold any
    polynomial of degree less than 2 * degree_bound to a constant, so the
    constancy check at the end would accept twice the intended degree.
    degree_bound must be a power of two in [2, n / 2]; None means n / 4,
    the STARK's rate-1/4 default, floored at 2 so that a four-point
    domain, the smallest the package accepts, still gets its one fold.
    """
    if degree_bound is None:
        degree_bound = max(2, n // 4)
    if degree_bound < 2 or degree_bound & (degree_bound - 1) or degree_bound > n // 2:
        raise ValueError("degree_bound must be a power of two in [2, n / 2]")
    return degree_bound.bit_length() - 1


def fri_prove(
    initial_codeword: list[int],
    initial_domain: list[int],
    prime: int,
    transcript: Transcript,
    num_queries: int,
    grinding_bits: int,
    num_rounds: int | None = None,
    degree_bound: int | None = None,
) -> FRIProof:
    """Produce a FRI proof for ``initial_codeword`` over ``initial_domain``.

    Folds the codeword ``log_2(degree_bound)`` times, committing to each
    intermediate codeword; ``degree_bound`` defaults to a quarter of the
    domain size, the STARK's rate. ``num_rounds`` sets the fold count
    directly instead and cannot be combined with ``degree_bound``. Once
    every commitment is absorbed, finds the grinding nonce, absorbs it,
    and only then squeezes the query positions. For each fold round
    ``j`` and each of the ``num_queries`` queried positions, records the
    query's leaf and sibling values plus a Merkle path for each.

    Raises ValueError for non-power-of-two domain sizes, mismatched
    codeword and domain lengths, or non-positive ``num_queries``.
    """
    # EXERCISE: implement this function.
    #
    # Commit, fold, open, grind. Merkle-commit the initial codeword and
    # absorb its root under a round-0 label. Then for each round, squeeze
    # that round's beta from the transcript, fold the current codeword and
    # domain with it, commit the folded result, and absorb the new root
    # before the next squeeze; binding each root before its successor
    # challenge is what stops a prover picking a beta that cancels a flawed
    # codeword. Squeeze num_queries positions against the initial domain
    # size, then for every round record each position reduced modulo that
    # round's size, along with the leaf value there, the value at the paired
    # index half a round-size away, and the Merkle path. Finally search for
    # a grinding nonce over the transcript state and absorb it. Derive the
    # fold count from the degree bound: log2(degree_bound) folds turn degree
    # below degree_bound into a constant on N / degree_bound points, and one
    # fold more would flatten degree below 2 * degree_bound as well, so the
    # count is what makes the final constancy check test the claimed degree
    # and not twice it. Default degree_bound to N / 4, the STARK's rate,
    # floored at 2 so a four-point domain still gets its one fold, and
    # reject a bound that is not a power of two in [2, N / 2]; accept
    # num_rounds as a direct override in [1, log2(N) - 1], but not together
    # with degree_bound. Reject mismatched codeword and domain lengths, a
    # domain below size four or not a power of two, num_queries below one,
    # and negative grinding bits.
    #
    # Reference: Chapter 34, '4.3 FRI with Fiat-Shamir challenges' and '4.4 Transcript and grinding'
    #
    # Proved by:
    #   tests/ch34/test_fri_full.py
    #   tests/ch34/test_stark_roundtrip.py
    raise NotImplementedError("exercise: fri_prove")


def fri_verify(
    proof: FRIProof,
    initial_domain: list[int],
    prime: int,
    transcript: Transcript,
    num_queries: int,
    grinding_bits: int,
    num_rounds: int | None = None,
    degree_bound: int | None = None,
) -> bool:
    """Verify a FRI proof produced by ``fri_prove``.

    Replays every transcript interaction, rederiving every beta
    challenge, checking and absorbing the grinding nonce, and only then
    rederiving every query position. ``degree_bound`` and
    ``num_rounds`` mean what they mean in ``fri_prove`` and must match
    the prover's. Checks both Merkle paths of every opening, the
    queried leaf's and its fold partner's, and each round-to-round fold
    consistency. Returns True on accept, False on any check failure.
    Raises ValueError for structurally malformed proofs.
    """
    # EXERCISE: implement this function.
    #
    # Rederive everything the prover claimed instead of trusting it. Replay
    # the transcript in the prover's exact order (absorb root 0, then
    # alternate squeezing beta_j and absorbing root j+1), squeeze the same
    # query positions, check the grinding nonce against the state before
    # absorbing it, and rebuild each round's domain by squaring the first
    # half of the previous one. Then per query, per round: the opening's
    # leaf index must equal the query position reduced modulo that round's
    # size, and its Merkle path must rebuild that round's committed root.
    # Across consecutive rounds, refold the pair by hand with that round's
    # beta and require the result to equal the successor round's opened leaf
    # value at the successor index. Finally the final codeword must recommit
    # to the last root and must be constant, because log2(degree_bound)
    # folds of a codeword close to a polynomial of degree below degree_bound
    # leave degree below one; derive the round count from degree_bound
    # exactly as the prover does, since a verifier that folds once more
    # accepts twice the claimed degree. Return False on any of those
    # failures; raise ValueError only for structural malformation, such as a
    # commitment or opening count that does not match num_rounds.
    #
    # Reference: Chapter 34, '4.3 FRI with Fiat-Shamir challenges' and '4.4 Transcript and grinding'
    #
    # Proved by:
    #   tests/ch34/test_fri_full.py
    #   tests/ch34/test_stark_roundtrip.py
    raise NotImplementedError("exercise: fri_verify")
