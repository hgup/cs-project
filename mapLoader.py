import pygame
import pickle
class Map:
    
    def __init__(self, level):
        self.bg = None
        self.id = level
        self.path = r'./WorldData/Level ' + str(level) +'/' 
        self.loadMap()

    def loadMap(self):
        self.bg = pygame.image.load(self.path+'bg.png')
        with open(self.path +'map.dat', 'rb') as f:
            self.mapData = pickle.load(f)

if __name__ == "__main__":
    _map = Map(1)
    print(len(_map.mapData[0]))
    print(len(_map.mapData))
