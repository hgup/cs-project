#imports game modules
import sys
import pygame
import pickle
import numpy
import random
from pygame.locals import *
# import my modules
import sprites
import level
from settings import *
import mapLoader
#from gameMenu import Menu

# order for the players will always remain
# A1, G1, A2, G2, A3, G3 ...
class MenuBlocks(pygame.sprite.Sprite):
    def __init__(self,img,pos):
        super().__init__()
        self.image = pygame.image.load(r'./OtherData/' + img)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.value = 1
class Game:
    def __init__(self):
        #---------------- PYGAME STUFF ------------------#
        self.settings = Settings()
        self.displaySize = self.settings.getDisplaySize()
        self.screen = pygame.Surface((self.settings.width,self.settings.height))
        self.screen = pygame.display.set_mode((self.settings.width,self.settings.height),FULLSCREEN)
        self.fpsClock = pygame.time.Clock()
        self.homeScreen()
    
    def newGame(self):
        #---------------- SPRITE STUFF ------------------#
        self.playerGroup = pygame.sprite.Group()
        self.player = sprites.Angel(pos=[200,100])
        self.playerGroup.add(self.player)
        #---------------- MAP INIT STUFF ----------------#
        level = self.startScreen()
        self.map = mapLoader.Map(level)
        self.bg = pygame.image.load(r'./WorldData/Level '+str(level)+r'/bg.png')
        #---------------- GAME RUNTIME STUFF ------------#
        self.running = True
        self.cam = pygame.math.Vector2(1.0,0.0)
        self.focus = [(self.settings.width + self.player.rect.width) // 2,(self.settings.height + self.player.rect.height) // 2]
        self.mainloop()

    def mainloop(self):
        while self.running:
            # handle, update and draw
            self.handleEvents()
            self.update()
            self.draw()
            # flip and tick
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)

    def update(self):
        #---------------- player updates ------------#
        self.move(self.map.group)
        self.cam[0] += (self.player.rect.x - self.cam[0] - self.focus[0])/20
        self.cam[1] += (self.player.rect.y - self.cam[1] - self.focus[1])/20
        self.cam[0] = int(self.cam[0])
        self.cam[1] = int(self.cam[1])
        self.map.group.update()
        self.playerGroup.update()
        #---------------- MAP UPDATES ---------------#
        if self.player.rect.y >= self.settings.height * 2:
            self.player.rect.topleft = random.choice([(0,0),(1000,0),(1700,0)])
            self.player.physics.vel = pygame.math.Vector2(0.0,0.0)

    def blitAndFlip(self):
        self.display.fill("#101010")
        self.display.blit(pygame.transform.scale(self.screen,self.displaySize),(0,0))
        pygame.display.flip()

    def drawPlayers(self):
        for player in self.playerGroup.sprites():
            self.screen.blit(player.image,(player.rect.x - self.cam[0],player.rect.y - self.cam[1]))



    def draw(self):
        # fill with black
        self.screen.blit(self.bg,(0,0))
        # draw environment
        self.map.draw(self.screen, self.cam)
        # draw players
        self.drawPlayers()
        #self.screen.blit(self.player.image,self.player.rect)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == KEYDOWN:
                    self.player.start_move(event)
                    if event.key == K_ESCAPE:
                        self.home = False
                        self.running = False
                    if event.key == K_DOWN:
                        self.player.dash()
                    if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                        self.player.jumping = True
            if event.type == KEYUP:
                    self.player.stop_move(event)
                    if event.key == K_SPACE or event.key == K_UP or event.key == K_w:
                        self.player.jumping = False

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

    def startScreen(self):
        self.menu = True
        while self.menu:
            for event in pygame.events.get():
                if event.type == KEYUP:
                    if event.key == K_Enter:
                        return 1

    def homeScreen(self):
        self.home = True
        self.bg = pygame.image.load('./OtherData/home.png')
        selection = 0
        self.homeGroup = pygame.sprite.Group()
        self.player = sprites.Angel([633,100],'#ec565c')
        for i in [('options.png',(35,535)),('play.png',(480,520)),('exit.png',(950,545)),('T.png',(632,154))]:
            self.homeGroup.add(MenuBlocks(i[0],i[1]))

        while self.home:
            self.screen.blit(self.bg,(0,0))
            self.handleEvents()
            self.move(self.homeGroup)
            self.player.update()
            self.screen.blit(self.player.image,self.player.rect.topleft)
            self.homeGroup.draw(self.screen)
            pygame.display.update()
            self.fpsClock.tick(self.settings.fps)
        self.player.kill()

if __name__ == "__main__":
    game = Game()
    pygame.quit()
