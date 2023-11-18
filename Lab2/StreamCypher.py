import solitaire


def encrypt(message, alg, seed):
    if alg == 'S':
        key_bytes, new_key = solitaire.generate_keybytes(message, seed)
        n = len(message)
        encrypted = bytearray(n)

        for i in range(n):
            encrypted[i] = key_bytes[i] ^ message[i]
    else:
        return
    return encrypted, new_key


def decrypt(message, alg, key):
    if alg == 'S':
        key_bytes, new_key = solitaire.generate_keybytes(message, key)
        n = len(message)
        decrypted = bytearray(n)

        for i in range(n):
            decrypted[i] = key_bytes[i] ^ message[i]
    else:
        return
    return decrypted, new_key


def stream_encrypter(message, alg, seed, action):
    if action == 'E':
        return encrypt(message, alg, seed)
    else:
        return decrypt(message, alg, seed)
