#----------------------- IMPORTS --------------------------#
import os
import pygame
import numpy
import pickle
import settings
from pygame.locals import *
import SpriteImages
# make a click and go level editor
    # mouse over a block when left click... creates a block
    # mouce over with right click ... deletes a block

# OPTIONAL
    # try to get grid lines to give it a blue print feel
    # later... give the options on the right hand side... to select different blocks
class Block(pygame.sprite.Sprite):
    # _id is a tuple that contains the 2d value of the main MapEditor.map
    def __init__(self, _id, value, level):
        super().__init__()
        self.pos = _id
        self.value = int(value)
        self.sprites = SpriteImages.levels[level]
        self.image = self.sprites[self.value]
        #----------- UPDATING THE RECT ---------------------#
        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0] * 40
        self.rect.y = self.pos[1] * 40

    def update(self):
        self.image = self.sprites[self.value]

class MapEditor:
    def __init__(self):
        #------------------ MAP ID STUFF -------------------#
        self.level = int(input("Enter map number:")) #1,2,3,4...
        self.path = r'./WorldData/Level ' +str(self.level)+ r'/'
        self.map = numpy.ones((36,64))
        self.map_coords_x = numpy.arange(64) * 40
        self.map_coords_y = numpy.arange(36) * 43
        self.cam = pygame.math.Vector2(0,0)
        self.sprites = SpriteImages.levels[self.level]
        #------------------ PYGAME STUFF -------------------#
        self.settings = settings.Settings()        
        self.screen = pygame.display.set_mode((self.settings.width + 200,self.settings.height + 50))
        self.canvas = pygame.Surface((self.settings.width,self.settings.height))
        self.fpsClock = pygame.time.Clock()
        #----------------- RUNTIME LOGIC STUFF -------------#
        self.running = True
        self.scrolling = False
        self.showGridLines = True
        self.loadMap()
        self.loadBlocks()
        self.mainloop()
    #====================== MAIN ========================# 
    #====================================================#
    def mainloop(self):
        while self.running:
            #-------------- EVENTS AND UPDATES -------------#
            self.events()
            self.update()
            #-------------------- DRAWING ------------------#
            self.screen.fill((0,0,0))
            self.drawMap()
            self.drawHud()
            self.blockGroup.draw(self.canvas)
            self.drawGridLines()
            self.screen.blit(self.canvas, (200,50))
            #------------------ UPDATE AND TICK ------------#
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)

    def events(self):
        for event in pygame.event.get():
            #---------------- KEYBOARD EVENTS --------------#
            if event.type == QUIT:
                self.running = False
            if event.type == KEYUP:
                if event.key == K_g:
                    self.showGridLines = not self.showGridLines
            #------------------- MOUSE EVENTS --------------#
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 2:
                    self.scrolling = True
                    pygame.mouse.get_rel()
            if event.type == MOUSEBUTTONUP:
                if event.button == 2:
                    self.scrolling = False

    def update(self):
        if self.scrolling:
            self.cam += pygame.mouse.get_rel()
        # update the map

    def loadBlocks(self):
        #-------------- CREATING Block OBJECTS -------------#
        self.blocks = []
        self.blockGroup = pygame.sprite.Group()
        for y in range(36):
            self.blocks.append([])
            for x in range(64):
                k = Block((x,y),self.map[y][x],self.level)
                self.blocks[y].append(k)
                self.blockGroup.add(k)

    #==================== FILE HANDLING ====================#
    #=======================================================#

    def loadMap(self):
        # --------------- self.map IS CREATED --------------#
        try:
            with open(self.path + 'map.dat','rb+') as f:
                self.map = pickle.load(f)
        except:
            try:
                os.mkdir(self.path) # the end has a '/'
            except:
                pass
            with open(self.path +'map.dat', 'wb+') as f:
                pickle.dump(self.map,f)
        self.map[10][10] = 2

    def writeMap(self):
        with open(self.path + 'map.dat','wb+') as f:
            pickle.dump(self.map,f)


    #======================= DRAWING =======================#
    #=======================================================#
    
    def drawHud(self):
        bg1 = pygame.Surface((200, self.settings.height + 50))
        bg2 = pygame.Surface((self.settings.width + 200, 50))
        bg1.fill((70,70,70))
        bg2.fill((70,70,70))
        #pygame.draw.line(self.screen, '
        self.screen.blit(bg1,(0,0))
        self.screen.blit(bg2,(0,0))

    def drawMap(self):
        self.canvas.fill((0,0,0))
        self.limit()
        self.blit_coords_x = self.map_coords_x + self.cam[0]
        self.blit_coords_y = self.map_coords_y + self.cam[1]
        c = 0
        for y,py in zip(self.blit_coords_y,range(36)):
            c += 1
            i = c
            for x,px in zip(self.blit_coords_x,range(64)):
                i += 1
                if i % 2:
                    pygame.draw.rect(self.canvas, '#1c1c1c',(x,y,40,40))
                else:
                    pygame.draw.rect(self.canvas, '#101010',(x,y,40,40))
                self.blocks[py][px].rect.x = x
                self.blocks[py][px].rect.y = y
                
    def drawGridLines(self):
        if self.showGridLines:
            pygame.draw.line(self.canvas, '#87afaf', (self.blit_coords_x[32],0), (self.blit_coords_x[32] ,2600))
            pygame.draw.line(self.canvas, '#87afaf', (-40,self.blit_coords_y[18]), (2600,self.blit_coords_y[18]))

    def limit(self):
        if self.cam[0] > 40:
            self.cam[0] = 40
        if self.cam[0] < - 1320:
            self.cam[0] = - 1320
        if self.cam[1] > 40:
            self.cam[1] = 40
        if self.cam[1] < - 760:
            self.cam[1] = - 760

if __name__ == "__main__":
    editor = MapEditor()
    pygame.quit()
    #input("Press any key to continue!")
