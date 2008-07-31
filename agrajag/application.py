#!/usr/bin/env python
#coding: utf-8

'''
Main Agrajag application class with helper classes.

@type _here: C{str}
@var  _here: Module pathname base directory. 
  Equivalent to C{__FILE__} stripped of module filename.
  NOT INTENDED to use outside the module.

@type _gfx: C{str}
@var  _gfx: Dynamically created from C{L{_here}} pathname to directory
  with game graphics.

@type _db: C{str}
@var  _db: Dynamically created from C{L{_here}} pathname to XML data files.

@type _stg: C{str}
@var  _stg: Dynamically created from C{L{_here}} pathname to XML files
  describing game levels.

@type app: C{L{AGApplication}}
@var  app: Globally accessible reference to the singleton C{L{AGApplication}}
  instance. Intended to supply information such as screen size, etc. in various
  places throughout the program where it wouldn't be accessible otherwise.
'''

import os
import sys

import pygame
from pygame.color import Color
import random

import clock
import dbmanager as dbm
import gfxmanager as gfxm
import stagemanager as stgm
import groupmanager as grpm
import hud

import spaceship
import mover

# temp
import weakref
import background
#

_here = os.path.dirname(__file__)
_gfx  = os.path.join(_here, './gfx')
_db   = os.path.join(_here, './db')
_stg  = os.path.join(_here, './stages')

app = None


class AGApplication(object):
  '''Main Agrajag application class.
     Runs the entire game.

     @type fps: C{int}
     @ivar fps: Game target framerate.

     @type fullscreen: C{bool}
     @ivar fullscreen: Flag determining whether to run fullscreen.

     @type screen: C{pygame.Surface}
     @ivar screen: Main game display screen.

     @type screen_size: sequence of two C{int}s
     @ivar screen_size: Dimensions of the window or fullscreen resolution.

     @type title: C{unicode}
     @ivar title: Window title.

     @type short_title: C{unicode}
     @ivar short_title: Shorter title version used by some window managers.

     @type clock: C{L{clock.Clock}}
     @ivar clock: Main game clock instance (only instance allowed to C{tick}).
  '''
  __instance = None

  @classmethod
  def singleton(cls, **kwargs):
    '''Get the singleton instance (with instantiating it if needed).
    '''
    if not cls.__instance:
      cls.__instance = cls(**kwargs)
    return cls.__instance

  def __init__(self, size=(800, 600), fps=40, fullscreen=False):
    '''Initialize the singleton or raise exception if its instance exists.
       Do NOT call this method manually, use AGApplication.singleton instead.
    '''
    global app

    if AGApplication.__instance:
      raise Exception('singleton instance exists')

    pygame.init()
    random.seed()

    self.screen_size = size
    self.fps = fps
    self.fullscreen = fullscreen

    if self.fullscreen:
      self.screen = pygame.display.set_mode(self.screen_size,
                                            pygame.constants.FULLSCREEN)
    else:
      self.screen = pygame.display.set_mode(self.screen_size)
    self.screen.fill(Color('black'))

    self.title = 'Agrajag, 2d shooter game'
    self.short_title = 'Agrajag'
    pygame.display.set_caption(self.title, self.short_title)

    self.clock = clock.Clock(readonly = False)

    self.__init_managers()

    app = AGApplication.__instance = self

  def _screen_width(self): return self.screen_size[0]
  screen_width = property(_screen_width)

  def _screen_height(self): return self.screen_size[1]
  screen_height = property(_screen_height)

  def main(self):
    '''Run Agrajag application.'''
    while True:
      menu_choice = AGMenu.run()
      if menu_choice == PLAY:
        self.run_level()
      elif menu_choice == HISCORES:
        self.show_hiscores()
      elif menu_choice == EXIT:
        break
      else:
        raise Exception('unknown menu option')

  def run_level(self):
    '''Start a game level.
    '''
    AGLevel.run()

  def show_hiscores(self):
    '''Display the hiscore table.
    '''
    raise NotImplementedError('AGApplication.show_hiscores')

  def __init_managers(self):
    self.dbm = dbm.DBManager()
    self.dbm.import_db(_db)

    self.gfxm = gfxm.GfxManager()
    self.gfxm.import_gfx(self.dbm.get(), _gfx)

    self.stgm = stgm.StageManager()
    self.stgm.import_stages(_stg)

    self.grpm = grpm.GroupManager()
    self.grpm.add('draw', 'OrderedUpdates')
    self.grpm.add('ship')
    self.grpm.add('enemies')
    self.grpm.add('enemy_projectiles')
    self.grpm.add('player_projectiles')
    self.grpm.add('beams')
    self.grpm.add('explosions')
    self.grpm.add('shields')
    self.grpm.add('bonuses')


class AGMenu(object):
  '''Main Agrajag game menu.
  '''
  
  def __init__(self, screen):
    raise NotImplementedError('AGMenu.__init__')

  def __run(self):
    '''Start the menu loop.
    '''
    raise NotImplementedError('AGMenu.__run')
  
  @staticmethod
  def run():
    '''Run the menu and return option selected by the user.
    '''
    raise NotImplementedError('AGMenu.run')


class AGLevel(object):
  '''Agrajag level object.

     @type hud: C{L{hud.Hud}}
     @ivar hud: In-level head-up display.

     @type last_played: C{unicode}
     @cvar last_played: Name of the level that was played last.
  '''

  last_played = None

  def __init__(self, name):
    self.name = name

    self.stgm = stgm.StageManager()

    self.grpm = grpm.GroupManager()
    self.grpm.add('draw', 'OrderedUpdates')
    self.grpm.add('ship')
    self.grpm.add('enemies')
    self.grpm.add('enemy_projectiles')
    self.grpm.add('player_projectiles')
    self.grpm.add('beams')
    self.grpm.add('explosions')
    self.grpm.add('shields')
    self.grpm.add('bonuses')

    self.stage_clock = 0

    self.hud = hud.Hud(app.screen_size)

  def __run(self):
    '''Start the level loop.
    '''
    stages = self.stgm.get()

    g_draw       = self.grpm.get('draw')
    g_ship       = self.grpm.get('ship')
    g_enemies    = self.grpm.get('enemies')
    g_beams      = self.grpm.get('beams')
    g_explosions = self.grpm.get('explosions')
    g_shields    = self.grpm.get('shields')
    g_bonuses    = self.grpm.get('bonuses')
    g_enemy_projectiles  = self.grpm.get('enemy_projectiles')
    g_player_projectiles = self.grpm.get('player_projectiles')

    clear_bg = lambda surf, rect: surf.fill((0, 0, 0), rect)

    # temp
    ship = weakref.ref( spaceship.PlayerShip((175, app.screen_size[1] - 60),
                                             g_ship) )
    self.hud.setup_connections(ship())
    back = background.SpaceBackground(app.screen_size)
    #

    running = True
    while True:
      for spawn_time in stages[self.name]['spawn']:
        if spawn_time <= self.stage_clock:
          while stages[self.name]['spawn'][spawn_time]:
            spawn = stages[self.name]['spawn'][spawn_time].pop()
            pos = spawn['x'], spawn['y']

            object_cls = eval('spaceship.' + spawn['object_cls_name'])
            if spawn['object_base_cls_name']:
              if spawn['object_base_cls_name'] == 'Projectile':
                if not spawn.has_key('object_params'):
                  raise ValueError, "Params for projectile '%s' in stage %s \
                      not set" % (spawn['object_cls_name'], self.name)

                if not spawn['object_params'].has_key('dir'):
                  raise ValueError, "Invalid 'dir' for projectile '%s' in \
                      stage %s" % (spawn['object_cls_name'], self.name)

                if not spawn['object_params'].has_key('collision_group'):
                  raise ValueError, "Invalid 'collision_group' for projectile \
                      '%s' in stage %s" % (spawn['object_cls_name'], self.name)

                params = spawn['object_params']

                dir = params['dir']
                g_coll = groupmanager.get(params['collision_group'])
                object = object_cls(pos, dir, g_coll)

              elif spawn['object_base_cls_name'] == 'Bonus':
                pass
              else:
                raise ValueError, "Invalid value '%s' for attrubite \
                    'object_base_cls_name' in stage %s" % \
                    (spawn['object_base_cls_name'], self.name)
            else:
                object = object_cls(pos)

            if spawn['bonus_cls_name']:
              if isinstance(object, spaceship.BonusHolder):
                object.set_bonus(spawn['bonus_cls_name'], spawn['bonus_params'])
              else:
                raise ValueError, "Instances of %s can not hold bonuses." \
                    % object.__class__.__name__

            if spawn['mover_cls_name']:
              mover_cls = eval("mover.%s" % spawn['mover_cls_name'])
              m = mover_cls(pos, object.max_speed, spawn['mover_params'])
              object.set_mover(m)

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
      app.clock.tick(40)
      self.stage_clock += app.clock.get_time()

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
        if ship(): ship().fly_down(app.screen_size[1])
      if pressed_keys[pygame.K_LEFT]:
        if ship(): ship().fly_left()
      if pressed_keys[pygame.K_RIGHT]:
        if ship(): ship().fly_right(app.screen_size[0])
      if pressed_keys[pygame.K_z]:
        if ship(): ship().shoot()

      back.clear(app.screen, clear_bg)
      back.update()
      back.draw(app.screen)

      g_draw.clear(app.screen, clear_bg)
      self.hud.clear(app.screen, clear_bg)

      g_draw.update()
      self.hud.update()

      g_draw.draw(app.screen)
      self.hud.draw(app.screen)

      pygame.display.update()

  @staticmethod
  def run(name=None):
    '''Run next unplayed level or the level specified by C{level} parameter.
    '''
    if not name:
      stgman = stgm.StageManager()
      stages = sorted(stgman.get())
      if AGLevel.last_played:
        name = ''
        stage_iter = stages.__iter__()
        while name != AGLevel.last_played:
          name = stage_iter.next()
        name = stage_iter.next()
      else:
        name = stages[0]

      level = AGLevel(name)
      level.__run()


if __name__ == '__main__':
  agrajag = AGApplication.singleton()
  agrajag.run_level()
