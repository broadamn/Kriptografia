def perform_solitaire(deck):
    deck = deck[:]
    while True:
        deck = move_joker1(deck)
        deck = move_joker2(deck)
        deck = triple_cut(deck)
        deck = count_cut(deck)
        value = extract_value(deck)
        if value > 0:
            return value, deck


def move_joker1(deck):
    white_joker_pos = deck.index(53)
    if white_joker_pos < 53:
        deck[white_joker_pos], deck[white_joker_pos + 1] = deck[white_joker_pos + 1], deck[white_joker_pos]
    else:
        deck = [deck[0], 53] + deck[1:53]
    return deck


def move_joker2(deck):
    black_joker_position = deck.index(54)
    if black_joker_position < 52:
        deck[black_joker_position: black_joker_position + 3] = deck[black_joker_position + 1: black_joker_position + 4] + [deck[black_joker_position]]
    elif black_joker_position == 52:
        deck = [deck[0], 54] + deck[1:52] + [deck[53]]
    else:
        deck = [deck[0], deck[1], 54] + deck[2:53]
    return deck


def triple_cut(deck):
    white_joker_pos = deck.index(53)
    black_joker_pos = deck.index(54)
    first, second = min(white_joker_pos, black_joker_pos), max(white_joker_pos, black_joker_pos)
    deck = deck[(second + 1):54] + deck[first:(second + 1)] + deck[0:first]
    return deck


def count_cut(deck):
    last_card_value = deck[53]
    if last_card_value <= 52:
        deck = deck[last_card_value:53] + deck[0:last_card_value] + [last_card_value]
    return deck


def extract_value(deck):
    top_card_value = deck[0]
    return -1 if top_card_value > 52 else deck[top_card_value]


def generate_keybytes(message, key):
    n = len(message)
    key_bytes = bytearray(n)
    for i in range(n):
        (x1, key) = perform_solitaire(key)
        (x2, key) = perform_solitaire(key)
        key_byte = (x1 & 0xF) << 4 | (x2 & 0xF)
        key_bytes[i] = key_byte

    return key_bytes, key