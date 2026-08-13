# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 38: Wallets, addresses, and key rotation
# Section: "Plan the rotation cadence"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch38-wallets-addresses-key-rotation/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch38/03-breach-years.py

# Block 3: pedagogical slice of wallet_rotation.mosca_wallet (stdlib only).
def breach_years(X, Y, Z):
    return X + Y - Z


def recommend(X, Y, Z):
    breach = breach_years(X, Y, Z)
    safe_window = max(0, Z - Y)
    if breach <= 0:
        return ("calendar", Y)
    if safe_window >= 1:
        return ("every-N-years", safe_window)
    return ("external-trigger", 0)


# Strand wallet surface from Ch 36: X=10, Y=4.
X, Y = 10, 4
for label, Z in (("aggressive Z=4", 4), ("ncsc-2035 Z=9", 9), ("mid-2040 Z=14", 14)):
    cadence, N = recommend(X, Y, Z)
    breach = breach_years(X, Y, Z)
    print(f"{label}: breach={breach:>3}y -> {cadence}, N={N}y")
# ==> aggressive Z=4: breach= 10y -> external-trigger, N=0y
# ==> ncsc-2035 Z=9: breach=  5y -> every-N-years, N=5y
# ==> mid-2040 Z=14: breach=  0y -> calendar, N=4y
