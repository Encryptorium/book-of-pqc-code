# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "Quasi-cyclic codes"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/08-quasi-cyclic-codes.py

# Key-size savings from quasi-cyclic structure.
# Random [2n, n] code: parity-check matrix has n * 2n bits.
# QC code: store one row of the circulant block, n bits.

n_hqc1 = 17_669
random_matrix_bits = n_hqc1 * (2 * n_hqc1)
qc_bits = n_hqc1
savings = random_matrix_bits / qc_bits

# Ceil division: 17,669 bits needs 2,209 bytes, not 2,208.
random_matrix_bytes = -(-random_matrix_bits // 8)
qc_bytes = -(-qc_bits // 8)

print(f"random matrix: {random_matrix_bits:,} bits = {random_matrix_bytes:,} bytes")
print(f"QC representation: {qc_bits:,} bits = {qc_bytes:,} bytes")
print(f"savings factor: {savings:,.0f}x")
# ==> random matrix: 624,387,122 bits = 78,048,391 bytes
# ==> QC representation: 17,669 bits = 2,209 bytes
# ==> savings factor: 35,338x
