import pygame
from pygame.locals import *
pygame.init()
window = pygame.display.set_mode((400,400))
fps_clock = pygame.time.Clock()
def startScreen():
    running = True
    while running:
        pygame.display.update()
        fps_clock.tick(10)
startScreen()

