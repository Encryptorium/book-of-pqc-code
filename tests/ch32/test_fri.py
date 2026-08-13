"""Tests for ``commitment_schemes.fri``."""

import pytest

from commitment_schemes import fri


# In F_97, g = 8 has order 16 (verified in prose). A 16-element domain
# supports 4 folding rounds.
F97 = 97
G16 = 8


def test_generate_domain_size_sixteen() -> None:
    domain = fri.generate_domain(16, G16, F97)
    assert len(domain) == 16
    assert domain[0] == 1
    # Domain is closed under negation, with index i + 8 = -index i mod 97
    for i in range(8):
        assert (domain[i] + domain[i + 8]) % F97 == 0


def test_generate_domain_rejects_bad_size() -> None:
    with pytest.raises(ValueError):
        fri.generate_domain(3, G16, F97)
    with pytest.raises(ValueError):
        fri.generate_domain(1, G16, F97)


def test_generate_domain_rejects_wrong_order_generator() -> None:
    # g = 2 does not have order 16 in F_97 (order is 48 in fact).
    with pytest.raises(ValueError):
        fri.generate_domain(16, 2, F97)


def test_low_degree_fold_to_constant() -> None:
    """A polynomial of degree < 2 folded with 3 rounds reaches a constant.

    Starting codeword size 16, fold 3 rounds -> size 2, which for a
    polynomial of degree < 2 should equal the same constant everywhere.
    """
    domain = fri.generate_domain(16, G16, F97)
    # p(x) = 7 + 3x (degree 1)
    coeffs = [7, 3]
    evals = fri.commit(coeffs, domain, F97)

    # Fold 3 rounds so the final domain has 2 points. A degree-1
    # polynomial under 3 folds becomes a degree-0 (constant) function
    # for any choice of betas, because the degree halves each round.
    betas = [5, 11, 17]
    initial_evals = evals
    current_evals = list(initial_evals)
    current_domain = list(domain)
    for beta in betas:
        current_evals, current_domain = fri.fold_once(
            current_evals, current_domain, beta, F97
        )
    # Final evaluations all equal.
    assert len(current_evals) == 2
    assert current_evals[0] == current_evals[1]


def test_fold_to_constant_round_count() -> None:
    domain = fri.generate_domain(16, G16, F97)
    evals = fri.commit([1, 2, 3, 4], domain, F97)
    betas = [2, 3, 5, 7]  # 4 rounds for size 16 -> 1
    rounds = fri.fold_to_constant(evals, domain, betas, F97)
    # 1 initial round + 4 folds = 5 entries
    assert len(rounds) == 5
    assert len(rounds[-1].domain) == 1
    assert len(rounds[-1].evaluations) == 1


def test_honest_codeword_passes_consistency() -> None:
    """An honestly-folded codeword passes the consistency check at every index."""
    domain = fri.generate_domain(16, G16, F97)
    evals = fri.commit([1, 2, 3, 4], domain, F97)  # degree < 4
    betas = [13, 19, 23, 29]
    rounds = fri.fold_to_constant(evals, domain, betas, F97)
    for query in range(16):
        assert fri.query_consistency(rounds, query, F97)


def test_tampered_codeword_fails_consistency() -> None:
    """Corrupting one evaluation breaks consistency at at least one query."""
    domain = fri.generate_domain(16, G16, F97)
    evals = fri.commit([1, 2, 3, 4], domain, F97)
    betas = [13, 19, 23, 29]
    rounds = fri.fold_to_constant(evals, domain, betas, F97)

    # Tamper the initial codeword at index 3. The rest of the rounds
    # are unchanged, so the consistency check at query 3 must fail.
    rounds[0].evaluations[3] = (rounds[0].evaluations[3] + 1) % F97

    assert not fri.query_consistency(rounds, 3, F97)


def test_fold_once_rejects_mismatched_lengths() -> None:
    # G16^4 = 8^4 mod 97 = 22 has order 4.
    domain = fri.generate_domain(4, 22, F97)
    with pytest.raises(ValueError):
        fri.fold_once([1, 2, 3], domain, 5, F97)


def test_fold_to_constant_rejects_wrong_number_of_betas() -> None:
    domain = fri.generate_domain(16, G16, F97)
    evals = fri.commit([1, 2], domain, F97)
    with pytest.raises(ValueError):
        fri.fold_to_constant(evals, domain, [5, 11], F97)  # needs 4 betas
