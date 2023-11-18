import json
import socket
import threading
import StreamCypher

stop = False
connected = False

def receive_messages(client_socket, other_client, port2):
    global connected
    global stop
    global key
    global algorithm

    client_socket.listen(1)
    other_client_socket, other_client_address = client_socket.accept()
    if not connected:
        other_client.connect(('localhost', port2))
        print("Other client connected to you - press enter to continue")
        connected = True

    while True:
        try:
            message = other_client_socket.recv(4096)
            decrypted_message, new_key = StreamCypher.stream_encrypter(message, algorithm, key, 'D')
            key = new_key
            decrypted_message = decrypted_message.decode()
            if not decrypted_message or decrypted_message == 'exit':
                stop = True
                break

            print("\b" * 40, end="", flush=True)
            print(f"Received: {decrypted_message}")
            print("Enter a message (type 'exit' to quit): ", end="")

        except Exception as e:
            print(f"Error receiving data: {e}")
            break

    print("\b" * 40, end="", flush=True)
    print("Other client disconnected. Press enter to quit")
    other_client_socket.close()
    return


def start_client(port1, port2):
    global connected
    global stop
    global key
    global algorithm

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    other_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.bind(('localhost', port1))

    receive_thread = threading.Thread(target=receive_messages, args=(client, other_client, port2))
    receive_thread.start()

    if not connected:
        answer = input("Do you want to connect to the other client? (y/n)\n")
        if answer == 'y':
            other_client.connect(('localhost', port2))
            connected = True
        elif answer == "n":
            return

    while True and connected:
        message = input("Enter a message (type 'exit' to quit): ")
        if message.lower() == 'exit' or stop:
            break

        message = message.encode()
        encrypted_message, new_key = StreamCypher.stream_encrypter(message, algorithm, key, 'E')
        key = new_key
        other_client.send(encrypted_message)

    other_client.close()
    return


if __name__ == "__main__":

    with open("configuration.json") as confFile:
        conf = json.load(confFile)

    key = conf["key"]
    algorithm = conf["algorithm"]

    choice = input("Client1 = 1, Client2 = 2\n")
    if choice == "1":
        start_client(5895, 5896)
    else:
        start_client(5896, 5895)
