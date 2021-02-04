import sys
import socket
import pickle
import mapLoader
import pygame
import random

loadingMessage = ['Baking the cookies','Making the track ready','Praying To Swami']

class Network:

    def __init__(self,game, address,port,name):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #-------------------- GAME STUFF -------------------#
        self.game = game
        self.host = address
        self.port = int(port)
        self.addr = (self.host, self.port)
        self.name = name
        reply = self.connect()
        if reply is not None:
            self.id,x,y,self.peers,level = reply
            self.initRect = (x,y)
            self.game.loading('Sending loginData')
            self.client.send('Sent loginData'.encode())
            # get map data
            load = loadingMessage.copy()
            a = random.choice(loadingMessage)
            load.remove(a)
            self.game.loading(a)
            self.getFile("MultiplayerData/map.dat")
            # get map bg
            self.game.loading(random.choice(load))
            self.getFile("MultiplayerData/bg.png")
            self.map = mapLoader.Map(level)

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
        try:
            self.client.connect(self.addr)
            self.client.send(pickle.dumps([self.name,False])) # [ name, paused ]
            print('connected')
            try:
                return pickle.loads(self.client.recv(32))
                print('joined')
            except:
                self.game.sorry('GAME IS FULL!','Please Wait', size = 30)
        except Exception as err:
            self.game.sorry(f'An error Occured while connecting',f'Error: {err}',size=30)



    def send(self, data):
        try:
            self.client.send(data)
            reply = self.client.recv(2048)
            return reply
        except Exception as err:
            print(str(err))

if __name__ == "__main__":
    n = Network()
