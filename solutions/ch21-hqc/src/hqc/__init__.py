"""HQC public-key encryption: toy implementation for pedagogy.

Public API
----------
keygen   -- generate an HQC key pair
encrypt  -- encrypt a message (IND-CPA)
decrypt  -- decrypt a ciphertext (IND-CPA)
"""

from hqc.hqc import keygen, encrypt, decrypt

__all__ = ["keygen", "encrypt", "decrypt"]
