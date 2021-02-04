import socket
import pickle
import mapLoader

class Network:

    def __init__(self,address,port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = address
        self.port = int(port)
        self.addr = (self.host, self.port)
        reply = self.connect()
        self.id,x,y,self.peers = reply
        self.initRect = (x,y)
        self.client.send('Received loginData'.encode())
        # get map data
        self.getFile("MultiplayerData/map.dat")
        # get map bg
        self.getFile("MultiplayerData/bg.png")
        self.map = mapLoader.Map(1)

    def getFile(self,fileName):
        d = self.client.recv(2048)
        self.client.settimeout(1)
        full_data = b''
        while d:
            full_data += d
            try:
                d = self.client.recv(2048)
            except:
                break
        self.client.settimeout(None)
        with open(fileName,'wb') as f:
            f.write(full_data)
        self.client.send('Received:123'.encode())

    def connect(self):
        # connect self to self.addr
        self.client.connect(self.addr)
        return pickle.loads(self.client.recv(32))


    def send(self, data):
        try:
            self.client.send(data)
            reply = self.client.recv(2048)
            return reply
        except Exception as err:
            print(str(err))

if __name__ == "__main__":
    n = Network()
