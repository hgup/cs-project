#-------------- IMPORTS ---------------#
import ctypes

class Settings:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.fps = 60
        self.playerWidth = 20
        self.playerHeight = 20
        self.gravity = 0.5
        self.num_of_players = 3
        self.block_size = 32

    def getDisplaySize(self):
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        return screensize
