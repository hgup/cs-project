import pygame
import random
from pygame.locals import (
        K_a,K_s,K_w,K_d,
        K_h,K_j,K_k,K_l,
        K_LEFT,K_DOWN,K_UP,K_RIGHT)

from physics import Physics

from settings import Settings

controls = {
        0:{K_LEFT:'left',K_DOWN:'down',K_UP:'up',K_RIGHT:'right'},
        1:{K_a:'left',K_s:'down',K_w:'up',K_d:'right'},
        3:{K_h:'left',K_j:'down',K_k:'up',K_l:'right'},
        }

vec = pygame.math.Vector2

import json
class Angel(pygame.sprite.Sprite):

    def __init__(self,_id,pos = [0,0],color = '#f0f0f0'):
        # essentials
        super(Angel,self).__init__()
        # import settings
        self.settings = Settings()
        # set id
        self.id = _id
        # surface and rect
        self.image = pygame.Surface((200,200))
        pygame.draw.circle(self.image,color,(100,100),99)
        self.image = pygame.transform.scale(self.image,(30,30))
        self.image.fill(color)
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
        self.wall = False
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
        self.wall = False
        if self.colliding['top']:
            self.physics.vel.y *= 0.2

        if self.colliding['left']:
            self.physics.vel.x *= -0.5
            if self.moving:
                self.wall = True
                self.air_timer = True

        if self.colliding['right']:
            self.physics.vel.x *= -0.5
            if self.moving:
                self.wall = True
                self.air_timer = True

        if self.colliding['bottom']:
            self.physics.vel.y *= -0.5
            self.air_timer = True
        else:
            pass
        acc = 0
        if self.jumping  and self.air_timer:
            if self.wall:
                if self.colliding['right']:
                    self.physics.vel.x = -10
                    self.physics.acc.x += 0.3
                elif self.colliding['left']:
                    self.physics.vel.x = +10
                    self.physics.acc.x -= 0.3
            self.wall = False
            self.air_timer = False
            self.jump()
        if self.wall:
            self.physics.vel.y += 0.0001
            if self.physics.vel.y > 0.6:
                self.physics.vel.y = 0.6
            self.physics.vel.x = 0
            self.physics.fr = 0.1
        else:
            self.physics.fr = 0
        # apply those changes to player's position

        # NOTE: collisions will be implelemnted(restrictions) here

    def start_move(self,e):
        if e.key in self.controls.keys():
            movement = self.controls[e.key]
            self.moving = True
            if movement == 'left':
                self.physics.acc.x = -self.settings.base_acc
                self.last_state = 'left'
            if movement == 'right':
                self.last_state = 'right'
                self.physics.acc.x = +self.settings.base_acc

    def stop_move(self,e):
        try:
            if self.controls[e.key] == self.last_state:
                self.moving = False
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

