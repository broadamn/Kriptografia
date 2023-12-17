import random

def combined_keys(key1, key2):
    key = [0]*len(key1)
    for i in range(0, len(key1)):
        key[i] = key2[key1[i]-1]
    return key


def generate_key():
    key = list(range(1,55))
    random.shuffle(key)
    return key


def solitaire(key):
    key = key[:]
    while True:
        key = step_a(key)
        key = step_b(key)
        key = step_c(key)
        key = step_d(key)
        value = step_e(key)
        if value > 0:
            return (value, key)

def step_a(key):
    pos_wjoker = key.index(53)
    if pos_wjoker < 53:
        temp = key[pos_wjoker]
        key[pos_wjoker] = key[pos_wjoker+1]
        key[pos_wjoker+1] = temp
    else:
        key = [key[0], 53] + key[1:53]
    return key

def step_b(key):
    pos_bjoker = key.index(54)
    if pos_bjoker < 52:
        temp = key[pos_bjoker]
        key[pos_bjoker] = key[pos_bjoker+1]
        key[pos_bjoker+1] = key[pos_bjoker+2]
        key[pos_bjoker+2] = temp
    elif pos_bjoker == 52:
        key = [key[0], 54] + key[1:52] + [key[53]]
    else:
        key = [key[0], key[1], 54] + key[2:53]
    return key

def step_c(key):
    pos_wjoker = key.index(53)
    pos_bjoker = key.index(54)
    first = min(pos_wjoker, pos_bjoker)
    second = max(pos_wjoker, pos_bjoker)
    key = key[(second+1):54] + key[first:(second+1)] + key[0:first]
    return key

def step_d(key):
    n = key[53]
    if n <= 52:
        key = key[n:53] + key[0:n] + [n]
    return key

def step_e(key):
    first = key[0]
    if first > 52:
        return -1
    else:
        return key[first]

def encrypt_solitaire(message, key):
    '''
    :type message: bytes
    '''
    n = len(message)
    result = bytearray(n)
    for i in range(0, n):
        (value1, key) = solitaire(key)
        (value2, key) = solitaire(key)

        key_byte = (value1 & 0xF) << 4 | (value2 & 0xF) 
        result[i] = key_byte^message[i] #XOR

    return (result, key)


def decrypt_solitaire(message, key):
    return encrypt_solitaire(message, key)