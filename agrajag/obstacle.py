#!/usr/bin/python
#coding: utf-8

import pygame
from spaceship import AGSprite

class Obstacle(AGSprite):
  def __init__(self, pos, *groups):
    AGSprite.__init__(self, *groups)
    
    size = self.gfx['obstacle']['w'], self.gfx['obstacle']['h']
    
    self.rect = pygame.Rect(pos, size)
    self.image = pygame.Surface(size)
    self.blit_state('obstacle', 'def')

  def update(self):
    pass
