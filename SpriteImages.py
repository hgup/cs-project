import pygame

level_1 = [0 for i in range(6)]
level_1[0] = pygame.Surface((40,40))
level_1[1] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/Dirt-M.bmp')
level_1[2] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/Dirt-AM.bmp')
level_1[3] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/Grass-L.bmp')
level_1[4] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/Grass-M.bmp')
level_1[5] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/Grass-R.bmp')

for i in level_1:
    i.set_colorkey("#000000")
levels = [None,level_1]
