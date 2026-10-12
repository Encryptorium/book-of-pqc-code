"""Chapter 5: KEMs vs key agreement vs public-key encryption.

Deliberately insecure pedagogical constructions, the chapter's attack on
its toy RSA-KEM, and the Fujisaki-Okamoto toy:

- ``kem_primitives.dh`` -- toy Diffie-Hellman key agreement in
  ``(Z/pZ)^*``, plus the multiplicative-order routine that decides
  whether a candidate base generates the whole group.
- ``kem_primitives.rsa_kem`` -- the toy RSA-KEM: ``encap`` samples a
  random ``K`` and encrypts it under textbook RSA, ``decap`` runs raw RSA
  decryption to recover it.
- ``kem_primitives.attacks`` -- the mauling attack that breaks the toy
  KEM's IND-CCA2 security, and the bound on how often a uniform ``K``
  fails to be coprime to the modulus.
- ``kem_primitives.elgamal`` -- toy ElGamal over the subgroup of squares
  mod 2063, the chapter's Diffie-Hellman used to encrypt. One decryption
  of a mauled ciphertext gives its plaintext away.
- ``kem_primitives.fo`` -- the same ElGamal put through the
  Fujisaki-Okamoto pattern: coins derived from the message, a
  re-encryption check, and implicit rejection.

None of it is secure. See the package README.
"""
