import pygame
import json
class SpriteImages:
    def __init__(self):
        self.readFile()
        self.levels = [None]
        self.generateObjects()

    def readFile(self):
        with open("./WorldData/blocks.json", 'r') as f:
            self.jsonFile = json.load(f)

    def generateObjects(self):
        for levelNo in self.jsonFile:
            levelData = [pygame.Surface((40,40))]
            levelData[-1].set_colorkey("#000000")
            path = self.jsonFile[levelNo]['path']
            for image in self.jsonFile[levelNo]['images']:
                levelData.append(pygame.image.load(path + image))
                levelData[-1] = pygame.transform.scale(levelData[-1],(40,40))
                levelData[-1].set_colorkey("#000000")
            self.levels.append(levelData)


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
