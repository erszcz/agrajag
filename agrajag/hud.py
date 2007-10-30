#!/usr/bin/env python
#coding: utf-8

import pygame

from widgets import VerticalProgressBar

class Hud:
  def __init__(self, viewport_size):
    self.vps = viewport_size

    self.g_hud = pygame.sprite.Group()

    self.label_font = pygame.font.Font('HookedUp.ttf', 20)

    pbar_length = self.vps[1] - 2*6 - self.label_font.get_height()
      # height - 2*label_margin - label_height
    
    # shield indicator
    self.l_shield = self.label_font.render('s', True, (255, 255, 255))
    self.pb_shield = VerticalProgressBar((4, 2), pbar_length, self.g_hud)
    self.pb_shield.color = 'blue'
    self.pb_shield.set_val(0)
    
    # energy weapon indicator
    self.l_eweapon = self.label_font.render('e', True, (255, 255, 255))
    self.pb_eweapon = VerticalProgressBar((self.vps[0] - 10, 2),
                                          pbar_length, self.g_hud)
    self.pb_eweapon.color = 'red'
    self.pb_eweapon.val = 100


  def update(self):
    self.g_hud.update()


  def draw(self, screen):
    screen.blit(self.l_shield,
                (4, self.vps[1] - 6 - self.label_font.size('s')[1]))
    screen.blit(self.l_eweapon,
                (self.vps[0] - 11, self.vps[1] - 6 - self.label_font.size('s')[1]))
    self.g_hud.draw(screen)


  def slot_shield_updated(self, value, maximum):
    self.pb_shield.max = maximum
    self.pb_shield.val = value


  def slot_armour_updated(self, value):
    print "Armour HUD info updated. Value:", value


  def slot_weapon_updated(self, type, value, maximum = None):
    if type == 'energy':
      self.pb_eweapon.max = maximum
      self.pb_eweapon.val = value
    elif type == 'ammo':
      self.pb_eweapon.val = 0
      self.update()


  # temp
  def setup_connections(self, ship):
    ship.shield_updated.connect(self.slot_shield_updated)
    ship.armour_updated.connect(self.slot_armour_updated)
    ship.weapon_updated.connect(self.slot_weapon_updated)
