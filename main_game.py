#imports game modules
import sys
import pygame
import pickle
from pygame.locals import (
        K_ESCAPE,KEYUP,KEYDOWN,K_w,QUIT,FULLSCREEN)
# import my modules
import sprites
import level
from settings import *
#from gameMenu import Menu

# order for the players will always remain
# A1, G1, A2, G2, A3, G3 ...
class Game:
    def __init__(self):
        self.settings = Settings()
        self.fpsClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.settings.width,self.settings.height))
        self.running = True
        # only useful for drawing Group
        self.playerGroup = pygame.sprite.Group()
        self.map = pygame.sprite.Group()
        self.player = sprites.Angel(pos=[100,100])
        self.playerGroup.add(self.player)
        self.map = mapLoader.Map()
        # map elements
        self.bg = pygame.image.load(r'./WorldData/Level 1/bg.png')
        #self.menu = Menu()
        # after everything start the mainloop
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
        # playerSprites_update
        self.move()
        # environment_update
        self.map.update()
        self.playerGroup.update()

    def draw(self):
        # fill with black
        self.screen.blit(self.bg,(0,0))
        # draw environment
        self.map.draw(self.screen)
        # draw players
        self.playerGroup.draw(self.screen)
        #self.screen.blit(self.player.image,self.player.rect)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == KEYDOWN:
                    self.player.start_move(event)
                    if event.key == K_ESCAPE:
                        self.running = False
                    if event.key == K_w:
                        self.player.jumping = True
            if event.type == KEYUP:
                    self.player.stop_move(event)
                    if event.key == K_w:
                        self.player.jumping = False

    def move(self):
        self.player.colliding = {'top':False,'bottom':False,'left':False,'right':False}
        self.player.move_x()
        s = pygame.sprite.spritecollideany(self.player,self.map)
        if s:
            if self.player.physics.vel.x > 0:
                self.player.colliding['right'] = True
                self.player.rect.right = s.rect.left
            elif self.player.physics.vel.x < 0:
                self.player.colliding['left'] = True
                self.player.rect.left = s.rect.right
        self.player.move_y()
        s = pygame.sprite.spritecollideany(self.player,self.map)
        if s:
            if self.player.physics.vel.y > 0:
                self.player.colliding['bottom'] = True
                self.player.rect.bottom = s.rect.top
            elif self.player.physics.vel.y < 0:
                self.player.colliding['top'] = True
                self.player.rect.top = s.rect.bottom

    def start(self):
        # set running is true
        # running
        pass

if __name__ == "__main__":
    game = Game()
    pygame.quit()
    input("Press any key)
