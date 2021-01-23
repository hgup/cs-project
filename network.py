import socket

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = 'localhost'
        self.port = 9999
        self.addr = (self.host, self.port)
        reply =self.connect()
        try:
            self.id,x,y,peers = eval(reply)
            self.peers = peers
            self.initRect = (x,y)
        except:
            print(reply)


    def connect(self):
        # connect self to self.addr
        self.client.connect(self.addr)
        return self.client.recv(32).decode() #id


    def send(self, data):
        try:
            self.client.send(data)
            reply = self.client.recv(2048)
            return reply
        except Exception as err:
            print(str(err))

if __name__ == "__main__":
    n = Network()
