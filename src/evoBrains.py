#!/usr/bin/env python

import pygame
import random
import math
from agent import Agent

class World:
    def __init__ (self):
        self.viewWorld = True
        self.generation = 1
        self.epoch = 0
        self.dimension = (1024,768)
        self.population = 12
        self.numObstacles = 50
        self.foodAvailable = 60
        self.agentsBest = 4
        self.agentsSelect = 8
        self.bgColor = (125, 220, 255, 0)
        self.agentColor = (50, 50, 220, 0)
        self.foodColor = (50, 220, 50, 0)
        self.obsColor = (44, 44, 44, 0)
        self.obstacles = list()
        self.agents = list()
        self.food = list()

    def setDimension (self, dim):
        self.dimension = dim
        
    def setPopulation (self, pop):
        self.population = pop
        
    def setNumObstacles (self, obs):
        self.numObstacles = obs

    def _initObstacles (self):
        self.obstacles = list ()
        cx = self.dimension[0]/2
        cy = self.dimension[1]/2
        safeZone = pygame.Rect (cx - 50, cy - 50, 50, 50)
        for o in range (self.numObstacles):
            obst = None
            coll = True
            while coll:
                x = random.randint (0, self.dimension[0])
                y = random.randint (0, self.dimension[1])
                w = random.randint (10, 100)
                h = random.randint (10, 100)
                obst = pygame.Rect (x, y, w, h)
                coll = obst.colliderect (safeZone)
            self.obstacles.append (obst)

    def _drawObstacles (self):
        for o in self.obstacles:
            pygame.draw.rect (self.screen, self.obsColor, o, 0)

    def _initAgents (self):
        for a in range (self.population):
            agent = Agent (self.dimension)
            self.agents.append (agent)
        
    def _drawAgents (self):
        for a in self.agents:
            t = 3
            if a.energy > 0:
                t = 0
            yd = math.sin (a.direction)
            xd = math.cos (a.direction)
            end = (a.position[0] + a.radius * xd, a.position[1] + a.radius * yd)
            pos = (int (a.position[0]), int (a.position[1]))
            pygame.draw.circle (self.screen, self.agentColor, pos, int (a.radius), t)
            pygame.draw.line (self.screen, (255,255,255,0), a.position, end, 2)
            for s in range (3):
                ang_s = -0.5 * math.pi + s * .5 *  math.pi
                ang_s += a.direction
                yd = math.sin (ang_s)
                xd = math.cos (ang_s)
                end = (int(a.position[0] + a.rangeObs * xd), int(a.position[1] + a.rangeObs * yd))
                pygame.draw.line (self.screen, (150,150,150,0), a.position, end, 1)
                pygame.draw.circle (self.screen, (150,150,150,0), end, 2)
                

    def _initFood (self, count = -1):
        cx = self.dimension[0]/2
        cy = self.dimension[1]/2
        safeZone = pygame.Rect (cx - 50, cy - 50, 150, 150)
        if count < 0:
            self.food = list ()
            count = self.foodAvailable
        for i in range (count):
            coll = True
            fp = None
            while coll:
                fp = (random.randint (0, self.dimension[0]), random.randint (0, self.dimension[1]))
                for o in self.obstacles + [safeZone]:
                    coll = o.collidepoint (fp)
                    if coll:
                        break
            self.food.append ((fp))

    def _drawFood (self):
        for f in self.food:
            pygame.draw.circle (self.screen, (50, 220, 50, 0), f, 4)

    def _drawWorld (self):
        self.screen.fill (self.bgColor)
        self._drawObstacles ()
        self._drawAgents ()
        self._drawFood ()
        pygame.display.flip ()

    def _updateAgents (self):
        dead = 0
        for a in self.agents:
            if a.energy > 0:
                findex = a.updateAgent (self.food, self.obstacles)
                if findex > 0:
                    self.food.pop (findex)
            else:
                dead += 1
        return dead

    def _mateAgents (self):
        new_agents = filter (lambda a: a.foodTaken > 0, self.agents)
        slots = self.population - len (new_agents)
        if len(new_agents) == 0:
            for i in range (slots):
                new_agents.append (Agent (self.dimension))
        else:
            for i in range (slots):
                id1 = random.randint (0, slots-1)
                id2 = random.randint (0, slots-1)
                new_agents.append (self.agents[id1].mate (self.agents[id2]))
                                   
        #new_agents = list ()
        #for i in range (self.agentsBest):
        #    ba = self.agents.pop (0)
        #    pool -= 1
        #    if pool > 0:
        #        pa = self.agents.pop(random.randint (0, pool - 1))
        #    else:
        #        pa = self.agents.pop (0)
        #    pool -= 1
        #    new_agents.append (ba.mate (pa))
        #    new_agents.append (ba)
        #    new_agents.append (pa)
        #for k in range (self.population - len(new_agents)):
        #    new_agents.append (Agent(self.dimension))

        for a in new_agents:
            a.reinit ()
        self.agents = new_agents

    def start (self):
        stopWorld = False
        forceEnd = False
        self.screen = pygame.display.set_mode (self.dimension)
        self._initObstacles ()
        self._initAgents ()
        self._initFood (self.foodAvailable)

        while not stopWorld:
            self.epoch += 1
            if self.epoch > 20000:
                forceEnd = True
            for event in pygame.event.get ():
                if event.type == pygame.QUIT:
                    stopWorld = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.viewWorld = not self.viewWorld
            dead = self._updateAgents ()
            self._initFood (self.foodAvailable - len(self.food))
            if self.viewWorld:
                self._drawWorld ()
            if dead >= self.population - 1  or forceEnd:
                self.agents.sort (key = lambda a: a.lifespan * a.foodTaken, reverse = True)
                print ("Generation %d terminated in %d epochs, initializing a new one..." % (self.generation, self.epoch))
                for a in self.agents:
                    print (a.lifespan, a.foodTaken)
                self._mateAgents ()
                self.epoch = 0
                self.generation += 1
                self._initObstacles ()
                self._initFood ()
                forceEnd = False
            if self.epoch % 1000 == 0:
                print ("Generation: %d - Epoch: %d" % (self.generation, self.epoch))
            

def main ():
    pygame.init ()
    world = World ()
    world.setDimension ((1024, 768))
    world.setPopulation (16)
    world.setNumObstacles (20)
    
    world.start()

if __name__ == '__main__':
    main ()
