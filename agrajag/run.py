#!/usr/bin/python
#coding: utf-8

import os, sys, random
import pygame

from dbmanager import DBManager
from gfxmanager import GfxManager
from spaceship import Spaceship
from background import SpaceBackground
from obstacle import Obstacle

import psyco

def run():
  pygame.init()
  random.seed()
  
  display_size = 400, 600
  black = 0, 0, 0
  red = 255, 70, 70
  green = 70, 255, 70
  blue = 70, 70, 255
  white = 255, 255, 255

  l_green = 50, 255, 0

  screen = pygame.display.set_mode(display_size)
  screen.fill(black)

  clock = pygame.time.Clock()

  dbman = DBManager()
  dbman.import_db('./db')

  gfxman = GfxManager()
  gfxman.import_gfx(dbman.get(), './gfx')

  g_enemies = pygame.sprite.Group()
  g_enemies.add(Obstacle((60, 30)))
  g_enemies.add(Obstacle((160, 80)))

  g_explosions = pygame.sprite.Group()

  g_ship = pygame.sprite.Group()
  ship = Spaceship(g_enemies, g_explosions, (175, display_size[1] - 60), 8, g_ship)

  g_bullets = pygame.sprite.Group()

  back = SpaceBackground(display_size)

  play = True
  while play:
    for event in pygame.event.get():
      if   event.type == pygame.QUIT: sys.exit()
      elif event.type == pygame.KEYDOWN:
        if   event.key == pygame.K_q: sys.exit()
        elif event.key == pygame.K_s: ship.next_weapon()
        elif event.key == pygame.K_a: ship.previous_weapon()
      elif event.type == pygame.KEYUP:
        if   event.key == pygame.K_UP: ship.fly_up_stop()
    
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_UP]: ship.fly_up_start()
    if pressed_keys[pygame.K_DOWN]: ship.fly_down(display_size[1])
    if pressed_keys[pygame.K_LEFT]: ship.fly_left()
    if pressed_keys[pygame.K_RIGHT]: ship.fly_right(display_size[0])
    if pressed_keys[pygame.K_z]: ship.shoot(g_bullets)

    #clock.tick(40)
    clock.tick(60)
    #clock.tick(float(sys.argv[1]))

    screen.fill(black)
    back.update()
    back.draw(screen)
    g_enemies.update()
    g_enemies.draw(screen)
    g_explosions.update()
    g_explosions.draw(screen)
    g_ship.update()
    g_ship.draw(screen)
    g_bullets.update()
    g_bullets.draw(screen)
    pygame.display.flip()

if __name__ == '__main__':
  run()
