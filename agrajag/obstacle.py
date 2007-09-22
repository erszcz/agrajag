#!/usr/bin/python
#coding: utf-8

import pygame

class Obstacle(pygame.sprite.Sprite):
  def __init__(self, gfxman, pos, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)
    
    self.gfxman = gfxman
    self.image = self.gfxman['obstacle']
    self.rect = pygame.Rect(pos, (self.image.get_width(),
                                  self.image.get_height()))

  def update(self):
    pass
