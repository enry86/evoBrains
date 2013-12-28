#!/usr/bin/env python

import pygame
import random

class World:
    def __init__ (self):
        self.dimension = (1024,768)
        self.population = 10
        self.numObstacles = 10
        self.bgColor = (125, 220, 255, 0)
        self.obstacles = list()

    def setDimension (self, dim):
        self.dimension = dim
        
    def setPopulation (self, pop):
        self.population = pop
        
    def setNumObstacles (self, obs):
        self.numObstacles = obs

    def _initObstacles (self):
        for o in range (self.numObstacles):
            x = random.randint (0, self.dimension[0])
            y = random.randint (0, self.dimension[1])
            w = random.randint (0, 100)
            h = random.randint (0, 100)
            obst = pygame.Rect (x, y, w, h)
            self.obstacles.append (obst)

    def _drawObstacles (self):
        for o in self.obstacles:
            pygame.draw.rect (self.screen, (44, 44, 44, 0), o, 0)

    def start (self):
        stopWorld = False
        self.screen = pygame.display.set_mode (self.dimension)
        self.screen.fill (self.bgColor)
        self._initObstacles ()
        self._drawObstacles ()
        
        while not stopWorld:
            for event in pygame.event.get ():
                if event.type == pygame.QUIT:
                    stopWorld = True
            pygame.display.flip ()
            

def main ():
    world = World ()
    world.setDimension ((1024, 768))
    world.setPopulation (1)
    world.setNumObstacles (20)
    
    world.start()

if __name__ == '__main__':
    main ()
