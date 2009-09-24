#!/usr/bin/env python
#coding: utf-8

import sys
import math
import pygame
from pygame.color import Color

from agrajag import eventmanager

event_type = {}
event_type['TICK'] = pygame.USEREVENT

class MySprite(pygame.sprite.Sprite):
  def __init__(self, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)

  def update(self):
    pass

  def handle(self, event):
    print event

class Character(MySprite):
  MOVE_ROTATE = 0x00001
  MOVE_UP     = 0x00010
  MOVE_DOWN   = 0x00100
  MOVE_LEFT   = 0x01000
  MOVE_RIGHT  = 0x10000
  MOVE_ANY    = MOVE_ROTATE | MOVE_UP | MOVE_DOWN | MOVE_LEFT | MOVE_RIGHT

  def __init__(self, *groups):
    MySprite.__init__(self, *groups)

    self._image = pygame.Surface([50, 50])
    pygame.draw.aalines(self._image, Color('white'), False, \
                        [(1, 48), (24, 1), (48, 48)])

    self.image = self._image.copy()
    self.rect = self.image.get_rect()
    self.rect.topleft = 200, 200

    self._move = self.MOVE_ROTATE
    self._aim_at = (0, 0)

  def register_for_events(self, evm):
    # evm - event manager
    evm.register(pygame.MOUSEMOTION, self)
    evm.register(pygame.KEYDOWN, self)
    evm.register(pygame.KEYUP, self)
    evm.register(event_type['TICK'], self)

  def update(self):
    ms = 7  # move speed
    if self._move & self.MOVE_UP:
      self.rect.move_ip(0, -ms)
    elif self._move & self.MOVE_DOWN:
      self.rect.move_ip(0,  ms)

    if self._move & self.MOVE_LEFT:
      self.rect.move_ip(-ms, 0)
    elif self._move & self.MOVE_RIGHT:
      self.rect.move_ip( ms, 0)

    if self._move & self.MOVE_ANY:
      p = self.rect.center
      q = self._aim_at
      rot = math.atan2(q[1] - p[1], q[0] - p[0])
      _image_rotation = 3 * math.pi / 2 - rot
      self.image = pygame.transform.rotate(self._image,
                     _image_rotation * 180 / math.pi)
      self.rect = self.image.get_rect()
      self.rect.center = p
  
  def handle(self, event):
    if event.type == pygame.MOUSEMOTION:
      self._aim_at = event.pos
    elif event.type == pygame.KEYDOWN:
      if   event.key == pygame.K_w: self._move |= self.MOVE_UP
      elif event.key == pygame.K_s: self._move |= self.MOVE_DOWN
      elif event.key == pygame.K_a: self._move |= self.MOVE_LEFT
      elif event.key == pygame.K_d: self._move |= self.MOVE_RIGHT

      elif event.key == pygame.K_u:
        self.evm.unregister(pygame.KEYDOWN, self)
    elif event.type == pygame.KEYUP:
      if   event.key == pygame.K_w: self._move ^= self.MOVE_UP
      elif event.key == pygame.K_s: self._move ^= self.MOVE_DOWN
      elif event.key == pygame.K_a: self._move ^= self.MOVE_LEFT
      elif event.key == pygame.K_d: self._move ^= self.MOVE_RIGHT

    elif event.type == event_type['TICK']:
      self.app.update_area.append(pygame.Rect(self.rect))
      self.screen.fill(Color('black'), self.rect)
      self.update()
      self.screen.blit(self.image, self.rect)
      self.app.update_area.append(pygame.Rect(self.rect))

class Application:
  def __init__(self):
    pygame.init()

    self.evm = eventmanager.EventManager()
    self.evm.register(pygame.KEYDOWN, self)

    self.clock = pygame.time.Clock()
    self.fps = 30

    self.screen = pygame.display.set_mode((800, 600))

    self.render = pygame.sprite.RenderUpdates()
    self.chara = Character(self.render)
    self.chara.register_for_events(self.evm)
    self.chara.screen = self.screen
    self.chara.app = self

  def handle(self, event):
    if event.key == pygame.K_ESCAPE: sys.exit()

  def run(self):
    '''Run the application.
    '''
    while True:
      self.update_area = []
      pygame.event.post(pygame.event.Event(event_type['TICK']))
      self.evm.process()

      pygame.display.update(self.update_area)

      self.clock.tick(self.fps)

if __name__ == '__main__':
  app = Application()
  for x in 2, 3, 4:
    print pygame.event.event_name(x)
  app.run()

