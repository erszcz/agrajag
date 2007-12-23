#!/usr/bin/python
#coding: utf-8

import os, sys, random
import pygame
from profilehooks import profile

from dbmanager import DBManager
from gfxmanager import GfxManager
from stagemanager import StageManager
from groupmanager import GroupManager
from spaceship import PlayerShip, EnemyShip, \
    EnemyInterceptor, RechargeBonus
from background import SpaceBackground, BackgroundImage
from obstacle import Obstacle, MovingObstacle
import mover
from clock import Clock
from hud import Hud

import psyco

def run():
  pygame.init()
  random.seed()
  
  display_size = 800, 600
  viewport_size = display_size[0], 600
  black = 0, 0, 0
  red = 255, 70, 70
  green = 70, 255, 70
  blue = 70, 70, 255
  white = 255, 255, 255

  l_green = 50, 255, 0

  screen = pygame.display.set_mode(display_size)
  screen.fill(black)

  clock = Clock(readonly = False)

  dbman = DBManager()
  dbman.import_db('./db')

  gfxman = GfxManager()
  gfxman.import_gfx(dbman.get(), './gfx')

  stagemanager = StageManager()
  stagemanager.import_stages('./stages')
  stages = stagemanager.get()

  groupmanager = GroupManager()

  g_draw = groupmanager.add('draw', 'OrderedUpdates')
  g_ship = groupmanager.add('ship')
  g_enemies = groupmanager.add('enemies')
  g_enemy_projectiles = groupmanager.add('enemy_projectiles')
  g_player_projectiles = groupmanager.add('player_projectiles')
  g_beams = groupmanager.add('beams')
  g_explosions = groupmanager.add('explosions')
  g_shields = groupmanager.add('shields')
  g_bonuses = groupmanager.add('bonuses')

  hud = Hud(viewport_size)

  g_enemies.add(Obstacle((60, 30)))
  g_enemies.add(MovingObstacle((160, 80)))

  g_bonuses.add(RechargeBonus((300, 200)))

  #ship = PlayerShip((175, viewport_size[1] - 60), g_ship)
  #hud.setup_connections(ship)
  PlayerShip((175, viewport_size[1] - 60), g_ship)
  hud.setup_connections(g_ship.sprites()[0])

  back = SpaceBackground(viewport_size)
  g_bimg = pygame.sprite.Group()

  for stage_name in stages:
    stage_clock = 0
    while True:
      for spawn_time in stages[stage_name]['spawn']:
        if spawn_time <= stage_clock:
          while stages[stage_name]['spawn'][spawn_time]:
            spawn = stages[stage_name]['spawn'][spawn_time].pop()
            pos = spawn['x'], spawn['y']

            object_cls = eval(spawn['object_cls_name'])
            object = object_cls(pos)

            if spawn['mover_cls_name']:
              mover_cls = eval("mover.%s" % spawn['mover_cls_name'])
              m = mover_cls(pos, object.max_speed, spawn['mover_params'])
              object.mover = m

            for g in spawn['groups']:
              if g == 'enemies':
                g_enemies.add(object)
              elif g == 'explosions':
                g_explosions.add(object)
              elif g == 'enemy_projectiles':
                g_enemy_projectiles.add(object)
              elif g == 'player_projectiles':
                g_player_projectiles.add(object)

      # time management
      clock.tick(40)
      #print clock.get_fps()
      stage_clock += clock.get_rawtime()

      for event in pygame.event.get():
        if   event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
          if   event.key == pygame.K_q: sys.exit()
          #elif event.key == pygame.K_s: ship.next_weapon()
          #elif event.key == pygame.K_a: ship.previous_weapon()
          #elif event.key == pygame.K_x: ship.activate_shield(True)
          elif event.key == pygame.K_s:
            if g_ship.sprites():
              g_ship.sprites()[0].next_weapon()
          elif event.key == pygame.K_a:
            if g_ship.sprites():
              g_ship.sprites()[0].previous_weapon()
          elif event.key == pygame.K_x:
            if g_ship.sprites():
              g_ship.sprites()[0].activate_shield(True)
        elif event.type == pygame.KEYUP:
          #if   event.key == pygame.K_UP: ship.fly_up(False)
          #elif event.key == pygame.K_x: ship.activate_shield(False)
          if   event.key == pygame.K_UP:
            if g_ship.sprites():
              g_ship.sprites()[0].fly_up(False)
          elif event.key == pygame.K_x:
            if g_ship.sprites():
              g_ship.sprites()[0].activate_shield(False)
    
      pressed_keys = pygame.key.get_pressed()
      #if pressed_keys[pygame.K_UP]: ship.fly_up(True)
      #if pressed_keys[pygame.K_DOWN]: ship.fly_down(viewport_size[1])
      #if pressed_keys[pygame.K_LEFT]: ship.fly_left()
      #if pressed_keys[pygame.K_RIGHT]: ship.fly_right(viewport_size[0])
      #if pressed_keys[pygame.K_z]: ship.shoot(g_bullets, g_explosions)
      if pressed_keys[pygame.K_UP]:
        if g_ship.sprites():
          g_ship.sprites()[0].fly_up(True)
      if pressed_keys[pygame.K_DOWN]:
        if g_ship.sprites():
          g_ship.sprites()[0].fly_down(viewport_size[1])
      if pressed_keys[pygame.K_LEFT]:
        if g_ship.sprites():
          g_ship.sprites()[0].fly_left()
      if pressed_keys[pygame.K_RIGHT]:
        if g_ship.sprites():
          g_ship.sprites()[0].fly_right(viewport_size[0])
      if pressed_keys[pygame.K_z]: 
        if g_ship.sprites():
          g_ship.sprites()[0].shoot()

      back.clear(screen, clear_bg)
      back.update()
      back.draw(screen)
#      g_bimg.update()
#      g_bimg.draw(screen)

      # temp
      #if g_ship.sprites():
      #  g_ship.sprites()[0].damage(1)
      #

      g_draw.clear(screen, clear_bg)
      hud.clear(screen, clear_bg)

      g_draw.update()
      hud.update()

      g_draw.draw(screen)
      hud.draw(screen)

      pygame.display.flip()
      #print g_ship.sprites()
      #if g_ship.sprites():
        #print sys.getrefcount(g_ship.sprites()[0])


def clear_bg(surf, rect):
  surf.fill((0, 0, 0), rect)


if __name__ == '__main__':
  run()
