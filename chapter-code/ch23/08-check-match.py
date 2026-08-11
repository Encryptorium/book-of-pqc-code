# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "Toy SQIsign: verify"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/08-check-match.py

# Verification structure: walk the signature from the challenge curve,
# compare j-invariants. The runnable verify is in
# the ch23-sqisign package under solutions/.

p = 431

def check_match(j_walked, j_pk, p):
    return j_walked[0] % p == j_pk[0] % p and j_walked[1] % p == j_pk[1] % p

# After walking, suppose the path lands at j = (143, 0).
j_walked = (143, 0)
j_pk = (143, 0)
print(check_match(j_walked, j_pk, p))
# ==> True

# A path that lands elsewhere is rejected.
print(check_match((19, 0), j_pk, p))
# ==> False
