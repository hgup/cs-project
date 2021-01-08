import pygame

class JumpBooster(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.surface((40,40))
        self.rect = self.image.get_rect()

class Invisibility(pygame.sprite.Sprite):
