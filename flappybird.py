from lib2to3.refactor import get_all_fix_names
import random
from sys import exit
from tkinter import Toplevel
import pygame

H = 600
W = 288

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("flappy.ai")
pygame.font.init()
score_font = pygame.font.SysFont('Comic Sans MS', 30)


class Background :
    class sky :
        def __init__(self) -> None:
            self.image = pygame.image.load('imgs/bg.png').convert()

        def draw(self, screen) :
            screen.blit(self.image, (0, 0))

    class ground :
        def __init__(self) -> None:
            self.image = pygame.image.load('imgs/base.png').convert()

        def draw(self, screen) :
            screen.blit(self.image, (0, 500))


    def __init__(self) -> None:
        self.sky = self.sky()
        self.ground = self.ground()


            
class Bird :
    def __init__(self) -> None:
        self.x = 50
        self.y = H/2
        self.gravity = 0.4
        self.velocity = 0
        self.game_state = 1
        self.lift = 6.5
        self.image = pygame.image.load('imgs/bird1.png').convert_alpha()
        self.rect = self.image.get_rect(center=(self.x, self.y))
    

    
    def update(self, game_state) :
        self.game_state = game_state
        if (self.game_state) :
            self.velocity += self.gravity
            if (self.rect.bottom >= 500) :
                self.velocity=0
            self.y += self.velocity
    
    def draw(self, screen) :
        self.rect.center = (self.x, self.y)
        if(self.rect.top) <= 0 :
            self.rect.top = 0
            self.velocity = 1
        if(self.rect.bottom) > 500 :
            self.rect.bottom = 500
        screen.blit(self.image, self.rect)
         
    
    def jump(self) :
        if(self.rect.top >= 0 and self.rect.bottom <= 500 and self.game_state) :
            self.velocity -= self.lift
            self.y += self.velocity
 


class Pipe :
    class down :
        def __init__(self, x, y) -> None:
            self.x = x
            self.y = y
            self.image = pygame.image.load('imgs/pipe.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
    
    class up :
        def __init__(self, x, y) -> None:
            self.x = x
            self.y = y
            img = pygame.image.load('imgs/pipe.png').convert_alpha()
            self.image = pygame.transform.flip(img, False, True)
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            

    def __init__(self, x) -> None:
        self.x = x
        self.y = random.randint(-199, 0)
        self.d = 150;
        self.velocity = 2
        self.game_state = 1
        
        self.up = self.up(self.x, self.y)
        self.down = self.down(self.x, self.up.rect.bottom + self.d)

    

    def update(self, game_state) :
        self.game_state = game_state
        if(game_state):
            self.x -= self.velocity
            self.up.rect.left = self.down.rect.left = self.x


    def draw(self, screen) :
        screen.blit(self.up.image, self.up.rect)
        screen.blit(self.down.image, self.down.rect)
    
    def collision(self, bird) :
        if bird.rect.colliderect(self.up.rect) or bird.rect.colliderect(self.down.rect) :
            return True



class Pipes :
    def __init__(self) :
        self.base_x = 400 
        self.game_state = 1
        self.pipes = []
        self.passed = 0
        for i in range (2) :
            pipe = Pipe(self.base_x + i * 200)
            self.pipes.append(pipe)
    
    def draw(self, screen) :
        for pipe in self.pipes :
            pipe.draw(screen)

    def update(self, game_state) :
        self.game_state= game_state
        if (self.game_state) :
            self.pipes = [pipe for pipe in self.pipes if pipe.x>=-50]
            
            if (len(self.pipes)<2) :
                new_pipe = Pipe(self.pipes[len(self.pipes)-1].x + 200)
                self.pipes.append(new_pipe)
                self.passed+=1
        
            for pipe in self.pipes :
                pipe.update(game_state)
    
    def collision(self, bird) :
        for pipe in self.pipes :
            if pipe.collision(bird) :
                return True
        

class Environment :
    def __init__(self) :
        self.bird = Bird()
        self.bg = Background()
        self.pipes = Pipes()
        self.game_state = 1
        self.score = 0
        self.temp_score = 0
        self.dist = 0
    

    def run(self, screen) :
        self.bg.sky.draw(screen)
        self.pipes.draw(screen)
        self.bird.draw(screen)
        self.pipes.update(self.game_state)
        self.bird.update(self.game_state)
        self.bg.ground.draw(screen)
        
        if self.pipes.collision(self.bird) or self.bird.rect.bottom >= 500 :  
            self.game_state = 0

        if(self.score != self.pipes.passed) :
            self.score = self.pipes.passed
            print(self.score)
        

        if not self.game_state :
            print("----------------")
            self.__init__()

    
game = Environment()
clock = pygame.time.Clock()
while True :

    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_SPACE :
                game.bird.jump()
        if event.type == pygame.MOUSEBUTTONDOWN :
            game.bird.jump()

    game.run(screen)
    pygame.display.update()
    clock.tick(60)


