#!/usr/bin/end python
#coding: utf-8

import sys
import new

import pygame
from pygame.color import Color

class Ship(pygame.sprite.Sprite):
  def __init__(self, proto_image, pos, *groups):
    pygame.sprite.Sprite.__init__(self, groups)

    self.proto_image = proto_image
    self.image = self.proto_image.copy()
    self.rect = pygame.Rect(pos[0], pos[1], self.image.get_width(),
                            self.image.get_height())
    self.angle = 0

#  def update(self):
#    old_center = self.rect.center
#
#    self.image = pygame.transform.rotate(self.proto_image, self.angle)
#    self.angle -= 2
#    self.angle %= 360
#
#    self.rect = pygame.Rect(self.rect.left, self.rect.top,
#                            self.image.get_width(),
#                            self.image.get_height())
#    self.rect.center = old_center

  def rotate(self, angle):
    old_center = self.rect.center

    self.image = pygame.transform.rotate(self.proto_image, self.angle)
    self.angle += angle
    self.angle %= 360

    self.rect = pygame.Rect(self.rect.left, self.rect.top,
                            self.image.get_width(),
                            self.image.get_height())
    self.rect.center = old_center

def rotating_ship_update(self):
  old_center = self.rect.center

  self.image = pygame.transform.rotate(self.proto_image, self.angle)
  self.angle -= 2
  self.angle %= 360

  self.rect = pygame.Rect(self.rect.left, self.rect.top,
                          self.image.get_width(),
                          self.image.get_height())
  self.rect.center = old_center
  
def get_screen(size=(640, 480)):
  '''Return a Pygame display window.
  '''
  return pygame.display.set_mode(size)

def main_image_rotation():
  '''Display and rotate a bitmap using pygame.transform.
  '''
  pygame.init()

  screen = get_screen((200, 200))

  img = pygame.image.load('../gfx/ship.png').convert_alpha()

  clock = pygame.time.Clock()

  angle = 0

  draw_group = pygame.sprite.Group()
  rotating_ship = Ship(img, (100, 20), draw_group)
  rotating_ship.update = new.instancemethod(rotating_ship_update,
                                            rotating_ship,
                                            Ship)
  moving_ship = Ship(img, (100, 100), draw_group)

  running = True
  paused = False
  while running:
    for event in pygame.event.get():
      if   event.type == pygame.QUIT: sys.exit()
      elif event.type == pygame.KEYDOWN:
        if   event.key == pygame.K_ESCAPE: running = not running
        elif event.key == pygame.K_p: paused = not paused

#        elif event.key == pygame.K_w:
#          moving_ship.rect.move_ip(0, -1)
#        elif event.key == pygame.K_s:
#          moving_ship.rect.move_ip(0, 1)
#        elif event.key == pygame.K_a:
#          moving_ship.rect.move_ip(-1, 0)
#        elif event.key == pygame.K_d:
#          moving_ship.rect.move_ip(1, 0)
#        elif event.key == pygame.K_q:
#          moving_ship.rotate(1)
#        elif event.key == pygame.K_e:
#          moving_ship.rotate(-1)

    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_w]:
      moving_ship.rect.move_ip(0, -3)
    if pressed_keys[pygame.K_s]:
      moving_ship.rect.move_ip(0, 3)
    if pressed_keys[pygame.K_a]:
      moving_ship.rect.move_ip(-3, 0)
    if pressed_keys[pygame.K_d]:
      moving_ship.rect.move_ip(3, 0)
    if pressed_keys[pygame.K_n]:
      moving_ship.rotate(3)
    if pressed_keys[pygame.K_m]:
      moving_ship.rotate(-3)

    if paused:
      clock.tick(25)
      continue

    screen.fill(Color('green'))
    screen.blit(img, (20, 20))
    screen.blit(pygame.transform.rotate(img, 45), (20, 100))

    draw_group.update()
    draw_group.draw(screen)

    pygame.draw.line(screen, Color('white'), (99, 0), (99, 200))
    pygame.draw.line(screen, Color('white'), (0, 20), (200, 20))

    pygame.display.update()

    clock.tick(25)

if __name__ == '__main__':
  print 'Press:\n\tW, S, A, D to move around\n\tN, M to rotate'
  main_image_rotation()
