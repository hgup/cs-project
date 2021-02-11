#----------------------- IMPORTS --------------------------#
import os
import sys
import pygame
import numpy
import pickle
import settings
from pygame.locals import *
import SpriteImages
SpriteImages = SpriteImages.SpriteImages(local = True)
import FontRenderer
# make a click and go level editor
    # mouse over a block when left click... creates a block
    # mouce over with right click ... deletes a block

#-------------------THE BASIC BLOCK------------------------#
fps = 90
class Block(pygame.sprite.Sprite):

    def __init__(self, pos, value, level):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.value = int(value)
        self.level = level
        SpriteImages.convert()
        self.sprites = SpriteImages.levelData
        self.image = self.sprites[self.value]
        #----------- UPDATING THE RECT ---------------------#
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos*40

    def update(self, s):
        self.image = pygame.transform.scale(self.sprites[self.value],(s,s))
        self.rect = self.image.get_rect()

class MenuBlock(pygame.sprite.Sprite):

    def __init__(self, pos, _id,level):
        super().__init__()
        self.value = _id
        self.sprites = SpriteImages.levelData
        self.image = pygame.Surface((50,70),SRCALPHA)
        self.image.blit(self.sprites[self.value], (5,0))
        self.image.set_colorkey("#000000")
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0] + 35 ,pos[1] - 20)
        self.selected = False
        self.current = 1

    def update(self,mx,my, editor):
        if self.rect.collidepoint(mx,my):
            self.image.set_alpha(170)
            if editor.leftClick:
                editor.selectedBlock = self.value
        else:
            self.image.set_alpha(100)

        if editor.selectedBlock == self.value:
            self.image.set_alpha(255)

def initDisplay():
        pygame.display.init()
        pygame.display.set_icon(pygame.image.load(r'OtherData/logo_round.png'))
        pygame.display.set_caption('[V E R T E X]')

class MapEditor:

    def __init__(self, game = None):
        #------------------ PYGAME STUFF -------------------#
        self.settings = settings.Settings()
        self.alpha = 255
        self.displaySize = self.settings.getDisplaySize()
        self.game = game
        if game is None:
            self.display = pygame.display.set_mode(self.displaySize,FULLSCREEN)
        else:
            self.fullscreen = game.fullscreen
            self.display = self.game.screen
        self.screen = pygame.Surface((self.settings.width + 200,self.settings.height + 50))
        self.canvas = pygame.Surface((self.settings.width,self.settings.height))
        self.fpsClock = pygame.time.Clock()
        pygame.mouse.set_visible(False)

        #------------------ MAP ID STUFF -------------------#
        self.level = self.startScreen() #1,2,3,4...
        if self.level is not None:
            self.path = r'./WorldData/Level ' +str(self.level)+ r'/'
            self.cam = pygame.math.Vector2(0,0)
            self.sprites = SpriteImages.levelData

            #------------------ Menu Blocks ----------------#
            self.menuBlocks = pygame.sprite.Group()
            self.addMenuBlocks()

            #----------------- RUNTIME LOGIC STUFF -------------#
            self.size = 40
            self.heading = FontRenderer.CenteredText("MAP EDITOR: (LEVEL %d)"%(self.level),
                    (self.settings.width//2 + 100,25))
            self.running = True
            self.scrolling = False
            self.leftClick = False
            self.rightClick = False
            self.showCursor = True
            self.cursor = pygame.image.load(r'./OtherData/cursor_normal.png').convert()
            self.cursor.set_colorkey("#000000")
            self.cursor = pygame.transform.scale(self.cursor,(self.size,self.size))
            self.selectedBlock = 1
            self.showGridLines = True
            self.updated = False
            self.loadMap()
            self.map_coords_x = numpy.arange(self.dimensions[0]) * self.size
            self.map_coords_y = numpy.arange(self.dimensions[1]) * self.size
            self.loadBlocks()
            self.mainloop()

    def blitAndFlip(self):
            self.display.fill("#101010")
            self.display.blit(pygame.transform.scale(self.screen,self.displaySize),(0,0))
            pygame.display.flip()

    #====================== MAIN ========================#
    #====================================================#
    def mainloop(self):
        while True:
            #-------------- EVENTS AND UPDATES -------------#
            self.events()
            if not self.running:
                break
            self.update()
            #-------------------- DRAWING ------------------#
            self.screen.fill((0,0,0))
            self.drawMap()
            self.drawHud()
            self.blockGroup.draw(self.canvas)
            self.drawGridLines()
            self.screen.blit(self.canvas, (200,50))
            self.drawCursor()
            self.display.blit(pygame.transform.scale(self.screen,self.displaySize),(0,0))
            #------------------ UPDATE AND TICK ------------#
            pygame.display.update()
            self.fpsClock.tick(90)

    def events(self):
        self.g = 0
        for event in pygame.event.get():
            #---------------- KEYBOARD EVENTS --------------#
            if event.type == QUIT:
                self.running = False
                if self.updated:
                    self.confirm('Do you want to Save?')
            if event.type == KEYUP:
                if event.key == K_g:
                    self.showGridLines = not self.showGridLines
                if event.key == K_F1:
                    self.confirm('Do you want to Save?')
                if event.key == K_ESCAPE:
                    self.running = False
                    if self.updated:
                        self.confirm('Do you want to Save?')
                    else:
                        self.confirm("Do you want to quit?",no_e = False)
                if event.key == K_F11:
                    if self.game is not None:
                        pygame.display.toggle_fullscreen()
                        self.display = self.game.screen
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
            if event.type == MOUSEWHEEL:
                if event.y < 0: # mouse down
                    mx,my = pygame.mouse.get_pos()
                    self.map_coords_x = numpy.arange(self.dimensions[0]) * self.size
                    self.map_coords_y = numpy.arange(self.dimensions[1]) * self.size
                    self.size -= 2
                    if self.size < 20:
                        self.size = 20
                    else:
                        self.cam.x += self.dimensions[0]
                        self.cam.y += self.dimensions[1]
                elif event.y > 0: # mouse up
                    mx,my = pygame.mouse.get_pos()
                    self.size += 2
                    if self.size > 40:
                        self.size = 40
                    else:
                        self.cam.x -= self.dimensions[0]
                        self.cam.y -= self.dimensions[1]
                self.map_coords_x = numpy.arange(self.dimensions[0]) * self.size
                self.map_coords_y = numpy.arange(self.dimensions[1]) * self.size

    def update(self):
        if self.scrolling:
            m = pygame.mouse.get_rel()
            self.cam += m
        mx,my = pygame.mouse.get_pos()
        #---------------- CHECK ON CLICK -------------------#
        for block in self.blockGroup.sprites():
            if block.rect.collidepoint(mx-200,my-50):
                x,y = block.pos
                if self.rightClick:
                    self.updated = True
                    block.value = 0
                    self.map[int(y)][int(x)] = 0
                if self.leftClick:
                    self.updated = True
                    block.value = self.selectedBlock
                    self.map[int(y)][int(x)] = self.selectedBlock
        self.blockGroup.update(self.size)
        self.menuBlocks.update(mx,my,self)
    #=================== OBJECT HANDLING ===================#
    #=======================================================#

    def loadBlocks(self):
        #-------------- CREATING Block OBJECTS -------------#
        self.blocks = []
        self.blockGroup = pygame.sprite.Group()
        for y in range(self.dimensions[1]):
            self.blocks.append([])
            for x in range(self.dimensions[0]):
                k = Block((x,y),self.map[y][x],self.level)
                self.blocks[y].append(k)
                self.blockGroup.add(k)

    def addMenuBlocks(self):
        L = len(SpriteImages.levelData)
        p = 20
        c = 0
        for i in range(L):
            if i % 2 == 1:
                c += 1
            pos = (abs((i % 2)-1) * (50 + p), c * (70 + p))
            self.menuBlocks.add(MenuBlock(pos,i,self.level))

    #==================== FILE HANDLING ====================#
    #=======================================================#
    def loadMap(self):
        # --------------- self.map IS CREATED --------------#
        try:
            with open(self.path + 'map.dat','rb+') as f:
                self.chunks = pickle.load(f)
                self.map = pickle.load(f)
                self.dimensions = (32*self.chunks[0],18*self.chunks[1])
        except:
            self.chunks = self.getDimensions()
            self.dimensions = (32*self.chunks[0],18*self.chunks[1])
            self.map = numpy.zeros((self.dimensions[1],self.dimensions[0]))
            try:
                os.mkdir(self.path) # the end has a '/'
            except:
                pass
            with open(self.path +'map.dat', 'wb+') as f:
                pickle.dump(self.chunks,f)
                pickle.dump(self.map,f)

    def writeMap(self):
        with open(self.path + 'map.dat','wb+') as f:
            pickle.dump(self.chunks,f)
            pickle.dump(self.map,f)
        print('saved')
        self.updated = False


    #======================= DRAWING =======================#
    #=======================================================#
    def drawCursor(self):
        if self.showCursor:
            self.screen.blit(self.cursor,pygame.mouse.get_pos())

    def drawHud(self):
        bg1 = pygame.Surface((200, self.settings.height + 50)) # top to bottom
        bg2 = pygame.Surface((self.settings.width + 200, 50)) # left to right
        bg1.fill("#222831")
        bg2.fill("#333456")
        self.screen.blit(bg2,(0,0))
        self.screen.blit(bg1,(0,0))
        self.heading.draw(self.screen)
        self.menuBlocks.draw(self.screen)
        pygame.draw.line(self.screen,(255,255,255),(200,50),(600,250))

    def drawMap(self):
        self.canvas.fill("#101010")
        self.limit()
        self.blit_coords_x = self.map_coords_x + self.cam[0]
        self.blit_coords_y = self.map_coords_y + self.cam[1]
        c = 0
        for y,py in zip(self.blit_coords_y,range(self.dimensions[1])):
            c += 1
            i = c
            for x,px in zip(self.blit_coords_x,range(self.dimensions[0])):
                i += 1
                if i % 2:
                    pygame.draw.rect(self.canvas, '#1c1c1c',(x,y,self.size,self.size))
                else:
                    pygame.draw.rect(self.canvas, '#101010',(x,y,self.size,self.size))
                self.blocks[py][px].rect.x = x
                self.blocks[py][px].rect.y = y

    def drawGridLines(self):
        if self.showGridLines:
            for x in range(1,self.dimensions[0]//32):
                pygame.draw.line(self.canvas, '#87afaf',
                        (self.blit_coords_x[32*x],0), (self.blit_coords_x[32*x] ,2600))
            for y in range(1,self.dimensions[1]//16):
                pygame.draw.line(self.canvas, '#87afaf',
                        (-40,self.blit_coords_y[18*y]), (2600,self.blit_coords_y[18*y]))

    def limit(self):
        if self.cam[0] > 40:
            self.cam[0] = 40
        if self.cam[1] > 40:
            self.cam[1] = 40

    #===================== OTHER SCREENS ====================#
    #========================================================#
    def fadeIn(self,color ="#101010",screen = None):
        if screen is None:
            screen = self.display.copy()
        fadePad = pygame.Surface(self.displaySize)
        fadePad.fill(color)
        alpha = 40
        while True:
            alpha += 8
            if alpha > 255:
                break
            fadePad.set_alpha(alpha)
            self.display.blit(screen,(0,0))
            self.display.blit(fadePad,(0,0))
            pygame.display.flip()
            self.fpsClock.tick(fps)
        self.display.fill(color)
        pygame.display.flip()
        pygame.time.delay(50)

    def getDimensions(self):
        bg = pygame.transform.scale(pygame.image.load("./OtherData/map_editor.png"),self.display.get_size())
        ques = FontRenderer.CenteredText('No mapData found, Enter Dimensions! (1,4)',(640,300),textSize = 30,color='#101010')
        x,y = '2','2'
        Bx = FontRenderer.Button(' ',(600,500),color = (85,85,85))
        By = FontRenderer.Button(' ',(700,500))
        running = True
        is_x = True
        c = '2'
        while running:
            self.display.blit(bg,(0,0))
            Bx.renderFonts(x)
            By.renderFonts(y)
            Bx.draw(self.display)
            By.draw(self.display)
            ques.draw(self.display)
            pygame.display.update()
            self.fpsClock.tick(fps)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.unicode.isnumeric() and int(event.unicode) in range(1,5):
                            c = event.unicode
                if is_x:
                    x = c
                else:
                    y = c
                if event.type == KEYUP:
                    if event.key == K_TAB:
                        is_x = not is_x
                        if is_x:
                            c = x
                            Bx.color = (85,85,85)
                            By.color = (0,0,0)
                        else:
                            c = y
                            By.color = (85,85,85)
                            Bx.color = (0,0,0)
                    if event.key == K_F11:
                        pygame.display.toggle_fullscreen()
                    if event.key == K_RETURN:
                        return int(x),int(y)

    def startScreen(self):
        bg = pygame.transform.scale(pygame.image.load("./OtherData/map_editor.png"),self.display.get_size())
        ques = FontRenderer.CenteredText('Map to Edit?',(640,300),textSize = 30,color='#101010')
        warningNum = FontRenderer.CenteredText('*Level should be numeric',(640,500),color='#303030')
        IN = FontRenderer.Button('   ',(640,400))
        level = ''
        running = True
        while running:
            self.display.blit(bg,(0,0))
            IN.renderFonts(level)
            IN.draw(self.display)
            ques.draw(self.display)
            if not level.isnumeric():
                warningNum.draw(self.display)
            pygame.display.update()
            self.fpsClock.tick(fps)

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        level = level[:-1]
                    else:
                        if event.unicode.isnumeric():
                            if len(level) < 3:
                                level += event.unicode
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        self.fadeIn("#ffffff")
                        running = not running
                        break
                    if event.key == K_F11:
                        pygame.display.toggle_fullscreen()
                    if event.key == K_RETURN:
                        if level:
                            val = int(level)
                            if val in [1,2,3]:
                                self.fadeIn()
                                return val
                            else:
                                self.fadeIn("#ffffff")
                                self.sorry('Sorry, that level is not Available.')
                        else:
                            self.sorry("Don't leave it blank")


    def sorry(self,text):
        messege = FontRenderer.CenteredText(text,(640,300))
        running = True
        while running:
            self.display.fill('#101010')
            messege.draw(self.display)
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == K_RETURN or event.key == K_ESCAPE:
                        self.fadeIn("#ffffff")
                        return
            pygame.display.flip()
            self.fpsClock.tick(fps)


    def confirm(self,text, no_e = True):
        self.fadeIn('#ffffff')
        bg = pygame.transform.scale(pygame.image.load("./OtherData/map_editor.png"),self.display.get_size())
        qes = FontRenderer.CenteredText(text,(640,300),color = "#101010",textSize=40)
        yes = FontRenderer.RButton('yes',(640,400),color = (24,88,24))
        no = FontRenderer.RButton('no',(640,460),color = (88,24,24))
        cancel = FontRenderer.RButton('cancel',(640,520))
        running = True
        click = False
        while running:
            self.display.blit(bg,(0,0))
            qes.draw(self.display)
            yes.draw(self.display)
            if no_e:
                no.draw(self.display)
            cancel.draw(self.display)
            self.display.blit(self.cursor,pygame.mouse.get_pos())
            self.drawCursor()
            pygame.display.flip()
            self.fpsClock.tick(fps)
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        self.fadeIn()
                        self.running = True
                        running = False
                    if event.key == K_F11:
                        pygame.display.toggle_fullscreen()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        click = False
            mx,my = pygame.mouse.get_pos()
            if yes.hover(mx,my) and click:
                self.fadeIn('#ffffff')
                self.writeMap()
                break
            if no_e:
                if no.hover(mx,my) and click:
                        self.fadeIn("#ffffff")
                        break
            if cancel.hover(mx,my) and click:
                    self.fadeIn()
                    self.running = True
                    break

if __name__ == "__main__":
    editor = MapEditor()
    pygame.quit()
    sys.exit()
    #input("Press any key to continue!")
