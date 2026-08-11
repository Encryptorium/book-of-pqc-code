# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 22: Isogenies for programmers
# Section: "Velu's formulas over $\mathbb{F}_{p^2}$"
# https://book.encryptorium.com/part-4-code-isogeny/ch22-isogenies-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch22/05-fp2-add.py

p = 431

def fp2_add(x, y, p):
    return ((x[0]+y[0]) % p, (x[1]+y[1]) % p)
def fp2_sub(x, y, p):
    return ((x[0]-y[0]) % p, (x[1]-y[1]) % p)
def fp2_mul(x, y, p):
    return ((x[0]*y[0]-x[1]*y[1]) % p, (x[0]*y[1]+x[1]*y[0]) % p)
def fp2_inv(x, p):
    norm = (x[0]*x[0]+x[1]*x[1]) % p
    return ((x[0]*pow(norm,-1,p)) % p, ((-x[1])*pow(norm,-1,p)) % p)
def fp2_neg(x, p):
    return ((-x[0]) % p, (-x[1]) % p)
def fp2_sqr(x, p):
    return ((x[0]*x[0]-x[1]*x[1]) % p, (2*x[0]*x[1]) % p)

def ec_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1[0]%p == x2[0]%p and x1[1]%p == x2[1]%p:
        ny2 = fp2_neg(y2, p)
        if y1[0]%p == ny2[0]%p and y1[1]%p == ny2[1]%p:
            return None
        num = fp2_add(fp2_mul((3,0), fp2_sqr(x1,p), p), a, p)
        den = fp2_mul((2,0), y1, p)
        lam = fp2_mul(num, fp2_inv(den,p), p)
    else:
        lam = fp2_mul(fp2_sub(y2,y1,p), fp2_inv(fp2_sub(x2,x1,p),p), p)
    x3 = fp2_sub(fp2_sub(fp2_sqr(lam,p), x1, p), x2, p)
    y3 = fp2_sub(fp2_mul(lam, fp2_sub(x1,x3,p), p), y1, p)
    return (x3, y3)

def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1: R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R

def velu_eval(Q, kernel, a, p):
    if Q is None: return None
    xQ, yQ = Q
    x_new, y_new = xQ, yQ
    for R in kernel:
        if R is None: continue
        xR, yR = R
        if xQ[0]%p == xR[0]%p and xQ[1]%p == xR[1]%p:
            return None
        QpR = ec_add(Q, R, a, p)
        if QpR is None: return None
        x_new = fp2_add(x_new, fp2_sub(QpR[0], xR, p), p)
        y_new = fp2_add(y_new, fp2_sub(QpR[1], yR, p), p)
    return (x_new, y_new)

a0 = (1, 0)
G = ((13, 0), (290, 0))
P3 = ec_mul(144, G, a0, p)   # order 3
P3_2 = ec_mul(2, P3, a0, p)
kernel_3 = [None, P3, P3_2]

phi_G = velu_eval(G, kernel_3, a0, p)
print(phi_G)
# ==> ((412, 0), (94, 0))

print(velu_eval(P3, kernel_3, a0, p))
# ==> None
