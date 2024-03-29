#!/usr/bin/env python
#coding: utf-8

'''In-level heads-up display.
'''

import pygame
from pygame.color import Color

import application
import spaceship
import widgets

class Hud(object):
  def __init__(self):
    self.app = application.app
    screen_size = self.app.screen_size

    self.g_hud = pygame.sprite.Group()

    self.label_font = pygame.font.Font('fonts/HookedUp.ttf', 20)

    pbar_length = screen_size[1] - 2*6 - self.label_font.get_height()
      # height - 2*label_margin - label_height
    
    # shield indicator
    self.s_shield = pygame.sprite.Sprite(self.g_hud)
    self.s_shield.image = self.label_font.render('s', True, (255, 255, 255))
    self.s_shield.rect = pygame.Rect(
      (4, screen_size[1] - 6 - self.label_font.size('s')[1]),
      self.s_shield.image.get_size()
    )
    self.pb_shield = widgets.VerticalProgressBar((4, 2),
                                                 pbar_length,
                                                 self.g_hud)
    self.pb_shield.color = 'blue'
    self.pb_shield.set_val(0)
    
    # energy weapon indicator
    self.s_eweapon = pygame.sprite.Sprite(self.g_hud)
    self.s_eweapon.image = self.label_font.render('e', True, (255, 255, 255))
    self.s_eweapon.rect = pygame.Rect(
      (screen_size[0] - 11, screen_size[1] - 6 - self.label_font.size('s')[1]),
      self.s_eweapon.image.get_size()
    )
    self.pb_eweapon = widgets.VerticalProgressBar((screen_size[0] - 10, 2),
                                                  pbar_length, self.g_hud)
    self.pb_eweapon.color = 'red'
    self.pb_eweapon.val = 100

    # armour and ammo labels
    self.s_armour = pygame.sprite.Sprite(self.g_hud)
    self.s_armour.image = self.label_font.render('000', True, (255, 255, 255))
    self.s_armour.rect = pygame.Rect(
      (22, screen_size[1] - 6 - self.label_font.size('s')[1]),
      self.s_armour.image.get_size()
    )

    self.s_ammo = pygame.sprite.Sprite(self.g_hud)
    self.s_ammo.image = self.label_font.render('000', True, (255, 255, 255))
    self.s_ammo.rect = pygame.Rect(
      (screen_size[0] - 50, screen_size[1] - 6 - self.label_font.size('s')[1]),
      self.s_ammo.image.get_size()
    )

  def clear(self, screen, callback):
    self.g_hud.clear(screen, callback)

  def update(self):
    self.g_hud.update()

  def draw(self, screen):
    self.g_hud.draw(screen)

  def update_shield(self, shield):
    self.pb_shield.max = shield.maximum
    self.pb_shield.val = shield.current

  def update_armour(self, value):
    self.s_armour.image = self.label_font.render('%03d' % value, True,
                                                 Color('white'))

  def update_weapon(self, weapon):
    if isinstance(weapon, spaceship.EnergyWeapon):
      self.s_ammo.image = self.label_font.render(
                            '%02d%%' % (weapon.current * 100 / weapon.maximum),
                            True, Color('white'))
      self.pb_eweapon.max = weapon.maximum
      self.pb_eweapon.val = weapon.current
    elif isinstance(weapon, spaceship.AmmoWeapon):
      self.pb_eweapon.max = weapon.maximum
      self.pb_eweapon.val = weapon.current
      self.s_ammo.image = self.label_font.render('%03d' % weapon.current,
                                                 True, Color('white'))
