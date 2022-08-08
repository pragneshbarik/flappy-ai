from asyncio.windows_utils import pipe
import random
from sys import exit
import pygame
import math
import neat
import os

H = 600
W = 288

pygame.init()



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
        self.omega = 2.5     # Angular Velocity
        self.theta = 0      # Angular Displacement
        self.game_state = 1
        self.lift = 6.5
        self.image = pygame.image.load('imgs/bird1.png').convert_alpha()
        self.rect = self.image.get_rect(center=(self.x, self.y))
    

    def rotate(self) :
        if self.theta <= -85 : self.theta = -85
        if self.theta >= 20 : self.theta = 20 ; self.omega = 2.5
        if self.velocity > 0 : self.theta -= self.omega
        if self.velocity < 0 : self.theta = 20
    
    def fall(self) :
        self.velocity += self.gravity
            if (self.rect.bottom >= 500) :
                self.velocity=0
            self.y += self.velocity


    def update(self, game_state) :
        self.rotate()
        self.game_state = game_state
        if (self.game_state) :
            self.fall()
            
    
    def draw(self, screen) :
        self.rect.center = (self.x, self.y)
        if(self.rect.top) <= 0 :
            self.rect.top = 0
            self.velocity = 1
        if(self.rect.bottom) > 500 :
            self.rect.bottom = 500
        rotated_image = pygame.transform.rotozoom(self.image, self.theta, 1)
        new_rect = rotated_image.get_rect(center = self.rect.center)
        screen.blit(rotated_image, new_rect)
         
    
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
        self.base_x = 200 
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
    def __init__(self, screen) :
        self.screen = screen
        self.bird = Bird()
        self.bg = Background()
        self.pipes = Pipes()
        self.game_state = 1
        self.score = 0
        self.temp_score = 0
        self.dist = 0
    
    def euclidean(self, p1, p2) :
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def network_parameters(self, bird) :
        if len(self.pipes.pipes) == 2 : 
            valid_pipes = [pipe for pipe in self.pipes.pipes if pipe.up.rect.left >= self.bird.rect.right]

        return (abs(valid_pipes[0].up.rect.bottom - bird.rect.centery), abs(valid_pipes[0].down.rect.top-bird.rect.centery), bird.rect.centery, bird.velocity, valid_pipes[0].up.rect.left)
        


    def run(self) :
        self.bg.sky.draw(self.screen)
        self.pipes.draw(self.screen)
        self.bird.draw(self.screen)
        self.pipes.update(self.game_state)
        self.bird.update(self.game_state)
        self.bg.ground.draw(self.screen)
        
        if self.pipes.collision(self.bird) or self.bird.rect.bottom >= 500 :  
            self.game_state = 0


        if(self.score != self.pipes.passed) :
            self.score = self.pipes.passed
            print(self.score)

        if not self.game_state :
            self.__init__(self.screen)

    
    
    def evaluate_genomes(self, genomes, config) :
        self.genotypes = []
        self.networks = []
        self.birds = []
        self.pipes = Pipes()
        self.pipes.passed = 0 # Reinitialize Pipes
        prev_passed = 0

        
        clock = pygame.time.Clock()

        for g_id, genome in genomes :
            genome.fitness = 0
            network = neat.nn.FeedForwardNetwork.create(genome, config)
            self.networks.append(network)
            self.genotypes.append(genome)
            self.birds.append(Bird())
        
        done = False

        while not done and len(self.birds) > 0 :
            
            self.bg.sky.draw(self.screen)
            self.pipes.draw(self.screen)
            self.pipes.update(True)
            score = score_font.render(str(self.pipes.passed), True, (0,0,0))


            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    done  = True
                    pygame.quit()
                    exit()
                    break
            
            for id, bird in enumerate(self.birds) :
                self.genotypes[id].fitness += 0.1
                bird.draw(self.screen)
                bird.update(True)

                output = self.networks[id].activate(self.network_parameters(bird))[0]

                if output > 0 :
                    bird.jump()
                
                if self.pipes.collision(bird) or bird.rect.bottom >= 500 :
                    self.genotypes[id].fitness -= 100
                    self.networks.pop(self.birds.index(bird))
                    self.genotypes.pop(self.birds.index(bird))
                    self.birds.pop(self.birds.index(bird))

        

            
            self.bg.ground.draw(self.screen)        
            self.screen.blit(score, (W-30, 0))
            
            if prev_passed != self.pipes.passed :
                prev_passed = self.pipes.passed
                print(prev_passed)
                for genotype in self.genotypes :
                    genotype.fitness += self.pipes.passed
            
            pygame.display.update()
            clock.tick(120)
        
    def train(self, config_file, generations) :
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

        winner = population.run(self.evaluate_genomes, generations)

    
    def play(self) :
        clock = pygame.time.Clock()
        while True :
            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN :
                    if event.key == pygame.K_SPACE :
                        self.bird.jump()
            
            
            self.run()
            score = score_font.render(str(self.pipes.passed), True, (0,0,0))
            self.screen.blit(score, (W-30, 0))
            pygame.display.update()
            clock.tick(60)
            



screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("flappy.ai")
pygame.font.init()
score_font = pygame.font.SysFont('Arial', 30)


game = Environment(screen)
game.train('config.txt', 1000)