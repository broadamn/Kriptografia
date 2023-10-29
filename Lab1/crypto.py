#!/usr/bin/env python3 -tt
"""
File: crypto.py
---------------
Assignment 1: Cryptography
Course: CS 41
Name: Biro Adam
SUNet: baim2119

"""
import math
import random
import re

import utils

# Caesar Cipher


def encrypt_caesar(plaintext, key):
    encrypted = "".join([chr(((ord(char) - 65 + key) % 26) + 65) for char in plaintext])
    return encrypted


def decrypt_caesar(ciphertext, key):
    decrypted = "".join(
        [chr(((ord(char) - 65 - key) % 26) + 65) for char in ciphertext]
    )
    return decrypted


# Vigenere Cipher


def encrypt_vigenere(plaintext, keyword):
    ciphertext = ""
    len_k = len(keyword)
    index = 0

    for char in plaintext:
        if char.isalpha():
            shift = ord(keyword[index]) - ord("A")

            encrypted_char = chr(((ord(char) - ord("A") + shift) % 26) + ord("A"))
            ciphertext += encrypted_char

            index = (index + 1) % len_k
        else:
            ciphertext += char

    return ciphertext


def decrypt_vigenere(ciphertext, keyword):
    plaintext = ""
    len_k = len(keyword)
    index = 0

    for char in ciphertext:
        if char.isalpha():
            shift = ord(keyword[index]) - ord("A")

            encrypted_char = chr(((ord(char) - ord("A") - shift) % 26) + ord("A"))
            plaintext += encrypted_char

            index = (index + 1) % len_k
        else:
            plaintext += char

    return plaintext


def encrypt_scytale(plaintext, circumference):
    if circumference <= 0:
        return "Invalid circumference"

    padding = (circumference - len(plaintext) % circumference) % circumference
    plaintext += " " * padding

    rows = len(plaintext) // circumference
    ciphertext = ""
    for col in range(circumference):
        for row in range(rows):
            ciphertext += plaintext[row * circumference + col]

    return ciphertext


def decrypt_scytale(ciphertext, circumference):
    if circumference <= 0:
        return "Invalid circumference"

    rows = len(ciphertext) // circumference

    plaintext = ""
    for row in range(rows):
        for col in range(circumference):
            plaintext += ciphertext[col * rows + row]

    return plaintext.strip()


def encrypt_railfence(plaintext, num_rails):
    i, j, k = 0, 0, 1
    net = []
    for x in range(0, num_rails): net.append([])
    while i < len(plaintext):

        net[j].append(plaintext[i])

        if j == 0:
            k = 1

        if j == num_rails - 1:
            k = -1

        i += 1
        j += k

    crypted = ''
    for x in range(0, num_rails): crypted = crypted + ''.join(map(str, net[x]))
    return crypted


def decrypt_railfence(ciphertext, num_rails):
    net = []
    for i in range(0, num_rails): net.append(['0' for j in range(0, len(ciphertext))])

    i, j, k = 0, 0, 1

    for j in range(0, len(ciphertext)):

        net[i][j] = '*'

        if i == 0:
            k = 1

        if i == num_rails - 1:
            k = -1

        i += k

    k = 0
    for i in range(0, num_rails):
        for j in range(0, len(ciphertext)):
            if net[i][j] == '*':
                net[i][j] = ciphertext[k]
                k += 1

    i, j, k = 0, 0, 1
    decrypted = []
    for j in range(0, len(ciphertext)):

        decrypted.append(net[i][j])

        if i == 0:
            k = 1

        if i == num_rails - 1:
            k = -1

        i += k

    return ''.join(map(str, decrypted))



# Merkle-Hellman Knapsack Cryptosystem


def generate_private_key(n=8):
    # Generate a superincreasing sequence 'w' of length 'n'
    
    w = []
    w.append(random.randint(1, 100))
    for _ in range(n-1):
        s = sum(w)
        w.append(random.randint(s, 2*s))
        
    if(utils.is_superincreasing(w)):
        print("jo")
    else:
        print("nem jo")
    # Choose an integer 'q' greater than the sum of all elements in 'w'
    q = random.randint(sum(w) + 1, 2 * sum(w))

    # Discover an integer 'r' between 2 and 'q' that is coprime to 'q'
    r = random.randint(2, q)
    while not utils.coprime(r, q):
        r = random.randint(2, q)

    return (w, q, r)


def create_public_key(private_key):
    w, q, r = private_key
    # Compute the public key 'beta'
    beta = [(r * wi) % q for wi in w]
    return tuple(beta)


def encrypt_mh(message, public_key):
    n = len(public_key)
    ciphertexts = []

    for chunk in [message[i : i + n] for i in range(0, len(message), n)]:
        bits = [utils.byte_to_bits(byte) for byte in chunk]
        c = sum(ai * bi for ai, bi in zip(bits, public_key))
        ciphertexts.append(c)

    return ciphertexts


def decrypt_mh(message, private_key):
    w, q, r = private_key
    s = utils.modinv(
        r, q
    )  # Compute the modular inverse of r mod q using Extended Euclidean algorithm

    decrypted_bytes = bytearray()
    for c in message:
        c_prime = (c * s) % q

        superincreasing_subset = []
        i = len(w) - 1

        while i >= 0 and c_prime >= w[i]:
            superincreasing_subset.append(w[i])
            c_prime -= w[i]
            i -= 1

        if c_prime != 0:
            # If c_prime is not fully reduced to zero, it means there's no valid superincreasing subset
            # This indicates a decryption error
            raise ValueError("Decryption error. Invalid ciphertext.")

        # Reconstruct the original byte from the superincreasing subset
        original_byte = 0
        for subset_element in superincreasing_subset:
            original_byte |= 1 << w.index(subset_element)

        decrypted_bytes.append(original_byte)

    return decrypted_bytes
