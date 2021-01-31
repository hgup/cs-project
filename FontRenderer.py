import pygame

class CenteredText:

    def __init__(self, text, pos, color = (255,255,255),textSize = None):
        self.x,self.y = pos
        pygame.font.init()
        self.size = textSize if textSize is not None else 20
        self.font = pygame.font.Font('./FontData/8-bit-pusab.ttf', self.size)
        self.renderText(text,color)

    def renderText(self,text,color):
        self.txt = self.font.render(text, True, color)
        self.size = self.font.size(text) # gives (width, height)


    def draw(self, screen):
        dX = self.x - (self.size[0] / 2.0)
        dY = self.y - (self.size[1] / 2.0)
        screen.blit(self.txt,(dX,dY))

class Button:

    def __init__(self, text, pos, color='#202020',size = None,textSize = 25, key='black'):
        self.textSize = textSize
        self.size = size if size is not None else ((len(text)+2) * textSize, textSize*2)
        self.surf = pygame.transform.scale(pygame.image.load('./OtherData/button.png'),self.size)
        self.rect = self.surf.get_rect()
        self.rect.center = pos
        self.color = color
        self.key = key
        if self.color is None:
            self.surf.set_colorkey(key)
        self.renderFonts(text)

    def renderFonts(self,text):
        if self.color is not None:
            self.surf.fill(self.color)
        else:
            self.surf.fill(self.key)
        self.font = CenteredText(text,(self.size[0]//2, self.size[1]//2),textSize = self.textSize)
        self.font.draw(self.surf)

    def draw(self, surface):
        surface.blit(self.surf,self.rect.topleft)

    def hover(self,mx,my):
        if self.rect.collidepoint(mx,my):
            self.surf.set_alpha(255)
            self.font.draw(self.surf)
            return True
        else:
            self.surf.set_alpha(180)
            self.font.draw(self.surf)
            return False

class RButton(Button):

    def __init__(self, text, pos, color=(32,32,32), size = None,textSize = 25, key='black'):
        self.textSize = textSize
        self.size = size if size is not None else ((len(text)+2) * textSize, textSize*2)
        self.surf = pygame.transform.scale(pygame.image.load('./OtherData/button.png'),self.size)
        self.rect = self.surf.get_rect()
        self.rect.center = pos
        self.color = color
        self.surf.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        self.surf.fill(self.color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
        self.renderFonts(text)

    def renderFonts(self,text):
        self.font = CenteredText(text,(self.size[0]//2, self.size[1]//2 -2),textSize = self.textSize)
        self.font.draw(self.surf)
