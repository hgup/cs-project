import pygame

level_1 = [0 for i in range(6)]
level_1[0] = pygame.Surface((40,40))
level_1[1] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/full block.png')
level_1[2] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/top left.png')
level_1[3] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/top right.png')
level_1[4] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/bottom right.png')
level_1[5] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/bottom left.png')

for i in range(len(level_1)):
    level_1[i] = pygame.transform.scale(level_1[i],(40,40))
    level_1[i].set_colorkey("#000000")
levels = [None,level_1]
