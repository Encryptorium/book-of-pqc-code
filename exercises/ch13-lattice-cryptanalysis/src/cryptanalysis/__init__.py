"""Chapter 13: lattice cryptanalysis.

The package exposes a small core-SVP cost estimator for Module-LWE
parameter sets. The public entry points are:

- :func:`classical_bits`: the log-cost of classical sieving at block
  size ``beta`` from the Becker-Ducas-Gama-Laarhoven 2016 sieving
  exponent ``0.292 * beta``.
- :func:`quantum_bits`: the log-cost of quantum sieving at block size
  ``beta`` from the Laarhoven quantum speedup giving exponent
  ``0.265 * beta``.
- :func:`delta_beta`: the Chen 2013 root-Hermite-factor approximation
  for BKZ output quality, used inside the primal-attack success
  condition.
- :func:`primal_beta`: the smallest block size ``beta`` at which the
  unique-SVP primal attack (Kyber Round 3 submission, equation 9)
  succeeds for a given Module-LWE parameter tuple.
- :func:`dual_advantage`: the distinguishing advantage of a dual
  attacker who has found a short vector ``w`` in the dual lattice.
- :func:`estimate_parameter_set`: the full estimator that takes a
  Module-LWE parameter set and returns ``(beta, classical, quantum)``.
- :func:`estimate_ml_dsa_set`: the same estimator against ML-DSA's
  non-square Module-LWE instance, whose secret is uniform on
  ``[-eta, eta]`` rather than centered binomial.
"""

from .core_svp import classical_bits, delta_beta, quantum_bits
from .dual import dual_advantage
from .estimator import estimate_ml_dsa_set, estimate_parameter_set
from .primal import primal_beta

__all__ = [
    "classical_bits",
    "delta_beta",
    "dual_advantage",
    "estimate_ml_dsa_set",
    "estimate_parameter_set",
    "primal_beta",
    "quantum_bits",
]
