#----------------------- IMPORTS --------------------------#
import os
import pygame
import numpy
import pickle
import settings
from pygame.locals import *
import SpriteImages
import FontRenderer
# make a click and go level editor
    # mouse over a block when left click... creates a block
    # mouce over with right click ... deletes a block

#-------------------THE BASIC BLOCK------------------------#

class Block(pygame.sprite.Sprite):

    def __init__(self, pos, value, level):
        super().__init__()
        self.pos = pos
        self.value = int(value)
        self.sprites = SpriteImages.levels[level]
        self.image = self.sprites[self.value]
        #----------- UPDATING THE RECT ---------------------#
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.sprites[self.value]

class MapEditor:
    def __init__(self):
        #------------------ MAP ID STUFF -------------------#
        self.level = int(input("Enter map number:")) #1,2,3,4...
        self.path = r'./WorldData/Level ' +str(self.level)+ r'/'
        self.map = numpy.zeros((36,64))
        self.map_coords_x = numpy.arange(64) * 40
        self.map_coords_y = numpy.arange(36) * 43
        self.cam = pygame.math.Vector2(0,0)
        self.sprites = SpriteImages.levels[self.level]
        #------------------ PYGAME STUFF -------------------#
        self.settings = settings.Settings()        
        self.display = pygame.display.set_mode((1600,900),FULLSCREEN)
        self.screen = pygame.Surface((self.settings.width + 200,self.settings.height + 50))
        self.canvas = pygame.Surface((self.settings.width,self.settings.height))
        self.fpsClock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        #----------------- RUNTIME LOGIC STUFF -------------#
        self.heading = FontRenderer.CenteredText("MAP EDITOR: (LEVEL %d)"%(self.level),(self.settings.width//2 + 100,25))
        self.running = True
        self.scrolling = False
        self.leftClick = False
        self.rightClick = False
        self.showCursor = True
        self.cursor = pygame.image.load(r'./OtherData/cursor.png').convert()
        self.cursor.set_colorkey('#000000')
        self.selectedBlock = 1
        self.showGridLines = True
        self.updated = False
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
            self.drawCursor()
            self.display.blit(pygame.transform.scale(self.screen,pygame.display.get_surface().get_size()),(0,0))
            #------------------ UPDATE AND TICK ------------#
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)

    def events(self):
        for event in pygame.event.get():
            #---------------- KEYBOARD EVENTS --------------#
            if event.type == QUIT:
                self.running = False
                if self.updated:
                    self.confirm()
            if event.type == KEYUP:
                if event.key == K_g:
                    self.showGridLines = not self.showGridLines
                if event.key == K_F1:
                    self.confirm()
                if event.key == K_ESCAPE:
                    self.running = False
                    if self.updated:
                        self.confirm()
            if event.type == KEYDOWN:
                if event.key == K_1:
                    self.selectedBlock = 1
                if event.key == K_2:
                    self.selectedBlock = 2
                if event.key == K_3:
                    self.selectedBlock = 3
                if event.key == K_4:
                    self.selectedBlock = 4
                if event.key == K_5:
                    self.selectedBlock = 5
            #------------------- MOUSE EVENTS --------------#
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.leftClick = True
                if event.button == 2:
                    self.scrolling = True
                    self.showCursor = False
                    pygame.mouse.get_rel()
                if event.button == 3:
                    self.rightClick = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.leftClick = False
                if event.button == 2:
                    self.scrolling = False
                    self.showCursor = True
                if event.button == 3:
                    self.rightClick = False

    def update(self):
        if self.scrolling:
            self.cam += pygame.mouse.get_rel()
        mx,my = pygame.mouse.get_pos()
        #---------------- CHECK ON CLICK -------------------#
        for block in self.blockGroup.sprites():
            if block.rect.collidepoint(mx-200,my-50):
                x,y = block.pos
                if self.rightClick:
                    self.updated = True
                    block.value = 0
                    self.map[y][x] = 0
                if self.leftClick:
                    self.updated = True
                    block.value = self.selectedBlock
                    self.map[y][x] = self.selectedBlock
        self.blockGroup.update()

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

    def writeMap(self):
        with open(self.path + 'map.dat','wb+') as f:
            pickle.dump(self.map,f)
        print('saved')
        self.updated = False


    #======================= DRAWING =======================#
    #=======================================================#
    def drawCursor(self):
        if self.showCursor:
            self.screen.blit(self.cursor,pygame.mouse.get_pos())

    def drawHud(self):
        bg1 = pygame.Surface((200, self.settings.height + 50))
        bg2 = pygame.Surface((self.settings.width + 200, 50))
        bg1.fill((70,70,70))
        bg2.fill((40,40,40))
        #pygame.draw.line(self.screen, '
        self.screen.blit(bg1,(0,0))
        self.screen.blit(bg2,(0,0))
        self.heading.draw(self.screen)

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

    def confirm(self):
        qes = FontRenderer.CenteredText('Do you want to Save?',(500,300))
        yes = FontRenderer.Button('yes',(660,400),color = "#185818")
        no = FontRenderer.Button('no',(660,440),color = "#581818")
        cancel = FontRenderer.Button('cancel',(660,480))
        running = True
        click = False
        while running:
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        self.running = True
                        running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        click = False
            mx,my = pygame.mouse.get_pos()
            if yes.hover(mx,my) and click:
                self.writeMap()
                break
            if no.hover(mx,my) and click:
                    break
            if cancel.hover(mx,my) and click:
                    self.running = True
                    break
            self.screen.fill("#101010")
            qes.draw(self.screen)
            yes.draw(self.screen)
            no.draw(self.screen)
            cancel.draw(self.screen)
            self.drawCursor()
            self.display.blit(pygame.transform.scale(self.screen,pygame.display.get_surface().get_size()),(0,0))
            pygame.display.update()
if __name__ == "__main__":
    editor = MapEditor()
    pygame.quit()
    #input("Press any key to continue!")
