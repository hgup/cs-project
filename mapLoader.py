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
        self.loadMap()
        self.dimensions = (self.chunks[0]*32,self.chunks[1]*18)
        print(self.chunks,self.dimensions)
        self.map_coords_x = numpy.arange(self.dimensions[0]) * 40
        self.map_coords_y = numpy.arange(self.dimensions[1]) * 40
        self.blit_coords_x = numpy.arange(self.dimensions[0]) * 40
        self.blit_coords_y = numpy.arange(self.dimensions[1]) * 40
        self.sprites = []
        self.loadSprites()

    def loadMap(self):
        self.bg = pygame.image.load(self.path+'bg.png')
        with open(self.path +'map.dat', 'rb') as f:
            self.chunks = pickle.load(f)
            self.data = pickle.load(f)
            print(self.chunks)

    def loadSprites(self):
        # if self.sprites not defined that means map not loaded
        self.sprites = []
        self.group = pygame.sprite.Group()
        for y in range(self.dimensions[1]):
            self.sprites.append([])
            for x in range(self.dimensions[0]):
                k = Block((x,y),self.data[y][x],self.level)
                self.sprites[y].append(k)
                self.group.add(k)

    def draw(self, screen,cam):
        # be sure to update before calling
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                screen.blit(self.sprites[y][x].image,
                        (self.sprites[y][x].rect.x - cam[0],self.sprites[y][x].rect.y - cam[1]))

if __name__ == "__main__":
    Map(1)
