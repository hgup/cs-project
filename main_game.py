#imports game modules
import sys
import pygame
import pickle
import numpy
from pygame.locals import *
# import my modules
import sprites
import level
from settings import *
import mapLoader
#from gameMenu import Menu

# order for the players will always remain
# A1, G1, A2, G2, A3, G3 ...
class Game:
    def __init__(self):
        #---------------- PYGAME STUFF ------------------#
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.width,self.settings.height))
        self.fpsClock = pygame.time.Clock()
        #---------------- SPRITE STUFF ------------------#
        self.playerGroup = pygame.sprite.Group()
        self.player = sprites.Angel(pos=[100,100])
        self.playerGroup.add(self.player)
        #---------------- MAP INIT STUFF ----------------#
        self.map = mapLoader.Map(1)
        self.bg = pygame.image.load(r'./WorldData/Level 1/bg.png')
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
        self.move()
        self.cam[0] += (self.player.rect.x - self.cam[0] - self.focus[0])/20
        self.cam[1] += (self.player.rect.y - self.cam[1] - self.focus[1])/20
        self.map.group.update()
        self.playerGroup.update()
        #---------------- MAP UPDATES ---------------#

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
                        self.running = False
                    if event.key == K_w:
                        self.player.jumping = True
            if event.type == KEYUP:
                    self.player.stop_move(event)
                    if event.key == K_w:
                        self.player.jumping = False

    def collisionDetect(self,entity,group):
        for entity2 in group.sprites():
            if entity2.value:
                if entity.rect.colliderect(entity2.rect):
                    return entity2


    def move(self):
        self.player.colliding = {'top':False,'bottom':False,'left':False,'right':False}
        self.player.move_x()
        s = self.collisionDetect(self.player,self.map.group)
        if s:
            if self.player.physics.vel.x > 0:
                self.player.colliding['right'] = True
                self.player.rect.right = s.rect.left
            elif self.player.physics.vel.x < 0:
                self.player.colliding['left'] = True
                self.player.rect.left = s.rect.right
        self.player.move_y()
        s = self.collisionDetect(self.player,self.map.group)
        if s:
            if self.player.physics.vel.y > 0:
                self.player.colliding['bottom'] = True
                self.player.rect.bottom = s.rect.top
            elif self.player.physics.vel.y < 0:
                self.player.colliding['top'] = True
                self.player.rect.top = s.rect.bottom

if __name__ == "__main__":
    game = Game()
    pygame.quit()
    input("Press any key")
