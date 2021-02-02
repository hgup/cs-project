#=================== MODULES ====================#
import socket
import _thread
import sys
import pickle
from settings import Settings

inputs = sys.argv

def printStart():
    print(r'''
__     _______ ____ _____ _______  __
\ \   / / ____|  _ \_   _| ____\ \/ /
 \ \ / /|  _| | |_) || | |  _|  \  /
  \ V / | |___|  _ < | | | |___ /  \
   \_/  |_____|_| \_\|_| |_____/_/\_\

Server 2.0 for Vertex 2020
-----------------------------
Dedicated at Thy lotus feet
Don't play during study hours
-----------------------------
    ''')
class Server:

    def __init__(self, peers):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'localhost'
        if len(inputs) == 2:
            self.port = int(inputs[1])
        else:
            self.port = 9999
        self.server_ip = socket.gethostbyname(self.server)
        self.bind()
        self.peers = peers
        self.socket.listen(self.peers)
        self.settings = Settings()
        self.vertex = []
        self.available = [i for i in range(self.peers)]
        self.connected = []
        self.initVertex()
        self.acceptRequest()

    def bind(self):
        try:
            self.socket.bind((self.server, self.port))
        except socket.error as err:
            print(str(err))

    def getAvailableId(self):
        if len(self.available) != 0:
            self.available.sort()
            i = self.available[0]
            del self.available[0]
            self.connected.append(i)
            self.showAvailableId()
            return i
        self.showAvailableId()


    def setAvailableId(self,theId):
        self.available.append(theId)
        self.connected.remove(theId)
        self.showAvailableId()

    def showAvailableId(self):
        print('available:',self.available)
        print('connected:',self.connected)

    def initVertex(self):
        """ initialize vertex here """
        # [(x,y) , draw? ]
        self.vertex = [
                [(50,50),0],
                [(100,100),0],
                [(150,150),0]
                ][:self.peers]

    def threadedClient(self,conn):
        myId = self.getAvailableId()
        if myId is not None:
            x,y = self.vertex[myId][0] # init Rect
            # available myId is actually the game.net.id
            conn.send(str.encode(str([myId,x,y,self.peers]))) 
            self.mainloop(conn, myId)
            # now conn is useless
            self.setAvailableId(myId)
            print(f"id {myId} will now be available")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        else:
            conn.send(str.encode(str('Game is Full')))
        self.showAvailableId()

    def mainloop(self, conn, myId):
        running = True
        self.vertex[myId][1] = 1
        while running:
            try:
                data = conn.recv(2048)
                received = pickle.loads(data)
                if data:
                    self.vertex[received[0]][0] = received[1] # id[pos] = vec
                    conn.sendall(pickle.dumps(self.vertex))
                else:
                    conn.send(pickle.dumps(str(myId) + ' left the game'))
    
            except Exception as err:
                print(self.connections[myId][1],'left the game')
                self.vertex[myId][1] = 1
                running = False
                break

    def acceptRequest(self):
        self.connections = []
        c = 0
        print(f'[SERVER] OPEN AT PORT {self.port}')
        while True:
                c += 1
                print(f'[{c}] Waiting')
                conn,addr = self.socket.accept()
                self.connections.append((conn,addr))
                _thread.start_new_thread(self.threadedClient,(conn,))

if __name__ == "__main__":
    printStart()
    run = True
    while run:
        try:
            n = int(input('\tNUMBER OF PEERS: '))
            print("""
SERVER STARTED!
---------------""")
        except:
            print('By how many Peers I meant, specify a number...')
            continue
        Server(n)
        run = True if input("restart server? (y/n) : ") == 'y' else False

# received = [id, vec]
