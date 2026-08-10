# Chapter 18: hash-based signature cryptanalysis

The arithmetic behind Chapter 18's security claims, factored into functions so
every number the chapter prints has something under it that a test can hold.

This package computes and does not sign. `solutions/ch17-slh-dsa` is the working
SLH-DSA implementation; what is here is the analysis run *on* that construction.
Nothing in this tree calls a hash function.

```
src/hash_cryptanalysis/
  params.py           FIPS 205 Table 2's six SHA-2 sets, and the WOTS+ chain count
  multitarget.py      signature component accounting, preimage target populations
  fors_reuse.py       FORS coverage: exact, approximate, and reuse thresholds
  quantum.py          generic preimage and collision exponents
  countermeasures.py  verify-after-sign and constant-time chaining, in hash calls
```

## Running it

From a clone of the companion repository:

```
pytest tests/ch18
```

189 tests, no dependencies beyond the Python standard library, well under a
second. `PQC_IMPL=exercises pytest tests/ch18` runs the same suite against the
stub tree in `exercises/ch18-hash-cryptanalysis`.

## What the tests pin

Two of them are worth knowing about, because they check the package against
something outside it rather than against itself.

`test_signature_accounting.py` derives all six FIPS 205 signature sizes from the
component formula, `1 + k(1 + a) + d·ell + h` strings of `n` bytes, and compares
each against the published figure. The chapter checks this at
SLH-DSA-SHA2-128s alone, where 491 strings give 7,856 bytes. Six-for-six is the
stronger result: a formula can land on one row by luck and will not land on six.

`test_params.py` checks every derived quantity against the Table 2 column it is
supposed to reproduce, including that `h = d · h'` divides exactly. The six
integers per parameter set are transcribed from the standard and cannot be
derived from anything the book states, so a transcription error is the failure
mode with no other guard against it. The full twelve-row table, with the digest
length `m` and the public-key sizes, is frozen in `tests/ch17/test_vectors.py`.

## Divergences worth stating

**The target population is an intuition model, not the proof's term.**
`preimage_target_population` counts `k·t` FORS leaf hashes plus `d·ell` WOTS+
revealed chain values, scoped to one FORS instance and its hypertree layer. The
SPHINCS+/SLH-DSA security proof counts something else: it also carries signing
queries, position reuse, FORS few-time degradation, and construction-specific
terms. The chapter says so where it introduces the figure. Read
`effective_preimage_bits` as the size of the reduction ADRS removes, not as a
security level anyone claims.

**Signature components and preimage targets are different counts, and neither
contains the other.** Authentication-path nodes are components and not preimage
targets; substituting one is a second-preimage problem on a Merkle node. FORS
leaf hashes are targets and not components; the verifier recomputes each leaf
from a revealed secret, so the leaf hash never travels. The modules keep them in
separate functions for that reason, and adding the two populations is wrong.

**The SHAKE parameter sets are omitted rather than duplicated.** FIPS 205
tabulates twelve sets; the six SHAKE ones carry the same `n, h, d, a, k, w` as
their SHA-2 namesakes and differ only in the hash instantiation of Section 11,
which this package never evaluates. Including them would double the table
without changing a computed result.

**`bht_collision_bits` is a query count, not a cost.** It reports `n/3` because
Brassard-Hoyer-Tapp achieves that in an idealised black-box model with
`2**(n/3)` entries of quantum-accessible RAM. It is the smallest of the four
exponents in `quantum.py` and it is not the binding constraint on any FIPS 205
parameter set. `test_quantum.py::test_category_floors_track_grover_not_bht` is
the assertion that records which one is.

**`expected_position_collisions` uses the exact pair count.** The chapter quotes
the birthday estimate as `q²/2⁶⁴` at `h = 63`; the function computes
`(q(q-1)/2)·2^-h`, which is the same figure without the rounding-up, and agrees
with the quoted form to a relative error of about `1/q`.

**Nothing here models fault injection.** `countermeasures.py` prices the two
defences in hash calls and says nothing about whether they work. Chapter 18's
own treatment is the authority on that, and its conclusion is that
verify-after-sign is partial: the grafting attack of Castelnovi, Martinelli and
Prest produces a faulted signature that verifies.
