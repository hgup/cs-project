#-------------- IMPORTS ---------------#
import ctypes
import json
with open('settings.json','r') as f:
    data = json.load(f)

class Settings:
    def __init__(self):
        self.width = data["width"]
        self.height = data["height"]
        self.fps = data["fps"]
        self.playerWidth = data["playerWidth"]
        self.playerHeight = data["playerHeight"]
        self.gravity = data["gravity"]
        self.block_size = data["block_size"]
        self.colors = data["colors"]
        self.base_acc = data["base_acc"]
        self.lastAddress = data["lastAddress"]
        self.lastPort = data["lastPort"]
        self.lastName = data["lastName"]

    def getDisplaySize(self):
        try:
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return screensize
        except:
            return (1280,720)

    def update(self):
        dataR = {}
        dataR["width"] = self.width
        dataR["height"] = self.height
        dataR["fps"] = self.fps
        dataR["playerWidth"] = self.playerWidth
        dataR["playerHeight"] = self.playerHeight
        dataR["gravity"] = self.gravity
        dataR["block_size"] = self.block_size
        dataR["colors"] = self.colors
        dataR["base_acc"] = self.base_acc
        dataR["lastAddress"] = self.lastAddress
        dataR["lastPort"] = self.lastPort
        dataR["lastName"] = self.lastName
        dataR["bounds"] = data['bounds']
        with open('settings.json','w') as f:
            json.dump(dataR,f)

LB_x = LB_y = 0 - data['bounds']
UB_x = data['bounds'] + data['width']
UB_y = data['bounds'] + data['height']

if __name__ == '__main__':
    s = Settings()
    s.lastPort = 1234
    s.update()
