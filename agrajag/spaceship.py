#!/usr/bin/python
#coding: utf-8

import pygame, math
from dbmanager import DBManager
from gfxmanager import GfxManager

from functions import deg2rad

class AGSprite(pygame.sprite.Sprite):
  '''
  Abstract sprite class used as a parent class for more specific classes
  like Ship, Projectile or Obstacle.
  
  @type gfx: dict
  @ivar gfx: The graphics resources provided by L{GfxManager}.

  @type mover: None or class derived from C{Mover}
  @ivar mover: Object responsible for controlling sprite movement.

  @type speed: integer
  @ivar speed: Value of speed (current) of game object in px.

  @type dir: float
  @ivar dir: Angle determining movement direction in degrees.
  '''

  max_speed = 0

  def __init__(self, pos, *groups):
    '''
    @type  pos: pair of integers
    @param pos: Initial position of the object. This pair defines
    the top-left corner of the object's rectangle C{rect}.
    '''

    pygame.sprite.Sprite.__init__(self, *groups)

    self.cfg = self.check_cfg(DBManager().get(self.__class__.__name__))['props']
    self.gfx = GfxManager().get(self.__class__.__name__)
    self.__configure()

    self.rect = pygame.Rect(pos, (0, 0))

    self.mover = None

  def __configure(self):
    if self.cfg.has_key('max_speed'):
      self.max_speed = self.cfg['max_speed']

  def check_cfg(self, cfg):
    '''Check whether provided config object contains all required
    information and whether this information is valid'''
    return cfg
 
  def blit_state(self, image, state, pos = (0, 0)):
    '''Blit selected image state aquired from GfxManager on image
    representing current instance'''

    area = self.gfx[image]['states'][state]['x_off'], \
           self.gfx[image]['states'][state]['y_off'], \
           self.gfx[image]['w'], \
           self.gfx[image]['h']
    self.image.blit(self.gfx[image]['image'], pos, area)

  def update_position(self):
    if self.mover is not None:
      self.rect.topleft = self.mover.update()

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

  @type explosion_cls_name: string
  @ivar explosion_cls_name: Name of the class that should be instantiated
      when object blows up. It is assumed that its constructor takes 
      one standard argument - position of the explosion.
  """

  durability = 0
  explosion_cls_name = None

  def __init__(self, g_expl, pos, *groups):
    """
    @type  g_expl: C{pygame.sprite.Group}
    @param g_expl: Group of independent objects (C{pygame.sprite.Sprite})
        (which perish in time) such as explosions, salvage, etc.
    """

    AGSprite.__init__(self, pos, *groups)
    self.__configure()

    self.g_expl = g_expl

  def __configure(self):
    props = ['durability', 'explosion_cls_name']
    for p in props:
      if self.cfg.has_key(p):
        setattr(self, p, self.cfg[p])

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

    if self.explosion_cls_name is not None:
      explosion_cls = eval(self.explosion_cls_name)
      explosion = explosion_cls(self.rect.center)

      self.g_expl.add( explosion )

    self.kill()
    del self

class Ship(Destructible):
  '''
  Base class for player's ship and enemy ships.
  
  @type g_coll: C{pygame.sprite.Group}
  @ivar g_coll: Group of objects (C{pygame.sprite.Sprite}) the ship can
      collide with.

  @type g_expl: C{pygame.sprite.Group}
  @ivar g_expl: Group of independent objects (C{pygame.sprite.Sprite})
      such as explosions, salvage, etc.

  @type rect: C{pygame.Rect}
  @ivar rect: Rectangle describing position and size of the ship.
  '''

  def __init__(self, g_coll, g_expl, pos, *groups):
    '''
    @type  g_coll: C{pygame.sprite.Group}
    @param g_coll: Group of objects (C{pygame.sprite.Sprite}) the ship
        can collide with.

    @type  g_expl: C{pygame.sprite.Group}
    @param g_expl: Group of independent objects (C{pygame.sprite.Sprite})
        (which perish in time) such as explosions, salvage, etc.

    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines the top-left
        corner of the ship's rectangle C{rect}.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    '''

    Destructible.__init__(self, g_expl, pos, *groups)
    
    self.g_coll = g_coll


class PlayerShip(Ship):
  """
  Represents the player's ship (not necessarily a spaceship).

  @type speed: integer
  @ivar speed: Speed of the ship (in both x and y axes).

  @type weapons: sequence
  @ivar weapons: A sequence of weapons available on the ship.

  @type cw: integer
  @ivar cw: Index of the sequence C{L{weapons}} which designates the
      currently used weapon.

  @type cooldown: unsigned integer
  @ivar cooldown: Number of rounds that have to pass before the weapon/s
      can be fired again.
  """

  def __init__(self, g_coll, g_expl, pos, *groups):
    """
    @type  g_coll: C{pygame.sprite.Group}
    @param g_coll: Group of objects (C{pygame.sprite.Sprite}) the ship
        can collide with.

    @type  g_expl: C{pygame.sprite.Group}
    @param g_expl: Group of independent (which perish in time) objects
        (C{pygame.sprite.Sprite}) such as explosions, salvage, etc.

    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines the top-left
        corner of the ship's rectangle C{rect}.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """

    Ship.__init__(self, g_coll, g_expl, pos, *groups)
    
    self.exhaust(False) # inits the image
    self.rect = pygame.Rect(pos, (self.image.get_width(),
                                  self.image.get_height()))
    self.speed = PlayerShip.max_speed

    self.weapons = (Bullet, EnergyProjectile, Shell)
    self.cw = 0 # current weapon list index
    self.cooldown = 0

  def check_cfg(self, cfg):
    req_gfx = ['ship', 'exhaust']
    req_prop = []

    for g in req_gfx:
      if not cfg['gfx'][g]:
        raise Exception("Required gfx resource '%s' not defined" % g);

    for p in req_prop:
      if not cfg[p]:
        raise Exception("Required property '%s' not defined" % p);

    return cfg

  def exhaust(self, on):
    """
    Change the image of the ship by adding or removing an engine
    exhaust at the bottom.
    """
    
    self.image = pygame.Surface((self.gfx['ship']['w'],
                                 self.gfx['ship']['h'] + 
                                 self.gfx['exhaust']['h']))

    self.image.fill((50, 250, 0))
    self.image.set_colorkey((50, 250, 0))

    state = 'on' if on else 'off'

    self.blit_state('ship', 'def')
    self.blit_state('exhaust',
                    state,
                    (self.gfx['ship']['w']/2 - self.gfx['exhaust']['w']/2,
                     self.gfx['ship']['h']))

  # moving
  def fly_up(self, on):
    """
    Either turn on the engine exhaust and move the ship up or turn it off.
    Both cases use C{L{exhaust}}.
    """
    if on:
      self.exhaust(True)
      if self.rect.top >= self.max_speed:
        self.rect.move_ip(0, -self.max_speed)
    else:
      self.exhaust(False)

  def fly_down(self, boundary):
    """
    Move the ship down.

    @type  boundary: unsigned integer
    @param boundary: Height of the viewport. Needed in order to check
        whether the ship may fly farther downwards.
    """

    if self.rect.top <= boundary - (self.rect.height + self.max_speed):
      self.rect.move_ip(0, self.max_speed)
      
  def fly_left(self):
    """
    Move the ship left.
    """
    if self.rect.left >= self.max_speed:
      self.rect.move_ip(-self.max_speed, 0)
  def fly_right(self, boundary):
    """
    Move the ship right.

    @type  boundary: unsigned integer
    @param boundary: Width of the viewport. Needed in order to check
        whether the ship may fly farther towards the right edge of the screen.
    """
    if self.rect.left <= boundary - (self.rect.width + self.max_speed):
      self.rect.move_ip(self.max_speed, 0)

  def shoot(self, g_projectiles):
    """
    Shoot the currently selected weapon. Appropriately
    increase C{L{cooldown}}.

    @type  g_projectiles: pygame.sprite.Group
    @param g_projectiles: Group to add the newly created projectiles to.
    """
    if not self.cooldown:
      cls = self.weapons[self.cw]
      if cls in (Bullet, Shell):
        p1 = cls(self.g_coll, self.g_expl,
                 (self.rect.centerx + 1 - cls.offset, self.rect.top)) 
        p2 = cls(self.g_coll, self.g_expl,
                 (self.rect.centerx + 1 + cls.offset, self.rect.top)) 

        g_projectiles.add(p1, p2)

        self.cooldown = p1.cooldown
      else:
        p = cls(self.g_coll, self.g_expl, (self.rect.centerx, self.rect.top))
        g_projectiles.add(p)

        self.cooldown = p.cooldown
    else:
      self.cooldown -= 1

  def next_weapon(self):
    """
    Select next weapon.
    """
    if self.cw == self.weapons.__len__() - 1:
      self.cw = 0
    else:
      self.cw += 1

  def previous_weapon(self):
    """
    Select previous weapon.
    """
    if self.cw == 0:
      self.cw = self.weapons.__len__() - 1
    else:
      self.cw -= 1

class EnemyShip(Ship):
  def __init__(self, g_coll, g_expl, pos, *groups):
    """
    @type  g_coll: C{pygame.sprite.Group}
    @param g_coll: Group of objects (C{pygame.sprite.Sprite}) the ship
        can collide with.

    @type  g_expl: C{pygame.sprite.Group}
    @param g_expl: Group of independent (which perish in time) objects
        (C{pygame.sprite.Sprite}) such as explosions, salvage, etc.

    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines the top-left
        corner of the ship's rectangle C{rect}.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """

    Ship.__init__(self, g_coll, g_expl, pos, *groups)
    
    self.image = pygame.Surface((self.gfx['ship']['w'], self.gfx['ship']['h']))
    self.image.set_colorkey((255, 137, 210))
    self.blit_state('ship', 'def')

    self.rect = pygame.Rect(pos, (self.gfx['ship']['w'], self.gfx['ship']['h']))
  pass


class Explosion(AGSprite):
  def __init__(self, pos, *groups):
    AGSprite.__init__(self, pos, *groups)

    self.full_time = self.time = float(self.cfg['animation_length'])
    self.frame = 0
    self.frame_count = float(self.cfg['frame_count'])
    self.frame_span = self.time / self.frame_count

  def update(self):
    if self.time == self.full_time - math.floor(self.frame * self.frame_span) and self.time != 0:
      self.blit_state('expl', 'frame' + str(self.frame))
      self.time -= 1
      self.frame += 1
    elif self.time <= 0:
      self.kill()
      del self
    else:
      self.time -= 1

class BulletExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    self.image = pygame.Surface((19, 19))
    self.image.set_colorkey((0, 138, 118))
    self.blit_state('expl', 'frame0')
    self.rect = pygame.Rect((0, 0), (19, 19))
    self.rect.center = pos[0] + 1, pos[1]

class ShellExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    self.image = pygame.Surface((10, 8))
    self.image.set_colorkey((191, 220, 191))
    self.blit_state('expl', 'frame0')
    self.rect = pygame.Rect((0, 0), (10, 8))
    self.rect.center = pos

class ObstacleExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((0, 138, 118))
    self.blit_state('expl', 'frame0')
    self.rect = pygame.Rect((0, 0), size)
    self.rect.center = pos

class EnergyProjectileExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    self.image = pygame.Surface((47, 47))
    self.blit_state('expl', 'frame4')
    self.image.set_colorkey((225, 255, 119))
    self.rect = pygame.Rect((0, 0), (47, 47))
    self.rect.center = pos

class Projectile(AGSprite):
  damage = 0
  cooldown = 0
  offset = 0

  def __init__(self, g_coll, g_expl, pos, *groups):
    AGSprite.__init__(self, pos, *groups)
 
    self.__configure()

    self.g_coll = g_coll
    self.g_expl = g_expl

    self.speed = self.max_speed

  def __configure(self):
    if self.cfg.has_key('damage'):
      self.damage = self.cfg['damage']

    if self.cfg.has_key('cooldown'):
      self.cooldown = self.cfg['cooldown']

  def update(self, dir_angle = None):
    if not dir_angle:
      self.rect.move_ip(0, -self.speed)
    else:
      self.rect.move_ip(self.speed * math.sin(deg2rad(dir_angle)),
                        self.speed * math.cos(deg2rad(dir_angle)))

    self.detect_collisions()
    if self.rect.top < 0:
      self.kill()
      del self

  def explode(self):
    self.kill()
    del self

  def detect_collisions(self):
    for sprite in self.g_coll.sprites():
      if sprite.rect.collidepoint(self.rect.centerx, self.rect.top):
        self.explode()
        sprite.damage(self.damage)


class Bullet(Projectile):
  offset = 6

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, pos, *groups)
    
    self.image = pygame.Surface((1, 2))
    self.image.set_colorkey((0, 0, 0))
    self.image.fill((255, 210, 0))
    self.rect = pygame.Rect(pos, (1, 2))

  def explode(self):
    self.g_expl.add( BulletExplosion(self.rect.center) )
    self.kill()
    del self

class Shell(Projectile):
  offset = 6

  def comp(x, y):
    if   x.rect.bottom > y.rect.bottom:
      return -1
    elif x.rect.bottom == y.rect.bottom:
      return 0
    else:
      return 1
  comp = staticmethod(comp)

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, pos, *groups)
    
    self.image = pygame.Surface((1, 1))
    self.image.fill((110, 110, 110))
    self.image.set_colorkey((110, 110, 110))
    self.rect = pygame.Rect((pos[0], 0), (1, pos[1]))
    self.ship_top = pos[1]

  def update(self):
    self.detect_collisions()

  def detect_collisions(self):
    l_gc = self.g_coll.sprites()
    l_gc.sort(cmp = Shell.comp)
    ind = self.rect.collidelist(l_gc)
    if ind != -1:
      if l_gc[ind].rect.bottom < self.ship_top:
        self.explode((self.rect.centerx, l_gc[ind].rect.bottom))
        #l_gc[ind].damage(Shell.damage)
        l_gc[ind].damage(self.damage)
      else:
        l_gc = l_gc[(ind + 1):]
        ind = self.rect.collidelist(l_gc)
        if ind != -1:
          self.explode((self.rect.centerx, l_gc[ind].rect.bottom))
          #l_gc[ind].damage(Shell.damage)
          l_gc[ind].damage(self.damage)

  def explode(self, pos):
    self.g_expl.add( ShellExplosion(pos) )
    self.kill()
    del self

class EnergyProjectile(Projectile):

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, pos, *groups)

    self.image = pygame.Surface((10, 10))
    self.image.set_colorkey((255, 0, 0))
    self.blit_state('energy', 'frame2')
    self.rect = pygame.Rect((0, 0), (10, 10))
    self.rect.centerx, self.rect.top = pos

    self.period = self.time = 16
    self.frame = 0
    self.frame_span = 4

  def update(self):
    if self.time == self.period - self.frame * self.frame_span and self.time != 0:
      self.blit_state('energy', 'frame' + str(self.frame))
      self.time -= 1
      self.frame += 1
    elif self.time == 0:
      self.time = self.period
      self.frame = 0
    else:
      self.time -= 1
    
    Projectile.update(self)

  def explode(self):
    self.g_expl.add( EnergyProjectileExplosion(self.rect.center) )
    self.kill()
    del self
