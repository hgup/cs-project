#imports game modules
from network import Network
import sys
import os
import pygame
import pickle
import numpy
import random
import time
from pygame.locals import *
import _thread
# import my modules
import sprites
from settings import *
import mapLoader
import mapEditor
import FontRenderer
from network import Network
import server as server
#from gameMenu import Menu


class MenuBlocks(pygame.sprite.Sprite):
    def __init__(self,img,pos,val):
        super().__init__()
        self.image = pygame.image.load(r'./OtherData/' + img).convert()
        self.image.set_colorkey("#000000")
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.value = val

def initDisplay():
        pygame.display.init()
        pygame.display.set_icon(pygame.image.load(r'OtherData/logo_round.png'))
        pygame.display.set_caption('[V E R T E X]')

class Game:
    def __init__(self):
        #---------------- PYGAME STUFF ------------------#
        self.settings = Settings()
        self.address = self.settings.lastAddress
        self.port = self.settings.lastPort
        self.name = self.settings.lastName
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.displaySize = self.settings.getDisplaySize()
        initDisplay()
        #self.screen = pygame.Surface((self.settings.width,self.settings.height))
        self.screen = pygame.display.set_mode((self.settings.width,self.settings.height))
        self.fullscreen = False
        self.fpsClock = pygame.time.Clock()
        self.homeScreen()

    def newGame(self):
        self.running = False
        while True:
            if self.hosting:
                if self.hostGame(): # sets self.address and self.port
                    self.peers = int(self.peers)
                    self.level = int(self.level)
                    self.port = int(self.port)
                    self.address = 'localhost'
                    self.myServer = server.Server(self.peers,self.port,self.level)
                    self.running = True
                else:
                    break
            else:
                self.running = self.joinGame()
            #--------- SPRITE OVER NETWORK STUFF ------------#
            if not self.running:
                break
            self.playerGroup = pygame.sprite.Group()
            self.screen.blit(pygame.image.load('./OtherData/joining_game.png'),(0,0))
            pygame.display.update()
            self.net = Network(self.address,self.port)
            try:
                pass
            except Exception as err:
                print('self.net error')
                self.sorry(f'An error Occured while connecting',f'Error: {err}',size=30)
                continue
            self.peers = self.net.peers
            #try:
            #except:
            #    self.sorry('GAME IS FULL!','Please Wait', size = 30)
            #    continue
            self.vertex = [[(50,50),0],[(100,100),0],[(150,150),0]][:self.peers]
            self.addAllPlayers()
            self.redundantAngel = sprites.Angel(-1,(-500,-500),0)
            #---------------- MAP INIT STUFF ----------------#
            self.map = self.net.map 
            self.chunks = self.map.chunks
            self.chunkDimension = (40*32,40*18)
            self.dimensions = (self.chunks[0]*32,self.chunks[1]*18)
            self.bg = self.map.bg
            self.setCamFocus(self.player)
            #---------------- GAME RUNTIME STUFF ------------#
            self.down_pressed = False
            self.paused = False
            self.threads = True
            self.cam = pygame.math.Vector2(1.0,0.0)
            self.LB_x = self.LB_y = 0 - data['bounds']
            self.UB_x = data['bounds'] + data['width']//2 * (self.chunks[0] + 1)
            self.UB_y = data['bounds'] + data['height']//2 * self.chunks[1] 
            self.focus = [(self.settings.width - self.player.rect.width) // 2,
                    (self.settings.height - self.player.rect.height) // 2]
            self.downFocus = self.focus[0],self.focus[1] -200,
            self.bottomFocus = self.focus[0],self.focus[1] + 200,
            self.leftFocus = self.focus[0],self.focus[1],
            self.rightFocus = self.focus[0],self.focus[1],
            self.correction = [0,0] # bottom [0,200] top[0,-200]
            self.mainloop()
            self.net.client.close()
            self.player.kill()
            break

    def addAllPlayers(self):
        # initialize all locations
        font = pygame.font.Font('./FontData/8-bit-pusab.ttf',12)
        for _id in range(self.peers):
            a = sprites.Angel(_id,self.net.initRect,_id)
            self.playerGroup.add(a)
            if self.net.id == _id: # link this game session and player
                self.player = a
        self.nameSurf = font.render(self.name,True,'#f0f0f0')

    def mainloop(self):
        # threaded processes
        while True:
            # handle, update and draw
            events = pygame.event.get()
            pressed = self.handleGameEvents(events)
            if pressed == K_ESCAPE:
                self.paused = True
                self.pause(events)
                self.paused = False
                self.setCamFocus(self.player)
            if not self.running:
                break
            self.handlePlayerEvents(self.player,events)
            self.update()
            self.draw()
            # flip and tick
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)
        self.threads = False


    def setCamFocus(self,entity,axes='both'):
        if axes == 'both':
            self.focusedPlayerX = self.focusedPlayerY = entity
        elif axes == 'x' or axes == 'X':
            self.focusedPlayerX = entity
        elif axes == 'y' or axes == 'Y':
            self.focusedPlayerY = entity

    def camUpdates(self):
        self.correction = [0,0]
        if not self.paused:
            if (self.player.rect.x // 40) < 8:
                self.correction[0] = 330
            elif (self.player.rect.x // 40) > self.chunks[0]*32 - 8:
                self.correction[0] = -300
            if (self.player.rect.y // 40) > self.chunks[1]*18 - 12:
                self.correction[1] = -100
        if self.down_pressed:
            dy = (self.focusedPlayerY.rect.y - self.cam[1] - self.downFocus[1] + self.correction[1])
        else:
            dy = (self.focusedPlayerY.rect.y - self.cam[1] - self.focus[1] + self.correction[1])
        dx = (self.focusedPlayerX.rect.x - self.cam[0] - self.focus[0] + self.correction[0])
        self.cam[0] += dx/20
        self.cam[1] += dy/20
        self.cam[0] = int(self.cam[0])
        self.cam[1] = int(self.cam[1])

    def update(self):
        #---------------- player updates ------------#
        self.move(self.map.group)
        self.camUpdates()
        self.map.group.update()
        self.player.update()
        self.updateAllPlayers()
        #---------------- MAP UPDATES ---------------#
        if self.player.rect.y >= self.settings.height * self.chunks[1]:
            self.player.rect.topleft = random.choice([(0,0),(1000,0),(1700,0)])
            self.player.physics.vel = pygame.math.Vector2(0.0,0.0)

    def updateAllPlayers(self):
        # this is just to test
        try:
            self.vertex = pickle.loads(self.net.send(
                pickle.dumps([self.net.id,(self.player.rect.x,self.player.rect.y)])
                ))
        except:
            self.net.client.close()
            self.running = False
        for player,vert in zip(self.playerGroup.sprites(),self.vertex):
            player.rect.x, player.rect.y = vert[0]


    def blitAndFlip(self):
        self.display.fill("#101010")
        self.display.blit(pygame.transform.scale(self.screen,self.displaySize),(0,0))
        pygame.display.flip()

    def drawAllPlayers(self):
        for player in self.playerGroup.sprites():
            if self.vertex[player.id][1]:
                self.screen.blit(player.image,
                        (player.rect.x - self.cam[0], player.rect.y - self.cam[1]))
        self.screen.blit(self.nameSurf,
                (player.rect.x - self.cam[0] - len(self.name)*4, player.rect.y - self.cam[1] - 25))


    def draw(self):
        # fill with black
        self.screen.blit(self.bg,(0,0))
        # draw environment
        self.map.draw(self.screen, self.cam)
        # draw players
        self.drawAllPlayers()
        #self.screen.blit(self.player.image,self.player.rect)
    
    def pause(self,events):
        self.setCamFocus(self.redundantAngel)
        resume = pygame.image.load('./OtherData/resume.png').convert()
        resume.set_colorkey((0,0,0))
        exit = pygame.image.load('./OtherData/exit.png').convert()
        exit.set_colorkey((0,0,0))
        button_selected = pygame.image.load('./OtherData/select.png').convert()
        button_selected.set_colorkey((0,0,0))
        resumeCoords = FontRenderer.centerCoords(resume,(340,380))
        exitCoords = FontRenderer.centerCoords(exit,(340,520))
        bg = pygame.Surface((self.settings.width,self.settings.height)).convert()
        bg.fill((30,30,30))
        bg.set_alpha(150)
        self.player.physics.acc = pygame.math.Vector2(0,0)
        selected = 0
        options = 2
        paused = True
        while paused:
            events = pygame.event.get()
            pressed = self.handleGameEvents(events)
            if pressed == K_ESCAPE:
                break
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_DOWN:
                        if selected != options -1:
                            selected += 1
                    elif event.key == K_UP:
                        if selected != 0:
                            selected -= 1
                elif event.type == KEYUP:
                    if event.key == K_RETURN:
                        if selected == 0:
                            paused = False
                        if selected == 1:
                            self.running = False
                            paused = False

            self.update()
            self.draw()
            self.screen.blit(bg,(0,0))
            self.screen.blit(resume,resumeCoords)
            self.screen.blit(exit,exitCoords)
            if selected == 0:
                self.screen.blit(button_selected,resumeCoords)
            elif selected == 1:
                self.screen.blit(button_selected,exitCoords)

            # flip and tick
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)

    def handleGameEvents(self,events):
        for event in events:
            if event.type == QUIT:
                self.running = False
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    self.fullscreen = not self.fullscreen
                    pygame.display.toggle_fullscreen()
            if event.type == KEYUP:
                if event.key == K_RETURN: return K_RETURN
                if event.key == K_ESCAPE: return K_ESCAPE

    def handlePlayerEvents(self,player,events):
        for event in events:
            if event.type == KEYDOWN:
                    player.start_move(event)
                    if event.key == K_DOWN:
                        self.down_pressed = True
                        player.dash()
                    if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                        player.jumping = True
            if event.type == KEYUP:
                    player.stop_move(event)
                    if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                        player.jumping = False
                    if event.key == K_DOWN: self.down_pressed = False
                    if event.key == K_RETURN: return K_RETURN

    def collisionDetect(self,entity,group):
        for entity2 in group.sprites():
            if entity2.value:
                if entity.rect.colliderect(entity2.rect):
                    return entity2

    # group is that of platforms with which the player interacts
    def move(self,group):
        self.player.colliding = {'top':False,'bottom':False,'left':False,'right':False}
        self.player.move_x()
        s = self.collisionDetect(self.player,group)
        if s:
            if self.player.physics.vel.x > 0:
                self.player.colliding['right'] = True
                self.player.rect.right = s.rect.left
            elif self.player.physics.vel.x < 0:
                self.player.colliding['left'] = True
                self.player.rect.left = s.rect.right
        self.player.move_y()
        s = self.collisionDetect(self.player,group)
        if s:
            if self.player.physics.vel.y > 0:
                self.player.colliding['bottom'] = True
                self.player.rect.bottom = s.rect.top
            elif self.player.physics.vel.y < 0:
                self.player.colliding['top'] = True
                self.player.rect.top = s.rect.bottom
        return s #the entity that collided last

    def editor(self):
        editor = mapEditor.MapEditor(self)
        self.homeScreen()

    def homeScreen(self):
        self.home = True
        bg = pygame.image.load('./OtherData/home.png').convert()
        selected = 9
        homeSprites = []
        self.homeGroup = pygame.sprite.Group()
        self.player = sprites.Angel(0,[633,100],3)
        for i in [('options.png',(55,533),1),('play.png',(480,513),2),
                ('exit.png',(889,533),3),('T.png',(632,154),9)]:
            x = MenuBlocks(i[0],i[1],i[2])
            self.homeGroup.add(x)
            homeSprites.append(x)

        def changeSelected(x,selected):
            for homeButton in self.homeGroup:
                if homeButton is x:
                    selected = homeButton.value
                if selected == homeButton.value:
                    homeButton.image.set_alpha(255)
                else:
                    homeButton.image.set_alpha(180)
            return selected
        selected = 4
        actions = [None,self.editor,self.gameSelect]

        done = True
        doneSelected = False
        while self.home:
            events = pygame.event.get()
            s = self.move(self.homeGroup)
            if not doneSelected:
                self.handlePlayerEvents(self.player,events)
                if self.player.rect.y  > 800: self.player.rect.topleft = (633,100)
            else:
                if done:
                    homeSprites[selected - 1].kill()
                    done = False
                if self.player.rect.y > 800:
                    self.home = False
            pressed = self.handleGameEvents(events)
            selected = changeSelected(s, selected)
            if pressed == K_RETURN:
                if selected in (1,3): break
                if selected == 2: doneSelected = True
            self.player.update()
            self.screen.blit(bg,(0,0))
            self.screen.blit(self.player.image,self.player.rect.topleft)
            self.homeGroup.draw(self.screen)
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)

        if selected != 3:
            actions[selected]()
        self.player.kill()

    def gameSelect(self):
        while True:
            bg = pygame.image.load('./OtherData/map_editor.png').convert()
            selected = 9
            homeSprites = []
            self.gameGroup = pygame.sprite.Group()
            self.player.rect.top = -100
            for i in [('join_game.png',(100,533),1),('host_game.png',(800,533),2),
                    ('T.png',(632,154),4)]:
                x = MenuBlocks(i[0],i[1],i[2])
                self.gameGroup.add(x)
                homeSprites.append(x)

            def changeSelected(x,selected):
                for homeButton in self.gameGroup:
                    if homeButton is x:
                        selected = homeButton.value
                    if selected == homeButton.value:
                        homeButton.image.set_alpha(255)
                    else:
                        homeButton.image.set_alpha(180)
                return selected
            selected = 4

            gameTime = True
            done = True
            doneSelected = False
            while gameTime:
                events = pygame.event.get()
                s = self.move(self.gameGroup)
                if not doneSelected:
                    self.handlePlayerEvents(self.player,events)
                    if self.player.rect.y  > 800: self.player.rect.topleft = (633,100)
                else:
                    if done:
                        homeSprites[selected - 1].kill()
                        done = False
                    if self.player.rect.y > 800:
                        gameTime = False
                pressed = self.handleGameEvents(events)
                selected = changeSelected(s, selected)
                if pressed == K_RETURN:
                    if selected in (1,2): doneSelected = True
                if pressed == K_ESCAPE:
                    selected = 3
                    break
                self.player.update()
                self.screen.blit(bg,(0,0))
                self.screen.blit(self.player.image,self.player.rect.topleft)
                self.gameGroup.draw(self.screen)
                pygame.display.update()
                self.fpsClock.tick(self.settings.fps)

            if selected == 1:
                self.hosting = False
                self.newGame()
                self.player = sprites.Angel(3,(640,-100),3)
                continue
            elif selected == 2:
                self.hosting = True
                self.newGame()
                self.player = sprites.Angel(3,(640,-100),3)
                continue
            break
        self.homeScreen()
        self.player.kill()

    def hostGame(self):
        self.peers = '1'
        self.level = '1'
        selected = 9
        joinSprites = []
        joinGroup = pygame.sprite.Group()
        self.player.rect.topleft = (80,-10)
        for i in [('desk.png',(77,600),1)]:#,('join.png',(700,500),2)]:
            x = MenuBlocks(i[0],i[1],i[2])
            joinGroup.add(x)
            joinSprites.append(x)

        NAME = FontRenderer.Button('               ',(232,216),color=None,key = '#38b6ff',textSize = 30)
        PEER = FontRenderer.Button('               ',(505,211),color=None,key = '#38b6ff',textSize = 30)
        MAP = FontRenderer.Button('               ',(407,406), color=None, key = '#38b6ff',textSize = 30)
        PORT = FontRenderer.Button('               ',(640,394), color=None, key = '#38b6ff',textSize = 30)
        bg_image = pygame.image.load(r'./OtherData/Host_screen.png').convert()
        NAMEselected = pygame.Surface((5,257 - 175)) #84,175 -> 257
        NAMEselected.fill('#ffffff')
        PEERselected = pygame.Surface((5,250 - 169)) #407,169 -> 250
        PEERselected.fill('#ffffff')
        MAPselected = pygame.Surface((5,449 - 367)) #309,367 -> 449
        MAPselected.fill('#ffffff')
        PORTselected = pygame.Surface((5,423 - 362)) #548,362 -> 423
        PORTselected.fill('#ffffff')
        add = 1

        while True:
            if self.player.rect.y  > 800: self.player.rect.topleft = (80,-10)
            events = pygame.event.get()
            s = self.move(joinGroup)
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        if add == 0: self.name = self.address[:-1]
                        elif add == 1: self.peers = self.peers[:-1]
                        elif add == 2: self.level = self.level[:-1]
                        else: self.port = self.port[:-1]
                    else:
                        if event.key != K_RETURN and event.key != K_ESCAPE and event.key != K_TAB:
                            if add == 0: self.name += event.unicode
                            elif add == 1: self.peers += event.unicode
                            elif add == 2: self.level += event.unicode
                            else: self.port += event.unicode

                    if event.key == K_LSHIFT and event.key == K_TAB:
                        add -= 1
                        if add == -1: add = 3
                    elif event.key == K_TAB:
                        add = (add + 1) % 4
                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        return True
            self.handlePlayerEvents(self.player,events)
            pressed = self.handleGameEvents(events)
            if pressed == K_ESCAPE:
                self.running = False
                return False
            self.player.update()
            self.screen.blit(bg_image,(0,0))
            if add == 0:
                self.screen.blit(NAMEselected,(84,175))
            elif add == 1:
                self.screen.blit(PEERselected,(407,169))
            elif add == 2:
                self.screen.blit(MAPselected,(309,367))
            elif add == 3:
                self.screen.blit(NAMEselected,(548,362))
            NAME.renderFonts(self.name)
            NAME.draw(self.screen)
            PORT.renderFonts(self.port)
            PORT.draw(self.screen)
            PEER.renderFonts(self.peers)
            PEER.draw(self.screen)
            PORT.renderFonts(self.port)
            PORT.draw(self.screen)
            MAP.renderFonts(self.level)
            MAP.draw(self.screen)
            joinGroup.draw(self.screen)
            self.screen.blit(self.player.image,self.player.rect.topleft)
            self.fpsClock.tick(self.settings.fps)
            pygame.display.flip()


    def joinGame(self):

        selected = 9
        joinSprites = []
        joinGroup = pygame.sprite.Group()
        self.player.rect.topleft = (80,-10)
        for i in [('desk.png',(77,600),1)]:#,('join.png',(700,500),2)]:
            x = MenuBlocks(i[0],i[1],i[2])
            joinGroup.add(x)
            joinSprites.append(x)
        ADD = FontRenderer.Button('               ',(703,264),color=None,key = '#38b6ff',textSize = 30)
        PORT = FontRenderer.Button('               ',(1030,264),color=None,key = '#38b6ff',textSize = 30)
        NAME = FontRenderer.Button('               ',(873,424), color=None, key = '#38b6ff',textSize = 30)
        bg_image = pygame.image.load(r'./OtherData/Join_Screen.png').convert()
        ADDselected = pygame.Surface((5,80)) #483,224
        ADDselected.fill('#ffffff')
        PORTselected = pygame.Surface((5,60)) #938,234
        PORTselected.fill('#ffffff')
        NAMEselected = pygame.Surface((5,65)) #704,388
        NAMEselected.fill('#ffffff')
        add = 1

        while True:
            if self.player.rect.y  > 800: self.player.rect.topleft = (80,-10)
            events = pygame.event.get()
            s = self.move(joinGroup)
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        if add == 0: self.address = self.address[:-1]
                        elif add == 1: self.port = self.port[:-1]
                        else: self.name = self.name[:-1]
                    else:
                        if event.key != K_RETURN and event.key != K_ESCAPE and event.key != K_TAB:
                            if add == 0: self.address += event.unicode
                            elif add == 1: self.port += event.unicode
                            else: self.name += event.unicode
                    if event.key == K_TAB:
                        add = (add + 1) % 3
                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        return True
            self.handlePlayerEvents(self.player,events)
            pressed = self.handleGameEvents(events)
            if pressed == K_ESCAPE:
                return False
            self.player.update()
            self.screen.blit(bg_image,(0,0))
            if add == 0:
                self.screen.blit(ADDselected,(483,224))
            elif add == 1:
                self.screen.blit(PORTselected,(938,234))
            elif add == 2:
                self.screen.blit(NAMEselected,(701,388))
            ADD.renderFonts(self.address)
            ADD.draw(self.screen)
            PORT.renderFonts(self.port)
            PORT.draw(self.screen)
            NAME.renderFonts(self.name)
            NAME.draw(self.screen)
            joinGroup.draw(self.screen)
            self.screen.blit(self.player.image,self.player.rect.topleft)
            self.fpsClock.tick(self.settings.fps)
            pygame.display.flip()

    def sorry(self,text,text2 = '',size= 25):
        self.screen.fill('#101010')
        messege = FontRenderer.CenteredText(text,(640,300), textSize = size)
        if len(text2) > 40:
            FontRenderer.CenteredText(' '.join(text2.split()[:6]),(640,400), textSize = 20).draw(self.screen)
            FontRenderer.CenteredText(' '.join(text2.split()[6:]),(640,450), textSize = 20).draw(self.screen)
        else:
            FontRenderer.CenteredText(text2,(640,400), textSize = 15).draw(self.screen)
        running = True
        messege.draw(self.screen)
        pygame.display.update()
        while running:
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == K_RETURN or event.key == K_ESCAPE:
                        self.fadeIn()
                        return

    def fadeIn(self):
        fadePad = pygame.Surface((self.settings.width,self.settings.height))
        fadePad.fill("#101010")
        alpha = 40
        while True:
            alpha += 11
            if alpha > 255:
                break
            fadePad.set_alpha(alpha)
            self.screen.blit(fadePad,(0,0))
            pygame.display.flip()
            pygame.time.delay(2)
        self.screen.fill("#101010")
        pygame.time.delay(50)

if __name__ == "__main__":
    game = Game()
    pygame.quit()
