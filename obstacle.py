#!/usr/bin/python
#coding: utf-8

'''Dummy object intended to place on a level just to display something.
'''

import pygame
import random
from spaceship import Destructible
from mover import RandomMover, ZigZagMover, CircularMover, LinearMover

class Obstacle(Destructible):
  def __init__(self, pos, *groups):
    Destructible.__init__(self, pos, *groups)
    
    size = self.gfx['obstacle']['w'], self.gfx['obstacle']['h']
    
    self.image = pygame.Surface(size)
    self._blit_state('obstacle', 'def')

    self._initialize_position(pos, ('left', 'top'), size)

class MovingObstacle(Obstacle):
  def __init__(self, pos, *groups):
    Obstacle.__init__(self, pos, *groups)

    self.mover = RandomMover(pos, 50, {})
    #self.mover = ZigZagMover(pos, 100, {})
    #self.mover = CircularMover([pos[0], pos[1]], 1, {})
    #self.mover = LinearMover([pos[0], pos[1]], 1, {})
    #self.mover = LinearMover([pos[0], pos[1]], 60, {})
