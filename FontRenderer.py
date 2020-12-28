import pygame

class CenteredText:

    def __init__(self, text, pos, color = (255,255,255)):
        self.x,self.y = pos
        pygame.font.init()
        font = pygame.font.Font('./FontData/8-bit-pusab.ttf', 20)
        self.txt = font.render(text, True, color)
        self.size = font.size(text) # gives (width, height)

    def draw(self, screen):
        dX = self.x - (self.size[0] / 2.0)
        dY = self.y - (self.size[1] / 2.0)
        screen.blit(self.txt,(dX,dY))

class Button:

    def __init__(self, text, topleft, color='#202020',size = None):
        if size is None:
            size = ((len(text)+1) * 20, 40)
        self.size = size
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect()
        self.rect.topleft = topleft
        self.surf.fill(color)
        self.renderFonts(text)

    def renderFonts(self,text):
        CenteredText(text,(self.size[0]//2, self.size[1]//2)).draw(self.surf)

    def draw(self, surface):
        surface.blit(self.surf,self.rect.topleft)

    def hover(self,mx,my):
        if self.rect.collidepoint(mx,my):
            return True
        return False
