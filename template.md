# put this go function inside
    def go(self,val):
        if val == 1:
            self.offy -= 5
            self.rect.y -= 5
        if val == 2:
            self.offy += 5
            self.rect.y += 5
        if val == 3:
            self.offx += 5 
            self.rect.x -= 5
        if val == 4:
            self.offy += 5
            self.rect.x += 5
        print(self.offx,self.offy)

# put these two variables in __init__

        self.offx = 0
        self.offy = 0
# also with this, add parameter g to update

    def update(self,*args,g):
        self.go(g)

# add to __init__ of main game
        self.g = 0

# in event loop in main
    def events(self):
        self.g = 0
        ## your other code ##
        for event in pygame.event.get():
                if event.key == K_w:
                    self.g = 1
                if event.key == K_s:
                    self.g = 2
                if event.key == K_a:
                    self.g = 3
                if event.key == K_d:
                    self.g = 4
