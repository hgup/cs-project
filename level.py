import pygame
from physics import Physics
from settings import Settings
class Platform(pygame.sprite.Sprite):
    """This was made just to check the physics... but may still
    be used for some more complicated stuff like real platforms
    that move independent of the rest of the blocks"""
    def __init__(self,pos_x,pos_y,width = 100,height=20):
        super().__init__()
        self.settings = Settings()
        self.image = pygame.Surface((width,height))
        self.image.fill('orange')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos_x, pos_y
        self.physics = Physics(self.rect,1000)

    def update(self):
        #self.rect.x += 3
        if self.rect.left >= self.settings.width:
            self.rect.right = 0

B = Settings().block_size
class Block(pygame.sprite.Sprite):
    """This represents the token on which the entire
    mapping system is built on. Since, it is a 2d-plane,
    each block has a (x,y) pair. This pair is multiplied
    with the thickness of the square according to the on-screen
    resolution, while blitting"""
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.Surface((B,B))
        self.image.fill('blue')
        self.rect = self.image.get_rect()
        self.pos = pos_x, pos_y
        self.rect.x, self.rect.y = pos_x * B, pos_y * B

