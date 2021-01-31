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
#from gameMenu import Menu

# order for the players will always remain
# A1, G1, A2, G2, A3, G3 ...
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
        self.running = self.joinGame()
        #--------- SPRITE OVER NETWORK STUFF ------------#
        self.playerGroup = pygame.sprite.Group()
        self.net = Network(self.address,self.port)
        self.peers = self.net.peers
        self.vertex = [[(50,50),0],[(100,100),0],[(150,150),0]][:self.peers]
        self.addAllPlayers()
        #---------------- MAP INIT STUFF ----------------#
        level = 1 #self.startScreen()
        self.map = mapLoader.Map(level)
        self.bg = pygame.image.load(r'./WorldData/Level '+str(level)+r'/bg.png')
        #---------------- GAME RUNTIME STUFF ------------#
        self.cam = pygame.math.Vector2(1.0,0.0)
        self.focus = [(self.settings.width - self.player.rect.width) // 2,
                (self.settings.height - self.player.rect.height) // 2]
        self.mainloop()
        self.net.client.close()
        self.homeScreen()

    def addAllPlayers(self):
        # initialize all locations
        for _id in range(self.peers):
            a = sprites.Angel(_id,self.net.initRect,_id)
            self.playerGroup.add(a)
            if self.net.id == _id: # link this game session and player
                self.player = a

    def mainloop(self):
        while self.running:
            # handle, update and draw
            events = pygame.event.get()
            pressed = self.handleGameEvents(events)
            if pressed == K_ESCAPE:
                self.running = False
            Game.handlePlayerEvents(self.player,events)
            self.update()
            self.draw()
            # flip and tick
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)

    def camUpdates(self):
        self.cam[0] += (self.player.rect.x - self.cam[0] - self.focus[0])/20
        self.cam[1] += (self.player.rect.y - self.cam[1] - self.focus[1])/20
        if self.cam[0] < LB_x: self.cam[0] = LB_x
        elif self.cam[0] > UB_x: self.cam[0] = UB_x
        if self.cam[1] < LB_y: self.cam[1] = LB_y
        elif self.cam[1] > UB_y: self.cam[1] = UB_y
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
        if self.player.rect.y >= self.settings.height * 2:
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

    def draw(self):
        # fill with black
        self.screen.blit(self.bg,(0,0))
        # draw environment
        self.map.draw(self.screen, self.cam)
        # draw players
        self.drawAllPlayers()
        #self.screen.blit(self.player.image,self.player.rect)

    def pause(self):
        self.running = False
        try:
            self.net.client.close()
        except:
            pass

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

    def handlePlayerEvents(player,events):
        for event in events:
            if event.type == KEYDOWN:
                    player.start_move(event)
                    if event.key == K_DOWN: player.dash()
                    if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                        player.jumping = True
            if event.type == KEYUP:
                    player.stop_move(event)
                    if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                        player.jumping = False
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
        actions = [None,self.editor,self.newGame,self.newGame]

        done = True
        doneSelected = False
        while self.home:
            events = pygame.event.get()
            s = self.move(self.homeGroup)
            if not doneSelected:
                Game.handlePlayerEvents(self.player,events)
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

    def joinGame(self):

        selected = 9
        joinSprites = []
        joinGroup = pygame.sprite.Group()
        self.player.rect.topleft = (80,-10)
        for i in [('desk.png',(77,600),1)]:#,('join.png',(700,500),2)]:
            x = MenuBlocks(i[0],i[1],i[2])
            joinGroup.add(x)
            joinSprites.append(x)

        ADD = FontRenderer.Button(self.address,(703,264),color=None,key = '#38b6ff',textSize = 30)
        PORT = FontRenderer.Button(self.port,(1030,264),color=None,key = '#38b6ff',textSize = 30)
        bg_image = pygame.image.load(r'./OtherData/Join_Screen.png').convert()
        ADDselected = pygame.Surface((5,80)) #483,224
        ADDselected.fill('#ffffff')
        PORTselected = pygame.Surface((5,60)) #938,234
        PORTselected.fill('#ffffff')
        add = True

        while True:
            if self.player.rect.y  > 800: self.player.rect.topleft = (80,-10)
            events = pygame.event.get()
            s = self.move(joinGroup)
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        if add: self.address = self.address[:-1]
                        else: self.port = self.port[:-1]
                    else:
                        if event.key != K_RETURN and event.key != K_ESCAPE and event.key != K_TAB:
                            if add: self.address += event.unicode
                            else: self.port += event.unicode
                    if event.key == K_TAB:
                        add = not add
                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        return True
            Game.handlePlayerEvents(self.player,events)
            pressed = self.handleGameEvents(events)
            if pressed == K_ESCAPE:
                return False
            self.player.update()
            self.screen.blit(bg_image,(0,0))
            if add:
                self.screen.blit(ADDselected,(483,224))
            else:
                self.screen.blit(PORTselected,(938,234))
            ADD.renderFonts(self.address)
            ADD.draw(self.screen)
            PORT.renderFonts(self.port)
            PORT.draw(self.screen)
            joinGroup.draw(self.screen)
            self.screen.blit(self.player.image,self.player.rect.topleft)
            self.fpsClock.tick(self.settings.fps)
            pygame.display.flip()

    def sorry(self,text):
        messege = FontRenderer.CenteredText(text,(500,300))
        running = True
        while running:
            self.screen.fill('#101010')
            messege.draw(self.screen)
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
