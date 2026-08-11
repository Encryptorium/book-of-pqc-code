# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "Repetition code"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/07-rep-encode.py

def rep_encode(message, r, n):
    codeword = []
    for bit in message:
        codeword.extend([bit] * r)
    codeword.extend([0] * (n - len(codeword)))
    return codeword

def rep_decode(received, r, n):
    k = n // r
    message = []
    for i in range(k):
        block = received[i * r : (i + 1) * r]
        ones = sum(block)
        message.append(1 if ones > r // 2 else 0)
    return message

msg = [1, 0, 1, 1]
R, N = 17, 83
cw = rep_encode(msg, R, N)

# Inject 5 errors into the first block
corrupted = list(cw)
for i in [2, 5, 8, 11, 14]:
    corrupted[i] = 1 - corrupted[i]

block0 = corrupted[:R]
ones = sum(block0)
print(f"corrupted block 0: {ones} ones out of {R}")
print(f"majority vote: {'1' if ones > R // 2 else '0'}")
recovered = rep_decode(corrupted, R, N)
print("decoded message:", recovered)
# ==> corrupted block 0: 12 ones out of 17
# ==> majority vote: 1
# ==> decoded message: [1, 0, 1, 1]
