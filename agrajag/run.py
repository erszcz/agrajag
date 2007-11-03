#!/usr/bin/python
#coding: utf-8

import os, sys, random
import pygame

from dbmanager import DBManager
from gfxmanager import GfxManager
from stagemanager import StageManager
from groupmanager import GroupManager
from spaceship import PlayerShip, AdvancedPlayerShip, EnemyShip, \
    EnemyInterceptor
from background import SpaceBackground
from obstacle import Obstacle, MovingObstacle
import mover
from clock import Clock
from hud import Hud

from weakref import proxy, ref

import psyco

def run():
  pygame.init()
  random.seed()
  
  display_size = 800, 600
  viewport_size = display_size[0], 500
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

  g_ship = groupmanager.add('ship')
  g_enemies = groupmanager.add('enemies')
  g_enemy_projectiles = groupmanager.add('enemy_projectiles')
  g_player_projectiles = groupmanager.add('player_projectiles')
  g_beams = groupmanager.add('beams')
  g_explosions = groupmanager.add('explosions')
  g_shields = groupmanager.add('shields')

  hud = Hud(viewport_size)

  g_enemies.add(Obstacle((60, 30)))
  g_enemies.add(MovingObstacle((160, 80)))

  ship = ref( AdvancedPlayerShip((175, viewport_size[1] - 60), g_ship) )
  hud.setup_connections(ship())

  back = SpaceBackground(viewport_size)

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
      #clock.tick( float(sys.argv[1]) )
      stage_clock += clock.get_rawtime()

      for event in pygame.event.get():
        if   event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
          if   event.key == pygame.K_q: sys.exit()
          elif event.key == pygame.K_s:
            if ship(): ship().next_weapon()
          elif event.key == pygame.K_a:
            if ship(): ship().previous_weapon()
          elif event.key == pygame.K_x:
            if ship(): ship().activate_shield(True)
        elif event.type == pygame.KEYUP:
          if   event.key == pygame.K_UP:
            if ship(): ship().fly_up(False)
          elif event.key == pygame.K_x:
            if ship(): ship().activate_shield(False)
    
      pressed_keys = pygame.key.get_pressed()
      if pressed_keys[pygame.K_UP]:
        if ship(): ship().fly_up(True)
      if pressed_keys[pygame.K_DOWN]:
        if ship(): ship().fly_down(viewport_size[1])
      if pressed_keys[pygame.K_LEFT]:
        if ship(): ship().fly_left()
      if pressed_keys[pygame.K_RIGHT]:
        if ship(): ship().fly_right(viewport_size[0])
      if pressed_keys[pygame.K_z]:
        if ship(): ship().shoot()

      screen.fill(black)
      back.update()
      back.draw(screen)

      # temp
      #if ship():
      #  ship().damage(1)
      #

      g_enemies.update()
      g_beams.update()
      g_explosions.update()
      g_ship.update()
      g_enemy_projectiles.update()
      g_player_projectiles.update()
      g_shields.update()
      hud.update()

      g_enemies.draw(screen)
      g_ship.draw(screen)
      g_beams.draw(screen)
      g_enemy_projectiles.draw(screen)
      g_player_projectiles.draw(screen)
      g_shields.draw(screen)
      g_explosions.draw(screen)
      hud.draw(screen)

      screen.fill(red,
                  pygame.Rect((0, viewport_size[1]),
                              (display_size[0],
                               display_size[1] - viewport_size[1]))
                 )
      pygame.display.flip()
      #print g_ship.sprites()
      #if ship():
      #  print sys.getrefcount(ship())

if __name__ == '__main__':
  run()
