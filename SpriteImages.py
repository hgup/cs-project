import pygame
import json
class SpriteImages:
    def __init__(self, local = False):
        self.readFile()
        self.local = local
        self.generateObjects()

    def readFile(self):
        with open("./WorldData/blocks.json", 'r') as f:
            self.jsonFile = json.load(f)

    def generateObjects(self):
        self.levelData = [pygame.Surface((40,40))]
        self.levelData[-1].set_colorkey("#000000")
        if self.local:
            path = self.jsonFile['path']
        else:
            path = r'./MultiplayerData/resource_pack/'
        for image in self.jsonFile['images']:
            self.levelData.append(pygame.image.load(path + image))
            self.levelData[-1] = pygame.transform.scale(self.levelData[-1],(40,40))
            self.levelData[-1].set_colorkey("#000000")
    
    def convert(self):
        for i,block in enumerate(self.levelData):
            self.levelData[i] = block.convert()
            


"""
SAMPLE LEVEL DATA
level_1 = [0 for i in range(6)]
level_1[0] = pygame.Surface((40,40))
level_1[1] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/full block.png')
level_1[2] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/top left.png')
level_1[3] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/top right.png')
level_1[4] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/bottom right.png')
level_1[5] = pygame.image.load(r'./WorldData/Level 1/Sprites/World/bottom left.png')
level = [None,level_1]
"""
