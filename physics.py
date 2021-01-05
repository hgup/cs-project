import pygame
vec = pygame.math.Vector2
from settings import Settings
g = {
        "Earth": 0.3,
        "Moon": 0.1,
        "Bed": 0.4,
        "earth": 0.3,
        "moon": 0.1,
        "bed": 0.4
}

f = {
        "grass": (-0.02,1),
        'collide':(0.5,1)
}

class Physics:
    def __init__(self,rect,density):
        self.pos = vec(0,0) #top left of mass
        self.settings = Settings()
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.density = density
        self.volume = rect.width * rect.height * 1
        # for our 2d convention we assume everything to be 1units wide
        self.mass = self.volume * self.density
        self.momentum = vec(0,0)
        self.i = 0

    def motion_x(self):
        self.vel.x += self.acc.x

    def motion_y(self):
        self.vel.y += self.acc.y

    def gravity(self,region): #region eg. Earth, moon, My bed
        self.vel += vec(0,g[region])
        if self.vel.y > 16:
            self.vel.y = 16

    def friction(self,surface):
        # Friction always works in the direction opposite to the direction
        # in which the object is moving, or trying to move.
        deceleration = self.vel.x * f[surface][0]
        if deceleration > f[surface][1]: # limiting friction
            deceleration = f[surface][1]
        self.vel += vec(deceleration,0)
