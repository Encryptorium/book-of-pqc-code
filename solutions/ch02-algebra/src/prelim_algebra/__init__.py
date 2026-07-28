"""Chapter 2: the algebraic toolbox behind the algebra-heavy chapters.

Three modules, one per algebraic setting the chapter defines:

- ``modular``: arithmetic in Z/nZ. Exponentiation by repeated squaring, the
  extended Euclidean algorithm and the inverse it yields, and the element-order
  and generator searches exercise 2 asks for.
- ``polynomials``: arithmetic in F_p[x] and its quotients. Naive multiplication,
  reduction modulo a monic polynomial, evaluation, and the root search
  exercise 3 asks for.
- ``linear``: Gaussian elimination over F_p, which reports the reduced row
  echelon form and the rank together.

Nothing here is cryptography. Chapter 2 implements no scheme; it implements the
operations every later scheme is assembled from, in the slowest and clearest
form, so that the fast versions in Chapter 9 and beyond have something to be
compared against.

The package is stdlib-only and does no input validation, per the book's rule
for toy code: bad input crashes loudly rather than being handled. The asserts
that do appear are narration of a precondition, not error recovery.
"""

from .linear import gauss_eliminate
from .modular import ext_gcd, find_generator, mod_inv, mod_pow, order
from .polynomials import poly_eval, poly_mod, poly_mul, roots

__all__ = [
    "ext_gcd",
    "find_generator",
    "gauss_eliminate",
    "mod_inv",
    "mod_pow",
    "order",
    "poly_eval",
    "poly_mod",
    "poly_mul",
    "roots",
]
