#=================== MODULES ====================#
import socket
import _thread
from threading import Thread
import sys
import pickle
from settings import Settings
import mapLoader
import time

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
class Server(Thread):

    def __init__(self, peers, port = None, level = 1):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server = 'localhost'
        self.port = 9999 if port is not None else port
        self.level = level
        self.peers = peers

    def run(self):
        self.running = True
        self.mapPath = r'./WorldData/Level ' + str(self.level) +'/' 
        if len(inputs) == 2:
            self.port = int(inputs[1])
        self.server_ip = socket.gethostbyname(self.server)
        self.bind()
        self.socket.listen(self.peers)
        self.settings = Settings()
        self.vertex = []
        self.index = { 'pos' : 0, 'draw' : 1, 'name' : 2,'role' : 3}
        self.available = [i for i in range(self.peers)]
        self.connected = []
        self.initVertex()
        _thread.start_new_thread(self.control,())
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
        # [(x,y) 0, draw? 1, name  2]
        self.vertex = [
                [(50,50),0,'p1'],
                [(250,100),0,'p2'],
                [(450,150),0,'p3'],
                [(150,100),0,'p4'],
                [(550,150),0,'p5'],
                [(75,100),0,'p6'],
                [(650,150),0,'p7'],
                [(150,100),0,'p8'],
                [(90,150),0,'p9'],
                ][:self.peers]

    def threadedClient(self,conn,initData):
        myId = self.getAvailableId()
        if myId is not None:
            x,y = self.vertex[myId][0] # init Rect
            # available myId is actually the game.net.id
            conn.send(pickle.dumps([myId,x,y,self.peers,self.level]))
            print(conn.recv(32).decode())
            self.sendFile(self.mapPath + 'map.dat', conn)
            self.sendFile(self.mapPath + 'bg.png', conn)
            self.mainloop(conn, myId,initData)
            self.vertex[myId][1] = 0
            # now conn is useless
            self.setAvailableId(myId)
            print(f"id {myId} will now be available")
            #conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        else:
            conn.send(str.encode(str('Game is Full')))
        self.showAvailableId()
        print(f'[{myId}]',':thread ended')

    def newGame(self):
        while self.running:
            if len(self.alivePlayers) == 1:
                self.gameWon(self.alivePlayers[0])


    def gameloop(self):
        while True:
            pass
            # events
            # updates

    def control(self):
        self.zzz = ''
        while self.running:
            self.zzz += 'z'
            if len(self.zzz) > 3:
                self.zzz = 'z'
            time.sleep(0.4)
        else:
            print('Shutting Down Server!')
            self.socket.close()
            try:
                dummySock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dummySock.connect((self.server_ip,self.port))
                dummySock.close()
            except Exception as err:
                print('[130]',err)

    def mainloop(self, conn, myId,initData):
        running = True
        self.vertex[myId][1] = 1
        lastData = initData # [ name , paused ]
        while self.running:
            try:
                data = conn.recv(2048)
                received = pickle.loads(data) # [ id, rect, paused ]
                tempData = received[2:]
                if received[2]: # if paused
                    self.vertex[received[0]][self.index['name']] = self.zzz
                else:
                    self.vertex[received[0]][self.index['name']] = initData[0]
                    lastData = tempData
                if data:
                    self.vertex[received[0]][self.index['pos']] = received[1] # id[pos] = vec
                    conn.sendall(pickle.dumps(self.vertex))
                else:
                    conn.send(pickle.dumps(str(myId) + ' left the game'))
    
            except Exception as err:
                break
        print(self.connections[myId][1],'left the game')
        #self.connections.remove(myId)
        self.vertex[myId][1] = 1

    def acceptRequest(self):
        self.connections = []
        c = 0
        print(f'[SERVER] OPEN AT PORT {self.port}')
        while self.running:
                c += 1
                print('---------------')
                print(f'[{c}] Waiting')
                try:
                    conn,addr = self.socket.accept()
                    initData = pickle.loads(conn.recv(32)) # [ name, paused ]
                except:
                    break
                self.connections.append((conn,addr))
                a = _thread.start_new_thread(self.threadedClient,(conn,initData))

    def quit(self):
        self.running = False
        self.closeAllConn()

    def closeAllConn(self):
        for conn in self.connections:
            try:
                conn[0].shutdown(socket.SHUT_RDWR)
                conn[0].close()
                print(conn[1],': connection closed')
            except Exception as err:
                print('[184]',err)
        print('All Connections Closed!')

    def sendFile(self,fileName,sock):
        with open(fileName,'rb') as f:
            d = f.read()
            sock.sendall(d)
        if sock.recv(32).decode() == 'Received:123':
            print(f'Received {fileName}')

if __name__ == "__main__":
    printStart()
    n = ''
    defaults = [1, 9999, 1]
    ques = [f'\tNUMBER OF PEERS:({defaults[0]})  ',f'\tPORT:({defaults[1]})  ',f'\tLEVEL TO PLAY:({defaults[2]}) ']
    c = 0
    while c < 3:
        try:
            e = input(ques[c])
            n = int(e)
            defaults[c] = n
            c += 1
        except:
            if not e:
                c += 1
                continue
            print('PLEASE ENTER VALID DATA:🙏')
            print("""
SERVER STARTED!
---------------""")
    myServer = Server(*defaults)
    myServer.start()


# received = [id, vec]
