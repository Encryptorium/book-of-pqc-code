# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "Syndrome table decoding"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/04-syndrome-table-decoding.py

H = [
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1],
]

# Build syndrome table: syndrome -> error position.
table = {}
for j in range(7):
    syn = tuple(H[r][j] for r in range(3))
    table[syn] = j

print("syndrome table:")
for syn, pos in sorted(table.items()):
    print(f"  {syn} -> position {pos}")
# ==> syndrome table:
# ==>   (0, 0, 1) -> position 6
# ==>   (0, 1, 0) -> position 5
# ==>   (0, 1, 1) -> position 2
# ==>   (1, 0, 0) -> position 4
# ==>   (1, 0, 1) -> position 1
# ==>   (1, 1, 0) -> position 0
# ==>   (1, 1, 1) -> position 3
