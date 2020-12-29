import pygame

class CenteredText:

    def __init__(self, text, pos, color = (255,255,255),textSize = None):
        self.x,self.y = pos
        pygame.font.init()
        self.size = textSize if textSize is not None else 20
        font = pygame.font.Font('./FontData/8-bit-pusab.ttf', self.size)
        self.txt = font.render(text, True, color)
        self.size = font.size(text) # gives (width, height)

    def draw(self, screen):
        dX = self.x - (self.size[0] / 2.0)
        dY = self.y - (self.size[1] / 2.0)
        screen.blit(self.txt,(dX,dY))

class Button:

    def __init__(self, text, pos, color='#202020',size = None,textSize = None):
        self.textSize = textSize if textSize is not None else 20
        self.size = size if size is not None else ((len(text)+1) * 20, 40)
        self.surf = pygame.Surface(self.size)
        self.rect = self.surf.get_rect()
        self.rect.center = pos
        self.color = color
        self.surf.fill(self.color)
        self.renderFonts(text)

    def renderFonts(self,text):
        self.surf.fill(self.color)
        self.font = CenteredText(text,(self.size[0]//2, self.size[1]//2),textSize = self.textSize)
        self.font.draw(self.surf)

    def draw(self, surface):
        surface.blit(self.surf,self.rect.topleft)

    def hover(self,mx,my):
        if self.rect.collidepoint(mx,my):
            self.surf.fill('#87afaf')
            self.font.draw(self.surf)
            return True
        else:
            self.surf.fill(self.color)
            self.font.draw(self.surf)
            return False
