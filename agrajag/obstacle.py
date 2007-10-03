#!/usr/bin/python
#coding: utf-8

import pygame
import random
from spaceship import Destructible
from mover import RandomMover, ZigZagMover, CircularMover, LinearMover

class Obstacle(Destructible):
  def __init__(self, g_expl, pos, *groups):
    #AGSprite.__init__(self, pos, *groups)
    Destructible.__init__(self, g_expl, pos, *groups)
    
    size = self.gfx['obstacle']['w'], self.gfx['obstacle']['h']
    
    self.rect = pygame.Rect(pos, size)
    self.image = pygame.Surface(size)
    self.blit_state('obstacle', 'def')

  def update(self):
    pass

class MovingObstacle(Obstacle):
  def __init__(self, g_expl, pos, *groups):
    Obstacle.__init__(self, g_expl, pos, *groups)

   # self.mover = RandomMover([pos[0], pos[1]], 1)
   # self.mover = ZigZagMover([pos[0], pos[1]], 1, 10)
   # self.mover = CircularMover([pos[0], pos[1]], 1, 60)
    self.mover = LinearMover([pos[0], pos[1]], 1, 0)

  def update(self):
    self.update_position()
