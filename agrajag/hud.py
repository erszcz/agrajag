#!/usr/bin/env python
#coding: utf-8

import pygame

from widgets import VerticalProgressBar

class Hud:
  def __init__(self, viewport_size):
    self.vps = viewport_size

    self.g_hud = pygame.sprite.Group()

    self.label_font = pygame.font.Font('HookedUp.ttf', 20)
    self.l_shield = self.label_font.render('s', True, (255, 255, 255))
    self.pb_shield = VerticalProgressBar(0, 100, (4, 6),
      (self.vps[1] - 2*6 - self.label_font.size('s')[1]),
                                         self.g_hud)
    self.pb_shield.color = 'blue'
    # temp
    self.pb_shield.set_val(100)


    #self.screen = 
      # Think out some elegant way of getting the screen here.
      # Or, maybe, it won't be necessary?

  def update(self):
    self.g_hud.update()

  def draw(self, screen):
    screen.blit(self.l_shield,
                (4, self.vps[1] - 6 - self.label_font.size('s')[1]))
    self.g_hud.draw(screen)

  # temp
  def setup_connections(self, ship):
    ship.shield_updated.connect(self.pb_shield.set_val)
    ship.shield_updated.connect(self.zxc)

  def zxc(self, a):
    print 'Current shield level:', a
    print 'Shield level passed by signal:', a
