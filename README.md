# Book of PQC: companion code

Every line of code in [*The Encryptorium Book of Post-Quantum Cryptography*](https://book.encryptorium.com) that is meant to run, in a form you can run. Post-quantum cryptography (PQC) is the set of algorithms built to stay secure against an adversary holding a large quantum computer.

The book's continuous integration (CI) runs the fenced Python blocks in the prose and compares each one's output against a `# ==>` expected-output marker. The exception is a block tagged `no-verify`, which CI skips; the book has two, both sketches not meant to run standalone. This repository holds those blocks as files, the fuller implementations behind them, a stubbed copy of each so you can write them yourself, and the pytest suites that check either one. Those suites include the Automated Cryptographic Validation Protocol (ACVP) vector comparisons published by the US National Institute of Standards and Technology (NIST) for the algorithms the released chapters build. Chapter 11's ML-KEM vectors and Chapter 12's ML-DSA vectors are both here, checked byte for byte against Federal Information Processing Standards (FIPS) 203 and 204. Chapter 17's SLH-DSA vectors are here too, checked against FIPS 205: key generation byte for byte at all twelve parameter sets, signature verification accepting the valid cases and rejecting the invalid ones at all twelve, and signature generation byte for byte at the six fast sets. Signing at the six small-signature sets takes seconds per signature in pure Python, so those are covered by verification vectors alone and the generation check skips them rather than dropping them silently. Chapter 21's HQC is the one released chapter that builds a NIST-selected algorithm without matching its vectors, and that is deliberate: it implements the IND-CPA public-key scheme at the centre of HQC at `n = 83` with a repetition inner code, where the specification uses a concatenated Reed-Solomon and Reed-Muller code inside a Fujisaki-Okamoto KEM. Its `tests/ch21/test_vectors.py` checks the structure and byte lengths of the official known-answer tests when you vendor them, and skips when you have not; `tests/ch21/vectors/README.md` says where to get them and `solutions/ch21-hqc/README.md` states the divergence in full. Chapter 22 is a different case again and has no vectors to match: it builds SIDH, which NIST never standardised and which Castryck and Decru broke in 2022, so there is no live specification to be byte-compatible with and `tests/ch22` proves the mathematics instead; `solutions/ch22-isogenies/README.md` says so and also says what that suite does not establish. Chapter 23 is a fourth case, and the only one where a current specification does exist and this repository still makes no attempt to match it: it builds SQIsign, a round-3 additional-signatures candidate, as a toy at `p = 431` against the round-2 specification's 251-bit prime, and it searches the isogeny graph directly where the real scheme works inside the quaternion algebra. `tests/ch23` proves the quaternion and Deuring arithmetic instead, and `solutions/ch23-sqisign/README.md` sets out the compliance gap axis by axis and names three claims that suite does not establish. Chapter 24 is a fifth case, and the only one where there is no scheme to be compatible with: it is a survey of the multivariate family, so `solutions/ch24-multivariate` implements the Oil-Vinegar trapdoor the family shares rather than any one of UOV, MAYO or SNOVA, at `(n, m, q) = (5, 2, 7)` over a prime field where all three work over extension fields. What `tests/ch24` does instead is check the arithmetic behind the sizes: it recomputes UOV's 412,160-byte and 278,432-byte public keys from the parameter sets and compares them against Table 1 of the round-2 submission, so the figures the chapter quotes are derived rather than transcribed. The MAYO and SNOVA figures are transcriptions, and `solutions/ch24-multivariate/README.md` says which are which. Chapter 25 raises none of this: it builds a CycloneDX inventory document rather than a cryptographic algorithm, so there is no specification to be byte-compatible with and no vectors to match. `tests/ch25` checks the CycloneDX structure it emits and the worst-case propagation rule that assigns each entry its quantum status. Chapter 27 is the one case that goes the other way. Its vectors are not NIST's: it builds X25519 and Ed25519 from scratch as the classical halves of two hybrids, and `tests/ch27` checks them byte for byte against the known-answer tests in the specifications themselves, RFC 7748 Section 5.2 and RFC 8032 Section 7.1. The million-iteration X25519 vector is real but skipped by default, because it takes about a minute in pure Python; set `CH27_X25519_STRESS=1` to run it. The post-quantum halves are not built twice: the hybrid KEM imports Chapter 11's ML-KEM, and the composite signature uses a documented byte-size placeholder for ML-DSA-65 rather than importing Chapter 12's, because that chapter's subject is the combiner and `solutions/ch27-hybrid/src/hybrid/mldsa_stub.py` says so in full. Chapter 32 closes the list, and it is the plainest case of all: none of its four modules implements a standardised algorithm, so there is nothing normative to be byte-compatible with. Its KZG builds no pairings and works in a 2027-element field, its FRI is interactive with no Fiat-Shamir compilation, and its lattice commitment is a scalar SIS vector commitment rather than the ring constructions the chapter cites; `solutions/ch32-commitment-schemes/README.md` states each boundary. `tests/ch32` proves the round trips and the binding reductions instead. One test there is worth naming because it exists for a failure the others cannot see: `test_hash_bytes_uses_the_primitive_each_width_claims` pins which hash function each output width routes to, since a 384-bit request answered by SHAKE-128 returns the right number of bytes at the wrong security level, and every length assertion in the file passes anyway. Chapter 33 is here for a different reason than the vectors question, which it raises no more than Chapter 32 does: its subject is a proof technique rather than an algorithm, and the gap a reader should know about is stated in `solutions/ch33-fiat-shamir-qrom/README.md` under "Scope boundary". The package does not simulate a quantum adversary. Classical Python cannot issue a query in superposition, so what the code models is the classical side of the reduction the measure-and-reprogram technique produces, along with the reprogram-before-query discipline that technique depends on. The quantum content is in the chapter's prose. `tests/ch33` proves the Schnorr round trip, the rewinding extractor, and that discipline; a mutation pass at publication added five more that pin labelled constants the rest of the suite cannot see, including the toy group Chapter 33 shares with Chapter 32 by value rather than by import. Chapter 34 is the last of this group and raises the vectors question no more than the two before it, but the gap a reader should know about is a different one and `solutions/ch34-starks/README.md` states it under "Scope boundary": the package is called `ch34-starks`, exports `stark_prove` and `stark_verify`, and is not zero-knowledge. The toy drops the composition polynomial that hides the trace in a production STARK and sends the trace in the clear alongside the proof, so the soundness argument closes but the "ZK" does not exist. Its `F_97` parameters are vacuous by design as well, being far too small to support the proximity-gap error term, so no bit-level claim should be read off the code. `tests/ch34` proves the round trip, the AIR and FRI rejection paths, and the field structure; a mutation pass at publication added two more, one pinning the Merkle digest width after a constant named for it turned out to be dead, and one pinning the domain generator and coset shift that the chapter's printed listings depend on and nothing else bound. Chapter 35 closes that group and sits outside the vectors question entirely, because it implements no primitive: `solutions/ch35-case-studies` is the calculator that reads a deployed system's parameters and reports where it lands, and its README states the boundary under "Scope boundary". Every margin it returns is a model rather than a security claim, and the model omits terms a production soundness analysis prices, so where a published figure and one computed here disagree, the disagreement is evidence about the model. Its `composed_margin` takes a `regime` argument defaulting to the Johnson radius, which is where the proximity gap is proven; the `capacity` regime exists because deployed pipelines use it, not because it is sound, so asking for a capacity-regime number is asking what a deployment claimed rather than what anyone proved. `tests/ch35` proves the printed listings, the three decoding radii, and each of the six deployed configurations one at a time, because three of them share one grid cell and three share another and a shape-only test cannot tell them apart; an eighteen-mutation pass at publication added two, one reading the query-consistency term directly after it turned out to be invisible to any test reading only the total, and one recording why that is structural rather than a weak test.

## Layout

Four trees, each with one job.

- `chapter-code/chNN/`: every Python block that chapter prints and CI runs, one file each. Generated from the chapter text, so what you run is what the page shows. A block tagged `no-verify` is skipped, because CI does not run it and shipping it as a runnable file would be a promise the book does not keep. Chapter 4's ECDSA signing sketch is the first of those, which is why `chapter-code/ch04/` holds eight files for the nine blocks that chapter prints.
- `solutions/chNN-<slug>/`: the reference implementation for one chapter, as a standalone Python package
- `exercises/chNN-<slug>/`: the same package with the functions that chapter teaches replaced by stubs
- `tests/chNN/`: the pytest suite, which runs against either package tree

The chapters draw pedagogical slices from `solutions/`. Code in the book is a readable excerpt; code here is the fuller version it was cut from. `chapter-code/` is the excerpt itself: each file adds a generated provenance header, and after that header its body is the chapter excerpt byte for byte.

## What to run

| You want to | Go to |
|---|---|
| run a listing exactly as the page prints it | `python3 chapter-code/ch01/01-factor-trial-division.py` |
| read the fuller version it was cut from | `solutions/ch01-quantum-threat/` |
| write the chapter's functions yourself | `exercises/ch01-quantum-threat/`, then `PQC_IMPL=exercises pytest tests/ch01` |
| check either package tree | `pytest tests/ch01` |

Every path above is a real one in this clone. Substitute another released chapter's number to move around.

The worked answers to a chapter's numbered exercises are not a separate tree: they are functions in that chapter's `solutions/` package, stubbed in `exercises/` and pinned by `tests/`. Chapter 1's `factor_trial_division_counted` is its exercise 2. The prose form of those answers is Appendix D, on the website.

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

## Running the tests

A clone carries the chapters released so far, and nothing for the ones still in editorial review. Run a chapter's suite from the repository root:

```
pytest tests/ch01
```

The suite defaults to the reference implementation, so a clone is green on the first run.

## Implementing a chapter yourself

```
PQC_IMPL=exercises pytest tests/ch01
```

Every stubbed function raises `NotImplementedError` until you write it, so the first run is red by design. Open `exercises/ch01-quantum-threat/`, implement one function, run again. Each stub keeps the reference implementation's signature and adds a contract block naming what it owes its caller, where the book covers it, and which test proves it. Most stubs keep the reference docstring too, so the contract you implement against is the one the book describes rather than a paraphrase. The rest are functions the reference itself wrote without one, mostly one-line address accessors and field-arithmetic helpers, and there the contract block is the whole contract.

`PQC_IMPL` accepts only `solutions` or `exercises`. Every chapter with a package under `solutions/` has one under `exercises/` as well, so `PQC_IMPL=exercises` resolves for every test directory in the clone.

Nothing is hidden: `solutions/` is in this clone. Reading it costs you the exercise, which is a trade only you can price.

## Troubleshooting

**"No module named 'numpy'" in a Part II chapter.** The venv is active but numpy was not installed. Run `pip install "numpy>=1.26"` inside the venv.

**Pytest reports "no tests ran".** Two causes. Either the chapter named on the command line has not been released yet, so there is no `tests/chNN` directory to collect from (see Release model), or pytest was called from outside the repository root, since the chapter test directories are resolved relative to it.

**`python3 --version` reports 3.8 or 3.9.** Some reference packages annotate an optional argument with a PEP 604 union such as `bytes | None` and do not import `annotations` from `__future__`. On both versions the annotation is evaluated when the function is defined, so importing one of those modules raises `TypeError: unsupported operand type(s) for |` rather than a `SyntaxError`. The official installer at python.org bypasses a system package manager's pin.

**The venv activates but `which python` still points at the system CPython.** The shell cached the pre-venv path. Open a new shell, `cd` in, activate again.

Appendix C of the book covers the environment contract in full.

## Release model

The book publishes one chapter at a time, and a chapter's code publishes with it. This repository tracks the published book rather than the working draft, so anything present here belongs to a chapter that has cleared review. Expect it to grow as the book does.

**Chapters released so far: Chapters 1 through 35, which is all of Part I, all of Part II, all of Part III, all of Part IV, all of Part V, and all of Part VI.** The rest of the book is in editorial review, and each chapter's trees land here on the day its prose publishes.

Not every chapter fills all four trees. `chapter-code/` holds the listings a chapter prints in its own body and CI runs, so a chapter whose prose prints no Python has no directory there, and a chapter with a `no-verify` sketch ships one file fewer than it prints. Chapter 3 is the first of those, and it still ships a `solutions/` package, an `exercises/` package and a suite, because the worked answers on its Appendix D page are code and belong under test like any other.

## What this repository is not

It does not contain the book's prose or figures. Those live at [book.encryptorium.com](https://book.encryptorium.com), where the worked solutions to the numbered exercises are published as Appendix D alongside each released chapter.

## License

MIT, see `LICENSE`. The book's prose is licensed separately under CC BY-SA 4.0.

## Reporting a problem

The book makes two claims a reader can check: every algorithm runs, and every claim is sourced. A violation of either is a bug. Open an issue here, or write to <contact@encryptorium.com>.
