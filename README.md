# Book of PQC: companion code

Every line of code in [*The Encryptorium Book of Post-Quantum Cryptography*](https://book.encryptorium.com) that is meant to run, in a form you can run. Post-quantum cryptography (PQC) is the set of algorithms built to stay secure against an adversary holding a large quantum computer.

The book's continuous integration (CI) runs the fenced Python blocks in the prose and compares each one's output against a `# ==>` expected-output marker. The exception is a block tagged `no-verify`, which CI skips; the book has two, both sketches not meant to run standalone. This repository holds as files the blocks a chapter prints in its own body and CI runs, the fuller implementations behind them, a stubbed copy of each so you can write them yourself, and the pytest suites that check either one.

## Layout

Four trees, each with one job.

- `chapter-code/chNN/`: every Python block that chapter prints and CI runs, one file each. Generated from the chapter text, so what you run is what the page shows. A block tagged `no-verify` is skipped, because CI does not run it and shipping it as a runnable file would be a promise the book does not keep. The book has two. Chapter 4's ECDSA signing sketch is one, which is why `chapter-code/ch04/` holds eight files for the nine blocks that chapter prints; Chapter 21's sketch of a reference-compliant HQC call shape is the other, so `chapter-code/ch21/` holds eleven for twelve.
- `solutions/chNN-<slug>/`: the reference implementation for one chapter, as a standalone Python package
- `exercises/chNN-<slug>/`: the same package with stubs in place of the functions that chapter teaches but does not print. A function printed in the chapter is handed over already implemented, because copying it off the page is not an exercise.
- `tests/chNN/`: the pytest suite, which runs against either package tree

The chapters draw pedagogical slices from `solutions/`. Code in the book is usually a readable excerpt and the code here is the fuller version it was cut from. Chapter 13's toy LLL is written for the page alone and is not in a package, so `solutions/ch13-lattice-cryptanalysis` holds the core-SVP estimator and no lattice reduction. `chapter-code/` is the excerpt itself: each file adds a generated provenance header, and after that header its body is the chapter excerpt byte for byte.

## What to run

| You want to | Go to |
|---|---|
| run a listing exactly as the page prints it | `python3 chapter-code/ch01/01-factor-trial-division.py` |
| read the fuller version it was cut from | `solutions/ch01-quantum-threat/` |
| write the chapter's functions yourself | `exercises/ch01-quantum-threat/`, then `PQC_IMPL=exercises pytest tests/ch01` |
| check the reference implementation | `pytest tests/ch01` |

Every path above is a real one in this clone. The chapter number indexes all four trees, but only `tests/chNN` substitutes literally: the `solutions/` and `exercises/` directories carry a slug after the number, `chapter-code/` names each file after the block it holds, and `chapter-code/` has no `ch03` at all, because Chapter 3 prints no Python. List the tree rather than guessing a name. The chapter numbers and titles are listed at [book.encryptorium.com](https://book.encryptorium.com).

Where a numbered exercise asks for code, its worked answer is not a separate tree: it is a function in that chapter's `solutions/` package, stubbed in `exercises/` and pinned by `tests/`. Exercises that ask for reasoning rather than code have no function behind them, and their answers are prose only. Chapter 1's `factor_trial_division_counted` is its exercise 2. The prose form of every answer, code and reasoning alike, is Appendix D, one page per chapter, at `https://book.encryptorium.com/appendix-d-solutions/ch01/` and so on.

## What each chapter's code is checked against

The suites include the Automated Cryptographic Validation Protocol (ACVP) vector comparisons published by the US National Institute of Standards and Technology (NIST) for the algorithms the released chapters build.

- **Chapters 11 and 12.** The ML-KEM and ML-DSA vectors are both here, checked byte for byte against Federal Information Processing Standards (FIPS) 203 and 204.
- **Chapter 17.** Its SLH-DSA vectors are here too, checked against FIPS 205: key generation byte for byte at all twelve parameter sets; signature verification accepting a valid signature at all twelve and rejecting an invalid one at SLH-DSA-SHA2-128s and SLH-DSA-SHAKE-128s, the two sets where the committed fixture carries invalid cases, one for each of the six rejection reasons; and signature generation byte for byte at the six fast sets. Signing at the six small-signature sets takes seconds per signature in pure Python, so those are covered by verification vectors alone and the generation check skips them rather than dropping them silently.
- **Chapter 21.** Its HQC is the one released chapter that builds a NIST-selected algorithm without matching its vectors, and that is deliberate: it implements the IND-CPA public-key scheme at the centre of HQC at `n = 83` with a repetition inner code, where the specification uses a concatenated Reed-Solomon and Reed-Muller code inside a Fujisaki-Okamoto KEM. Its `tests/ch21/test_vectors.py` checks the structure and byte lengths of the official known-answer tests when you vendor them, and skips when you have not; `tests/ch21/vectors/README.md` says where to get them and `solutions/ch21-hqc/README.md` states the divergence in full.
- **Chapter 22.** It has no vectors to match. It builds SIDH, which NIST never standardised and which Castryck and Decru broke in 2022, so there is no live specification to be byte-compatible with and `tests/ch22` proves the mathematics instead; `solutions/ch22-isogenies/README.md` says so and also says what that suite does not establish.
- **Chapter 23.** A current specification does exist and, unlike Chapter 21, the suite carries no vectors file at all. It builds SQIsign, a round-3 additional-signatures candidate, as a toy at `p = 431` against the round-2 specification's 251-bit prime, and it searches the isogeny graph directly where the real scheme works inside the quaternion algebra. `tests/ch23` proves the quaternion and Deuring arithmetic instead, and `solutions/ch23-sqisign/README.md` sets out the compliance gap axis by axis and names three claims that suite does not establish.
- **Chapter 24.** There is no single scheme to be compatible with. The chapter is a survey of the multivariate family, so `solutions/ch24-multivariate` implements the Oil-Vinegar trapdoor the family shares rather than any one of UOV, MAYO or SNOVA, at `(n, m, q) = (5, 2, 7)` over a prime field where all three work over extension fields. What `tests/ch24` does instead is check the arithmetic behind the sizes: it recomputes UOV's 412,160-byte and 278,432-byte public keys from the parameter sets and compares them against Table 1 of the round-2 submission, so the 412,160-byte figure the chapter quotes is derived rather than transcribed. The MAYO and SNOVA figures are transcriptions, and `solutions/ch24-multivariate/README.md` says which are which.
- **Chapter 25.** It builds a CycloneDX inventory document rather than a cryptographic algorithm, so there is no specification to be byte-compatible with and no vectors to match. `tests/ch25` checks the CycloneDX structure it emits and the worst-case propagation rule that assigns each entry its quantum status.
- **Chapter 27.** The vectors here are not NIST's. The chapter builds X25519 and Ed25519 from scratch as the classical halves of two hybrids, and `tests/ch27` checks them byte for byte against the known-answer tests in the specifications themselves, RFC 7748 Section 5.2 and RFC 8032 Section 7.1. The million-iteration X25519 vector is real but skipped by default, because a million pure-Python scalar multiplications take tens of minutes; set `CH27_X25519_STRESS=1` to run it. The post-quantum halves are not built twice: the hybrid KEM imports Chapter 11's ML-KEM, and the composite signature uses a documented byte-size placeholder for ML-DSA-65 rather than importing Chapter 12's, because Chapter 27's subject is the combiner and `solutions/ch27-hybrid/src/hybrid/mldsa_stub.py` says so in full.
- **Chapter 32.** None of its four modules implements a standardised algorithm, so there is nothing normative to be byte-compatible with. Its KZG builds no pairings and works in a 2027-element field, its FRI is interactive with no Fiat-Shamir compilation, and its lattice commitment is a scalar SIS vector commitment rather than the ring constructions the chapter cites; `solutions/ch32-commitment-schemes/README.md` states the pairing and interactivity boundaries, and the module docstring in `solutions/ch32-commitment-schemes/src/commitment_schemes/lattice_pcs.py` states the scalar one. `tests/ch32` proves the round trips and the binding reductions instead. One test there is worth naming because it exists for a failure the others cannot see: `test_hash_bytes_uses_the_primitive_each_width_claims` pins which hash function each output width routes to, since a 384-bit request answered by SHAKE-128 returns the right number of bytes at the wrong security level, and every length assertion in the file passes anyway.
- **Chapter 33.** Its subject is a proof technique rather than an algorithm, and the gap a reader should know about is stated in `solutions/ch33-fiat-shamir-qrom/README.md` under "Scope boundary". The package does not simulate a quantum adversary. Classical Python cannot issue a query in superposition, so what the code models is the classical side of the reduction the measure-and-reprogram technique produces, along with the reprogram-before-query discipline that technique depends on. The quantum content is in the chapter's prose. `tests/ch33` proves the Schnorr round trip, the rewinding extractor, and that discipline; a mutation pass at publication added five more that pin constants and sampler ranges the rest of the suite cannot see, including the toy group Chapter 33 shares with Chapter 32 by value rather than by import.
- **Chapter 34.** The gap a reader should know about is a different one, and `solutions/ch34-starks/README.md` states it under "Scope boundary": the package is called `ch34-starks`, exports `stark_prove` and `stark_verify`, and is not zero-knowledge. The toy drops the composition polynomial that hides the trace in a production STARK and sends the trace in the clear alongside the proof, so the soundness argument closes but the "ZK" does not exist. Its `F_97` parameters are vacuous by design as well, being far too small to support the proximity-gap error term, so no bit-level claim should be read off the code. `tests/ch34` proves the round trip, the AIR and FRI rejection paths, and the field structure; a mutation pass at publication added two more, one pinning the Merkle digest width after a constant named for it turned out to be dead, and one pinning the domain generator and coset shift that the chapter's printed listings depend on and nothing else bound.
- **Chapter 35.** It implements no primitive. `solutions/ch35-case-studies` is the calculator that reads a deployed system's parameters and reports where it lands, and its README states the boundary under "Scope boundary". Every margin it returns is a model rather than a security claim, and the model omits terms a production soundness analysis prices, so where a published figure and one computed here disagree, the disagreement is evidence about the model. Its `composed_margin` takes a `regime` argument defaulting to the Johnson radius, which is where the proximity gap is proven; the `capacity` regime exists because deployed pipelines use it, not because it is sound, so asking for a capacity-regime number is asking what a deployment claimed rather than what anyone proved. `tests/ch35` proves the printed listings, the three decoding radii, and each of the six deployed configurations one at a time, because three of them share one grid cell and three share another and a shape-only test cannot tell them apart; an eighteen-mutation pass at publication added two, one reading the query-consistency term directly after it turned out to be invisible to any test reading only the total, and one recording why that is structural rather than a weak test.

## Setup

CPython 3.10 or newer. The lattice chapters (7 through 13) also need NumPy 1.26 or newer; Chapter 13 needs it for one block, the toy LLL, and its core-SVP estimator is standard library only. Chapter 27 needs it too, for a less obvious reason: none of its own modules import NumPy, but its hybrid KEM imports Chapter 11's ML-KEM through `sys.path`, so `pytest tests/ch27` pulls NumPy in transitively. Chapter 29 is a second transitive case and a step further removed again. Its JWKS verifier imports Chapter 27's composite signature, and importing anything under that package first runs `hybrid/__init__.py`, which imports the hybrid KEM, which imports Chapter 11's ML-KEM. Nothing in Chapter 29 or in the composite signature itself touches NumPy, and `pytest tests/ch29` needs it anyway, through two chapters and a package `__init__`. Every other chapter runs against the standard library alone.

```
git clone https://github.com/Encryptorium/book-of-pqc-code.git
cd book-of-pqc-code
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-ci.txt
pip install pytest
```

On Windows PowerShell the activation line is `.venv\Scripts\Activate.ps1`.

Pytest is not declared as a dependency of any chapter package, because the chapters' runtime code never imports it. Install it once into the venv, as above.

There is no per-chapter install step. Each `tests/chNN/conftest.py` puts the selected tree's `src/` directory at the front of `sys.path`, so the suite imports the package straight out of the clone.

An editable install is optional and changes only where an interactive `import` resolves from. Install at most one tree per chapter: `exercises/chNN-<slug>` is a copy of `solutions/chNN-<slug>` down to the `pyproject.toml`, so both declare the same distribution name and pip treats the second install as replacing the first.

## Running the tests

A clone carries all 41 chapters. Run a chapter's suite from the repository root:

```
pytest tests/ch01
```

The suite defaults to the reference implementation, so a clone is green on the first run. On a fresh clone `pytest tests/` reports 2,209 passed and 16 skipped: six Chapter 17 signature-generation sets, nine Chapter 21 known-answer checks awaiting vendored vectors, and Chapter 27's million-iteration vector. Pytest prints an `s` for each without saying why; add `-rs` to print every reason.

The continuous integration named at the top of this README runs in the book's source repository, which is private; this repository carries no workflow of its own. The four trees here are published from that gated source. The claim a reader can verify independently is the one the gate enforces: from a clone in the environment above, `pytest tests/` collects every chapter's suite and passes, apart from the skips this README already names (Chapter 17's slow signature-generation sets, Chapter 27's million-iteration vector, and Chapter 21's known-answer checks until you vendor the official vectors).

## Implementing a chapter yourself

```
PQC_IMPL=exercises pytest tests/ch01
```

Every stubbed function raises `NotImplementedError` until you write it, so the first run is red by design. Open `exercises/ch01-quantum-threat/`, implement one function, run again. Each stub keeps the reference implementation's signature and adds a contract block naming what it owes its caller, where the book covers it, and which test proves it. Most stubs keep the reference docstring too, so the contract you implement against is the one the book describes rather than a paraphrase. The remaining eighteen are functions the reference itself wrote without one: seven one-line address accessors in Chapter 17, five dataclass `__post_init__` validators in Chapters 7 through 10, and six helpers covering curve and quaternion arithmetic, key derivation, and configuration parsing. There the contract block is the whole contract.

`PQC_IMPL` accepts only `solutions` or `exercises`; any other value stops with an error naming the variable rather than a confusing import failure. Every chapter with a package under `solutions/` has one under `exercises/` as well, so `PQC_IMPL=exercises` resolves for every test directory in the clone.

`PQC_IMPL` switches every package in the clone at once, not just the chapter you are working on. Two chapters import another chapter's package, so their suites block on stubs you may not have reached yet: Chapter 27's hybrid KEM imports Chapter 11's ML-KEM, and Chapter 29 imports Chapter 27's combiner and Chapter 15's XMSS. On a fresh clone, `PQC_IMPL=exercises pytest tests/ch29` raises `NotImplementedError: exercise: xmss_keygen` from `exercises/ch15-xmss/`, which is Chapter 15's stub rather than a mistake in your Chapter 29 code. Write Chapters 11, 15 and 27 before those two, or leave those two suites on `solutions` while you work.

Nothing is hidden: `solutions/` is in this clone. Reading it costs you the exercise, which is a trade only you can price.

## Troubleshooting

**"No module named 'numpy'" in Chapters 7 through 13, 27 or 29.** The venv is active but numpy was not installed. Run `pip install "numpy>=1.26"` inside the venv.

**Pytest reports "no tests ran".** Two causes. Either the path names a chapter directory that does not exist (the chapter suites are `tests/ch01` through `tests/ch41`), or pytest was called from outside the repository root, since the chapter test directories are resolved relative to it.

**`python3 --version` reports 3.8 or 3.9.** Some reference packages annotate an optional argument with a PEP 604 union such as `bytes | None` and do not import `annotations` from `__future__`. On both versions the annotation is evaluated when the function is defined, so importing one of those modules raises `TypeError: unsupported operand type(s) for |` rather than a `SyntaxError`. The official installer at python.org bypasses a system package manager's pin.

**The venv activates but `which python` still points at the system CPython.** The activate script was run rather than sourced, so its `PATH` edit never reached the shell you are in. Run `source .venv/bin/activate` from the directory holding `.venv`, then check `which python` again.

[Appendix C](https://book.encryptorium.com/appendices/appendix-c-environment-setup/) covers the environment contract in full.

## Release model

The book published one chapter at a time, and each chapter's code published with it. This repository tracks the published book rather than the working draft, so everything here belongs to a chapter that has cleared review.

**Chapters released so far: all 41, which is the whole book, Parts I through VII.** Every chapter's trees are here. The book is still in external review, so what lands from now on is corrections to published chapters rather than new ones.

Not every chapter fills all four trees. `chapter-code/` holds the listings a chapter prints in its own body and CI runs, so a chapter whose prose prints no Python has no directory there, and a chapter with a `no-verify` sketch ships one file fewer than it prints. Chapter 3 is the only chapter with no directory there, and it still ships a `solutions/` package, an `exercises/` package and a suite, because the worked answers on its Appendix D page are code and belong under test like any other.

## What this repository is not

It does not contain the book's prose or figures. Those are published free to read at [book.encryptorium.com](https://book.encryptorium.com), where the worked solutions to the numbered exercises are Appendix D, one page per chapter.

## License

MIT, see `LICENSE`. The book's prose is licensed separately under CC BY-SA 4.0.

## Reporting a problem

The book makes two claims a reader can check: every algorithm runs, and every claim is sourced. A violation of either is a bug. Open an issue here, or write to <contact@encryptorium.com>.
