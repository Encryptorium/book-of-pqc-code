# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 18: Hash-based signature cryptanalysis
# Section: "Security comparison across Part III"
# https://book.encryptorium.com/part-3-hash-based/ch18-hash-based-signature-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch18/06-security-comparison-across-part-iii.py

header = f"{'scheme':<24} {'pre_cl':>7} {'pre_qu':>7} {'coll_cl':>8} {'coll_qu':>8} {'state':>10}"
print(header)
rows = [
    ("Lamport+Merkle (n=32)", 256, 128, 128, 85, "stateful"),
    ("WOTS+/XMSS (n=32)",    256, 128, 128, 85, "stateful"),
    ("SLH-DSA-128s",          128,  64,  64, 42, "stateless"),
    ("SLH-DSA-192s",          192,  96,  96, 64, "stateless"),
    ("SLH-DSA-256s",          256, 128, 128, 85, "stateless"),
]
for nm, pc, pq, cc, cq, st in rows:
    print(f"{nm:<24} {pc:>7} {pq:>7} {cc:>8} {cq:>8} {st:>10}")
# ==> scheme                    pre_cl  pre_qu  coll_cl  coll_qu      state
# ==> Lamport+Merkle (n=32)        256     128      128       85   stateful
# ==> WOTS+/XMSS (n=32)            256     128      128       85   stateful
# ==> SLH-DSA-128s                 128      64       64       42  stateless
# ==> SLH-DSA-192s                 192      96       96       64  stateless
# ==> SLH-DSA-256s                 256     128      128       85  stateless
