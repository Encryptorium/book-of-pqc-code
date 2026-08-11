# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 22: Isogenies for programmers
# Section: "Walking the isogeny chain"
# https://book.encryptorium.com/part-4-code-isogeny/ch22-isogenies-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch22/06-fp2-add.py

p = 431

def fp2_add(x, y, p):
    return ((x[0]+y[0]) % p, (x[1]+y[1]) % p)

def fp2_sub(x, y, p):
    return ((x[0]-y[0]) % p, (x[1]-y[1]) % p)

def fp2_mul(x, y, p):
    return ((x[0]*y[0]-x[1]*y[1]) % p, (x[0]*y[1]+x[1]*y[0]) % p)

def fp2_inv(x, p):
    norm = (x[0]*x[0]+x[1]*x[1]) % p
    inv_n = pow(norm, -1, p)
    return ((x[0]*inv_n) % p, ((-x[1])*inv_n) % p)

def fp2_neg(x, p):
    return ((-x[0]) % p, (-x[1]) % p)

def fp2_sqr(x, p):
    return ((x[0]*x[0]-x[1]*x[1]) % p, (2*x[0]*x[1]) % p)

def ec_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1[0]%p == x2[0]%p and x1[1]%p == x2[1]%p:
        ny2 = fp2_neg(y2, p)
        if y1[0]%p == ny2[0]%p and y1[1]%p == ny2[1]%p:
            return None
        num = fp2_add(fp2_mul((3, 0), fp2_sqr(x1, p), p), a, p)
        den = fp2_mul((2, 0), y1, p)
        lam = fp2_mul(num, fp2_inv(den, p), p)
    else:
        num = fp2_sub(y2, y1, p)
        den = fp2_sub(x2, x1, p)
        lam = fp2_mul(num, fp2_inv(den, p), p)
    x3 = fp2_sub(fp2_sub(fp2_sqr(lam, p), x1, p), x2, p)
    y3 = fp2_sub(fp2_mul(lam, fp2_sub(x1, x3, p), p), y1, p)
    return (x3, y3)

def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1: R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R

def velu_eval(Q, kernel, a, p):
    if Q is None:
        return None
    xQ, yQ = Q
    x_new, y_new = xQ, yQ
    for R in kernel:
        if R is None:
            continue
        xR, yR = R
        if (xQ[0]%p == xR[0]%p and xQ[1]%p == xR[1]%p):
            return None
        QpR = ec_add(Q, R, a, p)
        if QpR is None:
            return None
        x_new = fp2_add(x_new, fp2_sub(QpR[0], xR, p), p)
        y_new = fp2_add(y_new, fp2_sub(QpR[1], yR, p), p)
    return (x_new, y_new)

def compute_kernel(gen, order, a, p):
    pts = [None]
    cur = gen
    for _ in range(1, order):
        pts.append(cur)
        cur = ec_add(cur, gen, a, p)
    return pts

def recover_curve(img1, img2, p):
    """Recover a', b' from two points on y^2 = x^3 + a'x + b'."""
    x1, y1 = img1
    x2, y2 = img2
    lhs1 = fp2_sub(fp2_sqr(y1, p), fp2_mul(fp2_sqr(x1, p), x1, p), p)
    lhs2 = fp2_sub(fp2_sqr(y2, p), fp2_mul(fp2_sqr(x2, p), x2, p), p)
    num = fp2_sub(lhs1, lhs2, p)
    den = fp2_sub(x1, x2, p)
    a_new = fp2_mul(num, fp2_inv(den, p), p)
    b_new = fp2_sub(lhs1, fp2_mul(a_new, x1, p), p)
    return a_new, b_new

def velu_step(kernel_gen, l, a, b, p, aux):
    kernel = compute_kernel(kernel_gen, l, a, p)
    pushed = [velu_eval(pt, kernel, a, p) for pt in aux]
    probes = [img for img in pushed if img is not None]
    # Need two points with distinct x-coords for curve recovery.
    # Remove duplicates by x-coordinate.
    unique = []
    seen_x = set()
    for pr in probes:
        key = (pr[0][0] % p, pr[0][1] % p)
        if key not in seen_x:
            seen_x.add(key)
            unique.append(pr)
    probes = unique
    if len(probes) < 2:
        for x_int in range(2, p):
            x = (x_int, 0)
            x3 = fp2_mul(fp2_sqr(x, p), x, p)
            rhs = fp2_add(fp2_add(x3, fp2_mul(a, x, p), p), b, p)
            if rhs[1] != 0: continue
            if rhs[0] == 0: continue
            if pow(rhs[0], (p-1)//2, p) != 1: continue
            y_int = pow(rhs[0], (p+1)//4, p)
            probe = ((x_int, 0), (y_int, 0))
            img = velu_eval(probe, kernel, a, p)
            if img is None: continue
            key = (img[0][0] % p, img[0][1] % p)
            if key in seen_x: continue
            seen_x.add(key)
            probes.append(img)
            if len(probes) >= 2: break
    a_new, b_new = recover_curve(probes[0], probes[1], p)
    return a_new, b_new, pushed

def walk_chain(kernel_gen, l, e, a, b, p, aux, probes=None):
    """Walk an l^e isogeny as e steps of degree l.

    *probes* are extra points pushed through for curve recovery only;
    they are not returned.
    """
    gen = kernel_gen
    a_cur, b_cur = a, b
    cur_aux = list(aux)
    if probes is None:
        probes = []
    cur_probes = list(probes)
    for step in range(e):
        remaining = e - step
        step_gen = ec_mul(l**(remaining-1), gen, a_cur, p)
        push = [gen] + cur_aux + cur_probes
        a_new, b_new, pushed = velu_step(
            step_gen, l, a_cur, b_cur, p, push)
        gen = pushed[0]
        cur_aux = pushed[1:1+len(cur_aux)]
        cur_probes = pushed[1+len(cur_aux):]
        a_cur, b_cur = a_new, b_new
    return a_cur, b_cur, cur_aux

# --- SIDH at p = 431 = 2^4 * 3^3 - 1 ---
a0 = (1, 0)
b0 = (0, 0)

# Torsion bases (precomputed, verified in test suite).
PA = ((372, 0), (48, 0))    # order 16
QA = ((178, 168), (190, 428))  # order 16, independent of PA
PB = ((123, 0), (396, 0))   # order 27
QB = ((128, 133), (47, 6))  # order 27, independent of PB

# Alice: alpha = 3.
alpha = 3
RA = ec_add(PA, ec_mul(alpha, QA, a0, p), a0, p)
a_A, b_A, aux_A = walk_chain(RA, 2, 4, a0, b0, p, [PB, QB])
phiA_PB, phiA_QB = aux_A

# Bob: beta = 5.
beta = 5
RB = ec_add(PB, ec_mul(beta, QB, a0, p), a0, p)
a_B, b_B, aux_B = walk_chain(RB, 3, 3, a0, b0, p, [PA, QA])
phiB_PA, phiB_QA = aux_B

# Alice derives the shared secret.
# Pass torsion images as probes for curve recovery.
kernel_alice = ec_add(
    phiB_PA, ec_mul(alpha, phiB_QA, a_B, p), a_B, p)
a_AB_a, b_AB_a, _ = walk_chain(
    kernel_alice, 2, 4, a_B, b_B, p, [],
    probes=[phiB_PA, phiB_QA])

def j_inv_fp2(a, b, p):
    a3 = fp2_mul(fp2_sqr(a, p), a, p)
    four_a3 = fp2_mul((4, 0), a3, p)
    b2 = fp2_sqr(b, p)
    denom = fp2_add(four_a3, fp2_mul((27, 0), b2, p), p)
    return fp2_mul(fp2_mul((1728, 0), four_a3, p), fp2_inv(denom, p), p)

j_alice = j_inv_fp2(a_AB_a, b_AB_a, p)

# Bob derives the shared secret.
kernel_bob = ec_add(
    phiA_PB, ec_mul(beta, phiA_QB, a_A, p), a_A, p)
a_AB_b, b_AB_b, _ = walk_chain(
    kernel_bob, 3, 3, a_A, b_A, p, [],
    probes=[phiA_PB, phiA_QB])
j_bob = j_inv_fp2(a_AB_b, b_AB_b, p)

print(f"j_alice = {j_alice}")
# ==> j_alice = (315, 132)
print(f"j_bob   = {j_bob}")
# ==> j_bob   = (315, 132)
print(f"Match: {j_alice == j_bob}")
# ==> Match: True
