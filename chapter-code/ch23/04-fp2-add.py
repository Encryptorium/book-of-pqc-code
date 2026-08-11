# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "The endomorphisms of $E_0$"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/04-fp2-add.py

p = 431

def fp2_add(x, y, p):
    return ((x[0]+y[0]) % p, (x[1]+y[1]) % p)
def fp2_sub(x, y, p):
    return ((x[0]-y[0]) % p, (x[1]-y[1]) % p)
def fp2_mul(x, y, p):
    return ((x[0]*y[0]-x[1]*y[1]) % p, (x[0]*y[1]+x[1]*y[0]) % p)
def fp2_neg(x, p):
    return ((-x[0]) % p, (-x[1]) % p)
def fp2_pow(x, n, p):
    if n == 0: return (1, 0)
    r = (1, 0)
    base = x
    while n:
        if n & 1: r = fp2_mul(r, base, p)
        base = fp2_mul(base, base, p)
        n >>= 1
    return r

def iota(P, p):
    if P is None: return None
    x, y = P
    return (fp2_neg(x, p), fp2_mul((0, 1), y, p))

def pi_frob(P, p):
    if P is None: return None
    x, y = P
    return (fp2_pow(x, p, p), fp2_pow(y, p, p))

# A point on E_0: y^2 = x^3 + x at p = 431.
G = ((13, 0), (290, 0))

# Verify iota^2 = [-1] on G.
once = iota(G, p)
twice = iota(once, p)
print(twice == (G[0], fp2_neg(G[1], p)))
# ==> True

# Verify iota . pi anticommutes with pi . iota on G.
left = iota(pi_frob(G, p), p)
right = pi_frob(iota(G, p), p)
neg_right = (right[0], fp2_neg(right[1], p))
print(left == neg_right)
# ==> True
