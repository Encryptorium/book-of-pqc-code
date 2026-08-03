"""Chapter 6: Digital signatures reconsidered.

Two textbook signature schemes, the attack that breaks each one, and the
repair for the first:

- ``signature_attacks.rsa_forgery`` -- textbook RSA signing on the
  chapter's 64-bit modulus, the multiplicative forgery that follows from
  raw exponentiation being a group homomorphism, and the full-domain-hash
  construction that removes the message-level homomorphism the attacker
  used.
- ``signature_attacks.nonce_reuse`` -- ECDSA on a toy prime-order group,
  and the closed-form recovery of the private key from two signatures
  produced under the same nonce.

Neither scheme here is secure, and the FDH construction is pedagogical
rather than deployable. See the package README.
"""
