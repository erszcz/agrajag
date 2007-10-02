#!/usr/bin/python
#coding: utf-8

import pygame
import random
from spaceship import AGSprite
from mover import RandomMover, ZigZagMover, CircularMover
# temp
from spaceship import EnergyProjectileExplosion

class Destructible(AGSprite):
  """
  Class describing an object that can be destroyed.

  An object of this class is destructible: it has got a specified
  durability and C{damage} and C{explode} methods.

  @type g_expl: C{pygame.sprite.Group}
  @ivar g_expl: Group of independent objects (C{pygame.sprite.Sprite})
      (which perish in time) such as explosions, salvage, etc.
  
  @type durability: integer
  @ivar durability: Object's durability. It describes how much damage the
      object can sustain before blowing up.
  """
  def __init__(self, g_expl, pos, *groups):
    """
    @type  g_expl: C{pygame.sprite.Group}
    @param g_expl: Group of independent objects (C{pygame.sprite.Sprite})
        (which perish in time) such as explosions, salvage, etc.
  
    @type  durability: integer
    @param durability: Object's durability. It describes how much damage
        the object can sustain before blowing up.
    """
    AGSprite.__init__(self, pos, *groups)
    self.g_expl = g_expl
    self.durability = self.cfg['durability']

  def damage(self, damage):
    """
    Deal damage and check whether the object ceases to exist. If so, call
    L{C{explode}}.

    @type  damage: integer
    @param damage: Amount of damage the object takes.
    """
    self.durability -= damage
    if self.durability <= 0:
      self.explode()

  def explode(self):
    """Blow the object up and cease its existence."""
    # temp
    self.g_expl.add( EnergyProjectileExplosion(self.rect.center) )
    #
    self.kill()
    del self

class Obstacle(Destructible):
  def __init__(self, g_expl, pos, *groups):
    #AGSprite.__init__(self, pos, *groups)
    Destructible.__init__(self, g_expl, pos, *groups)
    
    size = self.gfx['obstacle']['w'], self.gfx['obstacle']['h']
    
    self.rect = pygame.Rect(pos, size)
    self.image = pygame.Surface(size)
    self.blit_state('obstacle', 'def')

  def update(self):
    pass

class MovingObstacle(Obstacle):
  def __init__(self, g_expl, pos, *groups):
    Obstacle.__init__(self, g_expl, pos, *groups)

   # self.mover = RandomMover([pos[0], pos[1]], 1)
   # self.mover = ZigZagMover([pos[0], pos[1]], 1, 10)
    self.mover = CircularMover([pos[0], pos[1]], 1, 60)

  def update(self):
    self.update_position()
