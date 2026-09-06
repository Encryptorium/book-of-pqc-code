"""Regression for Track 2 round 10 P1-01: a FORS signature must not let the
verifier's first authentication-path element stand in for a neighbouring leaf.

With the secret itself as the Merkle leaf, path[0] is the sibling's secret, so
one signature covers every target whose k indices each lie in {i, i ^ 1}: a
(2/t)^k share of all digests instead of (1/t)^k.  Hashing the secret into the
leaf closes it: path[0] is then a leaf hash, and the forgery below must fail.
"""

from fors_hypertree.fors import fors_keygen, fors_sign, fors_verify, message_indices


def _sibling_swap(sig, old, new):
    out = []
    for o, n_, (leaf, path) in zip(old, new, sig):
        out.append((leaf, path) if o == n_ else (path[0], [leaf, *path[1:]]))
    return out


def test_sibling_swap_forgery_is_rejected():
    k, t, n = 3, 4, 32
    sk, trees, pk = fors_keygen(b"audit-for-sibling-leak", k=k, t=t, n=n)
    original = b"original message"
    sig = fors_sign(sk, trees, original, k=k, t=t, n=n)
    old = message_indices(original, k, t)
    assert fors_verify(pk, original, sig, k=k, t=t, n=n)
    tried = 0
    for counter in range(10_000):
        target = f"forged message {counter}".encode()
        new = message_indices(target, k, t)
        if new != old and all(b in (a, a ^ 1) for a, b in zip(old, new)):
            tried += 1
            assert not fors_verify(pk, target, _sibling_swap(sig, old, new), k=k, t=t, n=n)
            if tried == 5:
                break
    assert tried == 5, "expected at least five sibling-adjacent targets in 10,000 tries"
