import mh
import solitaire
import socket
import common
import sys
import threading
import pickle

'''
Kl-Kl: Kommunikacio pelda: 8001 -> 8002

    MH({ id: 8001 })  ----> 
                    <---  MH({ id: 8002 })
    MH({ perm: key1  }) ---->
                    <---  MH({ perm: key2 })

LOOP: {{{
    SOL({ message: ... }) ---->
                    <---- SOL({ message: ... })


    SOL({ message: ... }) ---->
                    <---- SOL({ message: ... })
}}}
'''

def send_to_key_server(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((common.HOST, common.SERVER_PORT))
    common.send(s, message)
    rec = common.receive(s)
    s.close()
    return rec



def find_public_key(port):
    r = send_to_key_server({"type":0,"port":port})
    if r["status"] == "not found":
        return "not found"               
    return r["public_key"]



def print_usage():
    print("Usage:")
    print("\t",sys.argv[0],"query <target_port>  ##  show the public key of a client")
    print("\t",sys.argv[0],"<my_port> send <target_port>  ##  send a message to another client")
    print("\t",sys.argv[0],"<my_port> listen  ##  wait for other client to connect")
    exit()



def check_port(port_str):
    if not port_str.isnumeric():
        print("Port is not numeric")
        print_usage()
        return False
    port = int(port_str)
    if port < 0 or port > 0xFFFF:
        print("Port is invalid")
        print_usage()
        return False
    return port



def mh_send(socket, message, public_key):
    serialized = pickle.dumps(message)
    cypher = mh.encrypt_mh(serialized,public_key)
    common.send(socket, cypher)



def mh_receive(socket, private_key):
    cypher = common.receive(socket)
    plain = mh.decrypt_mh(cypher, private_key)
    deserialized = pickle.loads(plain)
    return deserialized



def sol_send(socket, message_str, common_key):
    serialized = message_str.encode("utf-8")
    (cypher, common_key)= solitaire.encrypt_solitaire(serialized, common_key)
    common.send(socket, cypher)
    return common_key



def sol_receive(socket, common_key):
    cypher = common.receive(socket)
    (plain, common_key) = solitaire.decrypt_solitaire(cypher, common_key)
    plain_str = plain.decode("utf-8")
    return (plain_str, common_key)



def generate_keys(port):
    #registration
    private_key = mh.generate_private_key()
    public_key = mh.create_public_key(private_key)
    print("Generated key-pair:",public_key, private_key)
    send_to_key_server({"type":1, "port":port, "public_key":public_key})
    return (private_key, public_key)



def send(port, target_port):
    (private_key, public_key) = generate_keys(port)
    target_key = find_public_key(target_port)
    if target_key == "not found":
        print("Not found")
        exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((common.HOST, target_port))

    # hello
    mh_send(s, {"port":port}, target_key)

    response = mh_receive(s, private_key)
    if (target_port != response["port"]):
        print("Not the same port")
        exit()

    print("Hello roundtrip finished")

    #secretKey1
    key1 = solitaire.generate_key()
    mh_send(s, {"perm":key1}, target_key)

    response = mh_receive(s, private_key)
    key2 = response["perm"]
    common_key = solitaire.combined_keys(key1,key2)

    print(common_key)
    print("Key exchange roundtrip finished")

    #send messages (loop)
    while True:
        input_str = input()
        common_key = sol_send(s, input_str, common_key)

        if input_str == "quit":
            break

        (reply, common_key) = sol_receive(s, common_key)
        print(reply)

    print("Messaging finished")
    s.close()



def listen(port):
    (private_key, public_key) = generate_keys(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((common.HOST, port))
    s.listen()
    clientsocket, address = s.accept()

    #hello
    request = mh_receive(clientsocket, private_key)
    target_port = request["port"]

    target_key = find_public_key(target_port)
    if target_key == "not found":
        print("Not found")
        exit()

    mh_send(clientsocket,{"port":port}, target_key)  
    print("Hello roundtrip finished")

    #secretKey2
    request = mh_receive(clientsocket, private_key)
    key1 = request["perm"]
    key2 = solitaire.generate_key()
    common_key = solitaire.combined_keys(key1,key2)

    mh_send(clientsocket, {"perm":key2}, target_key)  
    print(common_key)
    print("Key exchange roundtrip finished")

    #send messages (loop)
    while True:
        (request, common_key) = sol_receive(clientsocket, common_key)
        
        if request == "quit":
            break
        print(request)

        input_str = input()
        common_key = sol_send(clientsocket, input_str, common_key)

    print("Messaging finished")
    clientsocket.close()



def main():
    if len(sys.argv) < 3:
        print("Wrong parameters")
        print_usage()

    if sys.argv[1] == "query":
        port = check_port(sys.argv[2])
        target_key = find_public_key(port)
        if target_key == "not found":
            print("Not found.")
        else:
            print("The public key for", port, "is", target_key)
        return

    port = check_port(sys.argv[1])

    if sys.argv[2] == "send":
        if len(sys.argv) < 4:
            print("Not enough arguments.")
            print_usage()

        target_port = check_port(sys.argv[3])
        send(port, target_port)      

    elif sys.argv[2] == "listen":
        listen(port)
    else:
        print("Wrong arguments.")
        print_usage()

main()