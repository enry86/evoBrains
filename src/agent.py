#!/usr/bin/env python

import pygame
import math
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import SigmoidLayer

class Agent:
    
    def __init__ (self, worldsize, netParams = None):
        self.worldsize = worldsize
        self.direction = 0.0
        self.energy = 1000.0
        self.lifespan = 0.0
        self.position = [worldsize[0] / 2, worldsize[1] / 2]
        self.rangeObs = 50.0
        self.rangeFood = 100.0
        self.radius = 10.0
        self.nrgFood = 100.0
        self.damageObs = 2.0
        self.damageAge = 0.8
        self.brain = buildNetwork (6, 8, 2, outclass = SigmoidLayer)
        self.maxSpeed = .50
        self.speed = 0.0
        self.dirRange = math.pi / 100
        if netParams:
            self.brain._setParameters (netParams)

    def _getSensorValue (self, obsts):
        steps = 10
        sensors = [0,0,0]
        for s in range (steps):
            dst = self.rangeObs / steps * (s + 1)
            for i in range (3):
                if sensors[i] < steps - s:
                    ang = (- 0.5 * math.pi + (i * .5 * math.pi)) % (2 * math.pi)
                    ang = (ang + self.direction) % (2 * math.pi)
                    point = (math.cos(ang) * dst + self.position[0], math.sin (ang) * dst + self.position[1])
                    if point[0] < 0 or point[1] < 0:
                        coll = True
                    if point[0] >= self.worldsize[0] or point[1] >= self.worldsize[1]:
                        coll = True
                    coll = False
                    for o in obsts:
                        coll = o.collidepoint (point)
                        if coll:
                            break
                    if coll:
                        sensors[i] = steps - s 
        return sensors
                
    def _lookForFood (self, food):
        index = -1
        mindst = float("inf")
        direction = -1
        for i in range ( len (food)):
            f = food[i]
            x = self.position[0] - f[0]
            y = self.position[1] - f[1]
            dst = math.sqrt (x*x + y*y)
            if dst < mindst and dst < self.rangeFood:
                index = i
                mindst = dst
                dir_f = math.atan2(y, x) % (2 * math.pi)
                direction = (dir_f - self.direction) % (2 * math.pi)
        return [mindst, direction], index


    def _updateMovement (self, food, obsts):
        distances = self._getSensorValue (obsts)
        food = self._lookForFood (food)[0]
        inputs = distances + food + [self.energy]
        dr, sp = self.brain.activate (inputs)
        dr = -self.dirRange + (dr * 2 * self.dirRange)
        self.direction = (self.direction + dr) % (2 * math.pi)
        self.speed = -1 + (sp * 2)
        #self.speed = 0.1
        #self.direction = 0.0

    def _getFood (self, food):
        nrg = 0
        index = -1
        nearest, tmpindex = self._lookForFood (food)
        if nearest[0] < self.radius * 2 and nearest[0] >= 0:
            index = tmpindex
            nrg = self.nrgFood
        return nrg, index
    
    def _hitObstacle (self, pos, obsts):
        damage = 0
        x = pos[0] - self.radius
        y = pos[1] - self.radius
        bound = pygame.Rect (x, y,2 * self.radius, 2 * self.radius)
        if bound.collidelist (obsts) > 0:
            damage = self.damageObs
        if pos[0] < self.radius or pos[1] < self.radius:
            damage = self.damageObs
        if pos[0] >= self.worldsize[0] - self.radius or pos[1] >= self.worldsize[1] - self.radius:
            damage = self.damageObs
        return damage
        
    def updateAgent (self, food, obsts):
        self.lifespan += 1
        self._updateMovement (food, obsts)
        spdx = math.cos (self.direction)
        spdy = math.sin (self.direction)
        dst = self.speed * self.maxSpeed
        newpos = [self.position[0] + spdx * dst, self.position[1] + spdy * dst]
        damage = self._hitObstacle (newpos, obsts)
        if damage == 0:
            self.position = newpos
        nrgFood, idFood = self._getFood (food)
        self.energy += nrgFood
        self.energy -= damage
        self.energy -= dst
        self.energy -= self.damageAge
        return idFood
        
        
