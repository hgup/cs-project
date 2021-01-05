import pygame
import random
from pygame.locals import (
        K_a,K_s,K_w,K_d,
        K_h,K_j,K_k,K_l,
        K_LEFT,K_DOWN,K_UP,K_RIGHT)

from physics import Physics

from settings import Settings
controls = {
        1:{K_LEFT:'left',K_DOWN:'down',K_UP:'up',K_RIGHT:'right'},
        0:{K_a:'left',K_s:'down',K_w:'up',K_d:'right'},
        3:{K_h:'left',K_j:'down',K_k:'up',K_l:'right'},
        }
base_acc = 0.3
max_speed = 10
vec = pygame.math.Vector2
colors = ['green','red','white','pink']
class Angel(pygame.sprite.Sprite):

    def __init__(self,pos = [0,0]):
        # essentials
        super(Angel,self).__init__()
        # import settings
        self.settings = Settings()
        # surface and rect
        self.image = pygame.Surface((200,200))
        pygame.draw.circle(self.image,'#27ae60',(100,100),99)
        self.image = pygame.transform.scale(self.image,(30,30))
        self.image.fill('#27ae60')
        self.rect = self.image.get_rect()
        self.rect.x,self.rect.y = pos
        self.image.set_colorkey('#000000')
        # movement
        self.controls = controls[0]
        self.physics = Physics(self.rect,1)
        self.last_state = None
        self.jumping = False
        self.air_timer = 0
        self.colliding = {'top':False,'bottom':False,'left':False,'right':False}
        # additional features
        self.lives = 3
        self.stamina = 10.0
        self.capJump = 12

    def move_x(self):
        # apply physics to player.physics.rect
        self.physics.friction('grass')
        self.physics.motion_x()
        self.rect.move_ip(self.physics.vel.x,0)

    def move_y(self):
        # apply physics to player.physics.rect
        self.physics.gravity('earth')
        self.physics.motion_y()
        self.rect.move_ip(0,self.physics.vel.y)

    def update(self):
        if self.colliding['top']:
            self.physics.vel.y = 0
        if self.colliding['left'] or self.colliding['right']:
            self.physics.vel.x *= -0.5
        if self.colliding['bottom']:
            self.physics.vel.y *= -0.5
            self.air_timer = 0
        else:
            self.air_timer += 1
        if self.jumping  and self.air_timer <= 4:
            self.air_timer += 1 
            self.jump()
        # apply those changes to player's position

        # NOTE: collisions will be implelemnted(restrictions) here

    def start_move(self,e):
        if e.key in self.controls.keys():
            movement = self.controls[e.key]
            if movement == 'left':
                self.physics.acc.x = -base_acc
                self.last_state = 'left'
            if movement == 'right':
                self.last_state = 'right'
                self.physics.acc.x = +base_acc

    def stop_move(self,e):
        try:
            if self.controls[e.key] == self.last_state:
                self.physics.acc = vec(0,0)
            if self.controls[e.key] == 'down':
                self.physics.acc.y = 0
        except:
            pass

    def jump(self):
        self.physics.vel.y = -self.capJump

    def dash(self):
        self.physics.acc.y = 3

    def debug(self):
        pass

