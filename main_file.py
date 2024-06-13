import pygame
import os
import neat
import time
import random

WIN_WIDTH = 528
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROT = 25 # maximum rotation here 25 degrees
    ROT_VEL = 20
    ANIMATION_TIME = 10

    def __init__(self, x, y) -> None: # x and y are the starting position of the bird
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0 # when we last jumped
        self.vel = 0
        self.img = self.IMGS[0]
        self.height = self.y
        self.img_count = 0 # this tells which image we are on currently
        self.gravity =3

    def jump(self):
        self.vel = -10.5 # -ve number to up and +ve number to go down
        self.tick_count =0 # because we ahve just jumped so 0
        self.height = self.y

    def move(self):# this works for every frame in 30 fps in our case
        self.tick_count += 1 # one frame passed by
        self.accleration = self.gravity # this is acceleration due to gravity, and since downward is positive it will remain positive
        d = self.vel * self.tick_count + 0.5*self.accleration*self.tick_count**2

        if d>=16: # if the displacement is more than 16 then make the acceleration =0
            self.accleration =0
        
        elif d<0: # this makes the bird jump nice and smooth nothing much here
            d -=2

        self.y += d

        if d < 0 or self.y < self.height +50: # remove the second condition and check later
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
            
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        self.img_count +=1

        # for flapping part of the bird
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80: # nosediving down directly
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center= self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    

class Pipe:
    GAP = 200 # can be made random using randrange
    VEL = 5 # velocity can be changed to make it more difficult or easy depending on the requirement

    def __init__(self,x) -> None:
        self.x = x
        self.height =0
        self.top =0
        self.bottom =0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # x, y : False, True
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height() # the -ve is for taking the cursor to the top basically
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -=self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird: Bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # basically distance from PIPE to bird

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset) # will give None if not overlapping

        if top_point or b_point: # if either exists then it means it has collided
            return True
        
        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y) -> None:
        self.y = y
        self.x1 =0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # to potray is like a circle
        # very important calculations to print this thing
        if self.x1 + self.WIDTH <0:
            self.x1 = self.x2 +self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        # very important when x1 one finishes we go for x2, basically both are connected to each other with cement basically 😂
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base):    
    win.blit(BG_IMG, (0,0)) # blit is for draw here

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win) # base would be over the pipes which are not properly there kind of, so auto matic cropping would occur
    
    bird.draw(win) # bird would be on the top
    pygame.display.update()

def main():
    bird = Bird(230,350)
    base = Base(730) # these numbers are just calculated
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock() # read about it
    run = True
    score =0


    while run:
        add_pipe = False
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # bird.move()
        rem = [] # auto delete
        for pipe in pipes:
            if pipe.collide(bird= bird):
                pass
                # run = False

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # this means that the pipe is completely off the screen
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            
            pipe.move()
        if add_pipe:
            score += 1
            pipes.append(Pipe(700))
            # add_pipe = False
        for r in rem:
            pipes.remove(r)
        base.move()
        draw_window(win, bird, pipes, base)
    pygame.quit()
    quit()

main()
