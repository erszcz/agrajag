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
    
    self.image = pygame.Surface(size)
    self._blit_state('obstacle', 'def')

    self._initialize_position(pos, ('left', 'top'), size)

  def update(self, passed_time):
    pass

class MovingObstacle(Obstacle):
  def __init__(self, g_expl, pos, *groups):
    Obstacle.__init__(self, g_expl, pos, *groups)

    #self.mover = RandomMover([pos[0], pos[1]], {})
    #self.mover = ZigZagMover([pos[0], pos[1]], 1, {})
    #self.mover = CircularMover([pos[0], pos[1]], 1, {})
    #self.mover = LinearMover([pos[0], pos[1]], 1, {})
      # without speed adjustment to use pixels per second
    self.mover = LinearMover([pos[0], pos[1]], 60, {})

  def update(self, passed_time):
    self._update_position(passed_time)
