import socket
import pickle  # serializatiom of objects

class Network:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = "192.168.1.17"  # ip address from ipconfig
        self.port = 5547
        self.address = (self.server_address, self.port)  # server adress

    # connects client to the server. Returns player_number
    def connect(self):
        try:
            self.client_socket.connect(self.address)
            return pickle.loads(self.client_socket.recv(2048))
            # return self.client.recv(2048).decode()
        except:
            print("connect error")
            pass

    # sends data to server: (keys) - pressed keys
    # and returns answer from server (game_info)
    def send(self, data):
        try:
            # self.client.send(str.encode(data))
            self.client_socket.send(pickle.dumps(data))  # send to server
            return pickle.loads(self.client_socket.recv(2048*8))  # receive from server
        except socket.error as e:
            print("send error")
            print(e)

