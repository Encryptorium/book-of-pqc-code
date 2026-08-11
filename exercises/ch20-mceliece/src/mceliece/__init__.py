"""McEliece public-key cryptosystem: toy implementation for pedagogy.

Public API
----------
keygen   -- generate a McEliece key pair
encrypt  -- encrypt a k-bit message
decrypt  -- decrypt a ciphertext
"""

from mceliece.mceliece import keygen, encrypt, decrypt

__all__ = ["keygen", "encrypt", "decrypt"]
