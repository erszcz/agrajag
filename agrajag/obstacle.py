#!/usr/bin/python
#coding: utf-8

import pygame
import random
from spaceship import AGSprite

class Obstacle(AGSprite):
  def __init__(self, pos, *groups):
    AGSprite.__init__(self, pos, *groups)
    
    size = self.gfx['obstacle']['w'], self.gfx['obstacle']['h']
    
    self.rect = pygame.Rect(pos, size)
    self.image = pygame.Surface(size)
    self.blit_state('obstacle', 'def')

  def update(self):
    pass


class MovingObstacle(Obstacle):
  period = 50      # czas przez jaki kierunek sie nie zmienia
  it     = 0       # licznik czasu    

  def __init__(self, pos, *groups):
    Obstacle.__init__(self, pos, *groups)

    self.speed  = 2
    self.dir    = random.randint(0, 359)

  def update(self):
    self.it += 1
    if self.it % self.period == 0:
      self.dir = random.randint(0, 359)

    self.update_position()
