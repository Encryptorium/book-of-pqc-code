"""Chapter 5: KEMs vs key agreement vs public-key encryption.

Two deliberately insecure pedagogical constructions, one per primitive
the chapter builds, plus an attack module:

- ``kem_primitives.dh`` -- toy Diffie-Hellman key agreement in
  ``(Z/pZ)^*``, plus the multiplicative-order routine that decides
  whether a candidate base generates the whole group.
- ``kem_primitives.rsa_kem`` -- the toy RSA-KEM: ``encap`` samples a
  random ``K`` and encrypts it under textbook RSA, ``decap`` runs raw RSA
  decryption to recover it.
- ``kem_primitives.attacks`` -- the mauling attack that breaks the toy
  KEM's IND-CCA2 security, and the bound on how often a uniform ``K``
  fails to be coprime to the modulus.

None of it is secure. See the package README.
"""
