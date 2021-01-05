import numpy
import pygame
import pickle
import SpriteImages
SpriteImages = SpriteImages.SpriteImages()

class Block(pygame.sprite.Sprite):

    def __init__(self, pos, value, level):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.value = int(value)
        self.level = level
        self.sprites = SpriteImages.levels[level]
        self.image = self.sprites[self.value]
        #----------- UPDATING THE RECT ---------------------#
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos*40

    def update(self):
        self.image = self.sprites[self.value]

class Map:
    # self.data contains the value of that block coord
    
    def __init__(self, level):
        self.bg = None
        self.level = level
        self.path = r'./WorldData/Level ' + str(level) +'/' 
        self.spriteImages = SpriteImages.levels[level]
        self.map_coords_x = numpy.arange(64) * 40
        self.map_coords_y = numpy.arange(36) * 40
        self.blit_coords_x = numpy.arange(64) * 40
        self.blit_coords_y = numpy.arange(36) * 40
        self.sprites = []
        self.loadSprites()

    def loadMap(self):
        self.bg = pygame.image.load(self.path+'bg.png')
        with open(self.path +'map.dat', 'rb') as f:
            self.data = pickle.load(f)

    def loadSprites(self):
        # if self.sprites not defined that means map not loaded
        self.loadMap()
        self.sprites = []
        self.group = pygame.sprite.Group()
        for y in range(36):
            self.sprites.append([])
            for x in range(64):
                k = Block((x,y),self.data[y][x],self.level)
                self.sprites[y].append(k)
                self.group.add(k)

    def draw(self, screen,cam):
        # be sure to update before calling
        for y in range(36):
            for x in range(64):
                screen.blit(self.sprites[y][x].image,(self.sprites[y][x].rect.x - cam[0],self.sprites[y][x].rect.y - cam[1]))

        
        

if __name__ == "__main__":
    _map = Map(1)
    print(len(_map.data[0]))
    print(len(_map.data))
