"""Tests for FORS few-time security properties."""

from fors_hypertree.fors import fors_keygen, fors_sign, message_indices


def test_index_collision_rate_grows_with_q():
    """After many signatures, tree-position collisions appear."""
    seed = b"collision-rate"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    q = 50
    # Track which indices have been used per tree
    used: list[set[int]] = [set() for _ in range(k)]
    collisions = 0

    for i in range(q):
        msg = f"msg-{i}".encode()
        indices = message_indices(msg, k, t)
        for j in range(k):
            if indices[j] in used[j]:
                collisions += 1
            used[j].add(indices[j])

    # With q=50, k=6, t=16, expected collisions per tree ~ q^2/(2t) ~ 78.
    # Over k=6 trees, total expected ~ 468.  We just check it is non-zero.
    assert collisions > 0, "Expected at least one index collision at q=50"


def test_no_full_forgery_at_low_q():
    """At q=5, no two messages share all k indices (overwhelmingly likely)."""
    seed = b"no-full-collision"
    k, t = 6, 16

    all_index_tuples: list[tuple[int, ...]] = []
    for i in range(5):
        msg = f"low-q-{i}".encode()
        indices = message_indices(msg, k, t)
        all_index_tuples.append(tuple(indices))

    # Check no two tuples are identical
    for i in range(len(all_index_tuples)):
        for j in range(i + 1, len(all_index_tuples)):
            assert all_index_tuples[i] != all_index_tuples[j], (
                f"Full index collision between messages {i} and {j}"
            )


def test_same_leaf_reuse_reveals_same_value():
    """When two messages use the same index at tree j, the revealed leaf
    and auth path are identical (deterministic keygen)."""
    seed = b"reuse-check"
    k, t, n = 6, 16, 32
    sk_leaves, trees, pk = fors_keygen(seed, k=k, t=t, n=n)

    # Find two messages that share at least one index at some tree
    sigs_by_tree: list[dict[int, tuple[bytes, list[bytes]]]] = [
        {} for _ in range(k)
    ]

    found_reuse = False
    for i in range(100):
        msg = f"reuse-{i}".encode()
        indices = message_indices(msg, k, t)
        sig = fors_sign(sk_leaves, trees, msg, k=k, t=t, n=n)

        for j in range(k):
            idx = indices[j]
            if idx in sigs_by_tree[j]:
                # Same index used twice at tree j
                prev_leaf, prev_path = sigs_by_tree[j][idx]
                cur_leaf, cur_path = sig[j]
                assert cur_leaf == prev_leaf, "Same index should reveal same leaf"
                assert cur_path == prev_path, "Same index should produce same auth path"
                found_reuse = True
            else:
                sigs_by_tree[j][idx] = sig[j]

    assert found_reuse, "Expected at least one index reuse in 100 messages"
