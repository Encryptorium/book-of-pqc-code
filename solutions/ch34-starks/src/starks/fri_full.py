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
    tree = _merkle_tree(codeword, prime)
    return tree[-1][0], tree


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
    n = len(domain)
    if n != len(codeword):
        raise ValueError("domain and codeword must have the same length")
    if n < 2 or (n & (n - 1)):
        raise ValueError("domain size must be a power of two greater than one")
    half = n // 2
    two_inv = mod_inv(2, prime)
    new_codeword: list[int] = []
    new_domain: list[int] = []
    for i in range(half):
        x = domain[i]
        fx = codeword[i]
        f_neg = codeword[i + half]
        even = ((fx + f_neg) * two_inv) % prime
        odd = ((fx - f_neg) * two_inv) % prime
        odd = (odd * mod_inv(x, prime)) % prime
        new_codeword.append((even + beta * odd) % prime)
        new_domain.append((x * x) % prime)
    return new_codeword, new_domain


def _squeeze_beta(transcript: Transcript, prime: int, round_index: int) -> int:
    """Draw a FRI fold challenge from the transcript."""
    return transcript.squeeze_int(b"fri-beta-" + round_index.to_bytes(4, "big"), prime)


def _check_grinding(state: bytes, nonce: int, grinding_bits: int) -> bool:
    """Return True if ``sha256(state || nonce)`` has ``grinding_bits`` trailing zero bits."""
    if grinding_bits < 0:
        raise ValueError("grinding_bits must be non-negative")
    if not 0 <= nonce < (1 << 64):
        raise ValueError("grinding nonce must fit in 8 bytes")
    if grinding_bits == 0:
        return True
    digest = hashlib.sha256(state + nonce.to_bytes(8, "big")).digest()
    value = int.from_bytes(digest, "big")
    mask = (1 << grinding_bits) - 1
    return (value & mask) == 0


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
    n = len(initial_domain)
    if n != len(initial_codeword):
        raise ValueError("codeword and domain must have the same length")
    if n < 4 or (n & (n - 1)):
        raise ValueError("domain size must be a power of two at least four")
    if num_queries < 1:
        raise ValueError("num_queries must be at least one")
    if grinding_bits < 0:
        raise ValueError("grinding_bits must be non-negative")

    max_rounds = n.bit_length() - 2  # log_2(n) - 1: the final domain has 2 points
    if num_rounds is None:
        num_rounds = _rounds_for_degree_bound(n, degree_bound)
    elif degree_bound is not None:
        raise ValueError("give num_rounds or degree_bound, not both")
    if num_rounds < 1 or num_rounds > max_rounds:
        raise ValueError(
            f"num_rounds must be in [1, {max_rounds}] for domain size {n}"
        )

    codewords = [list(initial_codeword)]
    domains = [list(initial_domain)]
    trees = []
    commitments = []

    # Commit initial codeword.
    root, tree = commit_codeword(initial_codeword, prime)
    commitments.append(root)
    trees.append(tree)
    transcript.absorb(b"fri-commit-0", root)

    # Fold rounds.
    for j in range(num_rounds):
        beta = _squeeze_beta(transcript, prime, j)
        new_codeword, new_domain = _fold_codeword(codewords[-1], domains[-1], beta, prime)
        codewords.append(new_codeword)
        domains.append(new_domain)
        root, tree = commit_codeword(new_codeword, prime)
        commitments.append(root)
        trees.append(tree)
        transcript.absorb(b"fri-commit-" + (j + 1).to_bytes(4, "big"), root)

    # Grinding over the committed transcript, before any query position
    # exists: the nonce is absorbed first, so the positions depend on it
    # and every fresh query set costs the forger a fresh search.
    nonce = _find_grinding_nonce(transcript.state(), grinding_bits)
    transcript.absorb_int(b"fri-grinding", nonce, num_bytes=8)

    # Draw query positions against the initial domain.
    query_positions = [
        transcript.squeeze_index(b"fri-query-" + k.to_bytes(4, "big"), n)
        for k in range(num_queries)
    ]

    # Build openings for every query across every round.
    query_openings: list[list[QueryOpening]] = []
    for j in range(num_rounds + 1):
        round_codeword = codewords[j]
        round_tree = trees[j]
        round_size = len(round_codeword)
        half = round_size // 2 if round_size > 1 else 0
        round_openings: list[QueryOpening] = []
        for q in query_positions:
            idx = q % round_size
            sibling_idx = (idx + half) % round_size if half > 0 else idx
            round_openings.append(
                QueryOpening(
                    leaf_index=idx,
                    leaf_value=round_codeword[idx],
                    sibling_value=round_codeword[sibling_idx],
                    merkle_path=_merkle_path(round_tree, idx),
                    sibling_path=_merkle_path(round_tree, sibling_idx),
                )
            )
        query_openings.append(round_openings)

    final_codeword = codewords[-1]

    return FRIProof(
        commitments=commitments,
        query_openings=query_openings,
        final_codeword=final_codeword,
        grinding_nonce=nonce,
    )


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
    n = len(initial_domain)
    if n < 4 or (n & (n - 1)):
        raise ValueError("domain size must be a power of two at least four")
    if num_queries < 1:
        raise ValueError("num_queries must be at least one")
    if grinding_bits < 0:
        raise ValueError("grinding_bits must be non-negative")

    max_rounds = n.bit_length() - 2
    if num_rounds is None:
        num_rounds = _rounds_for_degree_bound(n, degree_bound)
    elif degree_bound is not None:
        raise ValueError("give num_rounds or degree_bound, not both")
    if num_rounds < 1 or num_rounds > max_rounds:
        raise ValueError(
            f"num_rounds must be in [1, {max_rounds}] for domain size {n}"
        )
    if len(proof.commitments) != num_rounds + 1:
        raise ValueError("proof commitments count does not match num_rounds")
    if len(proof.query_openings) != num_rounds + 1:
        raise ValueError("proof query_openings count does not match num_rounds")
    for openings in proof.query_openings:
        if len(openings) != num_queries:
            raise ValueError("each round must have num_queries openings")
    if len(proof.final_codeword) != n >> num_rounds:
        raise ValueError("final codeword length does not match num_rounds")

    # Replay the transcript.
    transcript.absorb(b"fri-commit-0", proof.commitments[0])
    betas: list[int] = []
    for j in range(num_rounds):
        betas.append(_squeeze_beta(transcript, prime, j))
        transcript.absorb(b"fri-commit-" + (j + 1).to_bytes(4, "big"), proof.commitments[j + 1])

    # Grinding, checked against the committed transcript and absorbed
    # before the query positions are derived, mirroring the prover.
    if not _check_grinding(transcript.state(), proof.grinding_nonce, grinding_bits):
        return False
    transcript.absorb_int(b"fri-grinding", proof.grinding_nonce, num_bytes=8)

    query_positions = [
        transcript.squeeze_index(b"fri-query-" + k.to_bytes(4, "big"), n)
        for k in range(num_queries)
    ]

    # Per-query Merkle path checks and fold-consistency checks.
    # Maintain the implicit domain sizes so we can recompute (x, -x) pairs.
    two_inv = mod_inv(2, prime)
    domain_sizes = [n]
    current_domain = list(initial_domain)
    round_domains = [current_domain]
    for _ in range(num_rounds):
        half = len(current_domain) // 2
        next_domain = [(current_domain[i] * current_domain[i]) % prime for i in range(half)]
        current_domain = next_domain
        round_domains.append(current_domain)
        domain_sizes.append(len(current_domain))

    for k, q in enumerate(query_positions):
        for j in range(num_rounds + 1):
            opening = proof.query_openings[j][k]
            round_size = domain_sizes[j]
            if round_size > 1:
                expected_sibling = (opening.leaf_index + round_size // 2) % round_size
            else:
                expected_sibling = opening.leaf_index
            if opening.leaf_index != q % round_size:
                return False
            depth = round_size.bit_length() - 1
            if len(opening.merkle_path) != depth or len(opening.sibling_path) != depth:
                raise ValueError("Merkle path length does not match the round's tree")
            # Verify Merkle opening.
            leaf_digest = _hash_leaf(opening.leaf_value, prime)
            if not _verify_merkle_path(
                proof.commitments[j], leaf_digest, opening.leaf_index, opening.merkle_path
            ):
                return False
            # Verify the sibling value against the same root at its own
            # position. The fold equation below reads both values, and
            # the next round's commitment cannot bind this one: a prover
            # who chooses the sibling freely chooses the folded value
            # freely, and commits to whatever that choice produces.
            sibling_digest = _hash_leaf(opening.sibling_value, prime)
            if not _verify_merkle_path(
                proof.commitments[j], sibling_digest, expected_sibling, opening.sibling_path
            ):
                return False
        # Fold-consistency across rounds.
        for j in range(num_rounds):
            current = proof.query_openings[j][k]
            nxt = proof.query_openings[j + 1][k]
            round_size = domain_sizes[j]
            half = round_size // 2
            idx = current.leaf_index
            paired_idx = (idx + half) % round_size
            # Determine which of (leaf, sibling) is at position idx and
            # which at paired_idx in the round-j codeword.
            if idx < half:
                fx, f_neg = current.leaf_value, current.sibling_value
                x = round_domains[j][idx]
            else:
                fx, f_neg = current.sibling_value, current.leaf_value
                x = round_domains[j][idx - half]
            even = ((fx + f_neg) * two_inv) % prime
            odd = ((fx - f_neg) * two_inv) % prime
            odd = (odd * mod_inv(x, prime)) % prime
            expected_folded = (even + betas[j] * odd) % prime
            next_idx = nxt.leaf_index
            expected_next_idx = idx % half if half > 0 else idx
            if next_idx != expected_next_idx:
                return False
            if expected_folded != nxt.leaf_value:
                return False

    # Final-round codeword must match the committed root.
    final_root, _ = commit_codeword(proof.final_codeword, prime)
    if final_root != proof.commitments[-1]:
        return False

    # Final codeword must be constant: after num_rounds of folding a
    # codeword close to a polynomial of degree less than degree_bound,
    # the polynomial degree bound halves each round. For the Chapter 34
    # toy (trace length 8, LDE size 32, num_rounds 3), the final
    # polynomial has degree less than one on a 4-point domain, so every
    # value in the final codeword equals the same constant. One fold
    # more would flatten every polynomial of degree below 16 as well,
    # so the round count is what makes this check test the claimed
    # degree and not twice it. A random codeword that
    # happens to pass every fold-consistency check by coincidence
    # cannot also make the final codeword constant except with the
    # negligible probability governed by the proximity-gap theorem.
    if len(proof.final_codeword) < 1:
        return False
    anchor = proof.final_codeword[0]
    for v in proof.final_codeword[1:]:
        if v != anchor:
            return False

    return True
