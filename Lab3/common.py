import pickle

SERVER_PORT = 8000
HOST = 'localhost'

def send(socket, message):
    serialized = pickle.dumps(message)
    length = len(serialized).to_bytes(4, 'big')
    #a csomag formatuma: 4 byte a hossz(big end.) + binaris adat
    socket.sendall(length+serialized)

def receive(socket):
    length = socket.recv(4)
    length = int.from_bytes(length, 'big')

    serialized = bytes()
    while length > 0:
        actual = socket.recv(2048)
        serialized = serialized + actual
        length = length - len(actual)

    return pickle.loads(serialized)