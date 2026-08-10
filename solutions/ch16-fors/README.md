FORS and hypertree implementation for Chapter 16 of the Encryptorium Book of Post-Quantum Cryptography. `fors.py` implements FORS keygen, sign and verify over $k$ Merkle trees of $t$ secret leaves each, with the $k$ indices extracted from SHA-256 of the message. `hypertree.py` implements a $d$-layer hypertree of WOTS+ Merkle subtrees, with WOTS+, L-tree compression and the Merkle helpers inlined from Chapter 15 so the module has no cross-package import. Standard library only; no external dependencies.

This is a teaching implementation of the two components, not an implementation of SLH-DSA. Chapter 17 builds that. The divergences from FIPS 205 below are deliberate, and each one is the thing Chapter 17 restores.

**No ADRS and no tweakable hash family.** FIPS 205 keys every hash call with a 32-byte address and a public seed through $F$, $H$, $T_\ell$, PRF and $H_{\text{msg}}$ (FIPS 205 Section 11). This package calls bare SHA-256 and separates domains with byte-string prefixes (`b"fors"`, `b"ht"`, `b"leaf"`, `b"sk"`) and big-endian integer counters. The property the construction needs, a distinct input at every hash call, is preserved; the wire format is not FIPS 205's and this package produces no interoperable signatures.

**FORS secret leaves enter the Merkle tree directly.** FIPS 205 Algorithm 15 line 5 computes each FORS leaf as $F(\text{PK.seed}, \text{ADRS}, sk)$, separating the secret value from the public tree node. `fors_keygen` inserts the secret value itself.

**The FORS public key is a plain concatenate-and-hash.** This package computes `SHA-256(root_0 || ... || root_{k-1})` truncated to $n$. FIPS 205 Algorithm 17 line 24 uses a single tweakable-hash call $T_k(\text{PK.seed}, \text{forspkADRS}, \text{root})$ under an address whose type is `FORS_ROOTS`.

**WOTS+ public keys are compressed with the RFC 8391 L-tree.** FIPS 205 Algorithm 6 instead uses one call $T_{\text{len}}(\text{PK.seed}, \text{wotspkADRS}, \text{tmp})$ over the $\ell$ chain endpoints, and builds every tree over a power-of-two number of leaves. `_ltree` here is Chapter 15's, carried forward for continuity.

**The hypertree leaf index is supplied by the caller.** In SLH-DSA both signer and verifier derive the tree and leaf index from $H_{\text{msg}}(R, \text{PK.seed}, \text{PK.root}, M)$, which is what makes the scheme stateless. There is no message randomizer $R$ and no digest splitting in this package.

**Parameters are pedagogical.** The defaults are $k = 6$, $t = 16$, $n = 32$ for FORS and $d = 2$, $h' = 4$, $w = 16$, $n = 32$ for the hypertree. None of these is a FIPS 205 parameter set; the smallest approved set, SLH-DSA-128s, uses $k = 14$, $a = 12$, $h = 63$, $d = 7$, $h' = 9$ and $n = 16$ (FIPS 205 Table 2).

**Parameter derivation uses floating point.** Nine sites across the two modules take base-2 logarithms with `math.log2`, among them `_ell_params`, `_checksum`, `_base_w`, both copies of `_auth_path`, `message_indices` and `fors_verify`. FIPS 205 Section 3.1 requires that implementations of SLH-DSA use no floating-point arithmetic, and gives the integer form of $\ell_2$ as Algorithm 1; the chapter prints that integer form. At the parameters here the two agree exactly, so the shortcut costs nothing but would not be acceptable in a conforming implementation.

FIPS 205 defines FORS and the hypertree only as internal components of SLH-DSA. Neither is an approved standalone signature scheme, and the standalone versions in this package exist to be read and rebuilt rather than deployed.
