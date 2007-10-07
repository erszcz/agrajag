#!/usr/bin/python
#coding: utf-8

import pygame, math
from dbmanager import DBManager
from gfxmanager import GfxManager
import mover

from functions import deg2rad

class AGSprite(pygame.sprite.Sprite):
  '''
  Abstract sprite class used as a parent class for more specific classes
  like Ship, Projectile or Obstacle.
  
  @type cfg: dict
  @ivar cfg: Class configuration provided by L{C{DBManager}}.

  @type gfx: dict
  @ivar gfx: The graphics resources provided by L{C{GfxManager}}.

  @type mover: None or class derived from C{Mover}
  @ivar mover: Object responsible for controlling sprite movement.

  @type max_speed: integer
  @ivar max_speed: Maximal speed object can by moved with expressed in pixels per iteration.

  @type pos: tuple or list
  @ivar pos: Current position of arbitrary object's point.

  @type align: string or tuple
  @ivar align: Name or names of properties used to align object's C{rect} attribute.
  '''

  max_speed = 0

  def __init__(self, pos, *groups):
    '''
    @type  pos: pair of integers
    @param pos: Initial position of the object. This pair defines
    the top-left corner of the object's rectangle C{rect}.
    '''

    pygame.sprite.Sprite.__init__(self, *groups)

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self.gfx = GfxManager().get(self.__class__.__name__)
    self.__configure()

    self._initialize_position(pos, 'center', (0, 0))

    self.mover = None

  def __configure(self):
    if self.cfg.has_key('max_speed'):
      self.max_speed = self.cfg['max_speed']

  def _check_cfg(self, required_props):
    """
    Auxiliary function that may be used to check if object's C{cfg} attribute
    contains information on required properties. Properties with no default
    values defined on class level should always be checked.
    """

    for p in required_props:
      if not self.cfg[p]:
        raise Exception("Required property '%s' not defined" % p);

  def _check_gfx(self, required_resources):
    """
    Auxiliary function that may be used to check if object's C{gfx} attribute
    contains required graphics resources. Resources' states are not checked!
    """

    for r in required_resources:
      if not self.gfx[r]:
        raise Exception("Required gfx resource '%s' not defined" % g);

  def _blit_state(self, image, state, pos = (0, 0)):
    '''Blit selected image state aquired from GfxManager on image
    representing current instance'''

    area = self.gfx[image]['states'][state]['x_off'], \
           self.gfx[image]['states'][state]['y_off'], \
           self.gfx[image]['w'], \
           self.gfx[image]['h']
    self.image.blit(self.gfx[image]['image'], pos, area)

  def _initialize_position(self, pos, align, size):
    """
    Initializes object's C{rect} attribute which is required by pygame
    to render object's image. Also sets object's C{pos} and C{align}
    attributes.

    @type pos: tuple or list of two integers
    @param pos: position of arbitrary object's point

    @type align: tuple or list of two strings
    @param align: names of properties used to align object's C{rect}

    @type size: tuple
    @param size: object's size in pixels
    """

    self.pos = pos
    self.align = align
    self.rect = pygame.Rect((0, 0), size)

    if type(align) is tuple or type(align) is list:
      setattr(self.rect, align[0], pos[0])
      setattr(self.rect, align[1], pos[1])
    elif type(align) is str:
      setattr(self.rect, align, pos)
    else:
      raise Exception("Invalid align value")

  def _update_position(self):
    """
    Set new position of the object. New position is determined by
    object's C{mover} if object has one. If not position is not changed.
    Object's C{align} attribute is used to properly align object's C{rect}.
    """

    if self.mover is not None:
      self.pos = self.mover.update()

      if type(self.align) is tuple:
        setattr(self.rect, self.align[0], self.pos[0])
        setattr(self.rect, self.align[1], self.pos[1])
      elif type(self.align) is str:
        setattr(self.rect, self.align, self.pos)

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
    self._check_gfx(['ship', 'exhaust'])
    self._check_cfg(['max_speed'])

    size = self.gfx['ship']['w'], \
           self.gfx['ship']['h'] + self.gfx['exhaust']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((50, 250, 0))

    self._initialize_position(pos, ('centerx', 'top'), size)

    self.exhaust(False) # inits the image
    self.weapons = (Bullet, EnergyProjectile, Shell)
    self.cw = 0 # current weapon list index
    self.cooldown = 0

  def exhaust(self, on):
    """
    Change the image of the ship by adding or removing an engine
    exhaust at the bottom.
    """
    
    state = 'on' if on else 'off'

    self.image.fill((50, 250, 0))
    self._blit_state('ship', 'def')
    self._blit_state('exhaust',
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
        self.pos = self.pos[0], self.pos[1] - self.max_speed
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
      self.pos = self.pos[0], self.pos[1] + self.max_speed
      
  def fly_left(self):
    """
    Move the ship left.
    """

    if self.rect.left >= self.max_speed:
      self.rect.move_ip(-self.max_speed, 0)
      self.pos = self.pos[0] - self.max_speed, self.pos[1]

  def fly_right(self, boundary):
    """
    Move the ship right.

    @type  boundary: unsigned integer
    @param boundary: Width of the viewport. Needed in order to check
        whether the ship may fly farther towards the right edge of the screen.
    """

    if self.rect.left <= boundary - (self.rect.width + self.max_speed):
      self.rect.move_ip(self.max_speed, 0)
      self.pos = self.pos[0] + self.max_speed, self.pos[1]

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
                 (self.pos[0] - cls.offset, self.pos[1])) 
        p2 = cls(self.g_coll, self.g_expl,
                 (self.pos[0] + cls.offset, self.pos[1])) 

        g_projectiles.add(p1, p2)

        self.cooldown = p1.cooldown
      else:
        p = cls(self.g_coll, self.g_expl, self.pos)
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
 
    size = self.gfx['ship']['w'], self.gfx['ship']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((255, 137, 210))
    self._blit_state('ship', 'def')

    self._initialize_position(pos, ('centerx', 'bottom'), size)

  def update(self):
    self._update_position();

class Explosion(AGSprite):
  def __init__(self, pos, *groups):
    AGSprite.__init__(self, pos, *groups)

    self.full_time = self.time = float(self.cfg['animation_length'])
    self.frame = 0
    self.frame_count = float(self.cfg['frame_count'])
    self.frame_span = self.time / self.frame_count

  def update(self):
    if self.time == self.full_time - math.floor(self.frame * self.frame_span) and self.time != 0:
      self._blit_state('expl', 'frame' + str(self.frame))
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

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((0, 138, 118))
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, ('centerx', 'centery'), size)

class ShellExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((191, 220, 191))
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, 'center', size)

class ObstacleExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((0, 138, 118))
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, ('centerx', 'centery'), size)

class EnergyProjectileExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size)
    self._blit_state('expl', 'frame4')
    self.image.set_colorkey((225, 255, 119))

    self._initialize_position(pos, ('centerx', 'centery'), size)

class Projectile(AGSprite):
  damage = 0
  cooldown = 0
  offset = 0

  def __init__(self, g_coll, g_expl, pos, *groups):
    AGSprite.__init__(self, pos, *groups)
 
    self.__configure()

    self.g_coll = g_coll
    self.g_expl = g_expl

    self.mover = mover.LinearMover(pos, self.max_speed, 180)

  def __configure(self):
    if self.cfg.has_key('damage'):
      self.damage = self.cfg['damage']

    if self.cfg.has_key('cooldown'):
      self.cooldown = self.cfg['cooldown']

  def update(self):
    self._update_position();
    self._detect_collisions()
    if self.rect.top < 0:
      self.kill()
      del self

  def explode(self):
    self.kill()
    del self

  def _detect_collisions(self):
    for sprite in self.g_coll.sprites():
      if sprite.rect.collidepoint(self.rect.centerx, self.rect.top):
        self.explode()
        sprite.damage(self.damage)


class Bullet(Projectile):
  offset = 6

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, pos, *groups)
    
    size = 1, 2

    self.image = pygame.Surface(size)
    self.image.set_colorkey((0, 0, 0))
    self.image.fill((255, 210, 0))

    self._initialize_position(pos, 'center', size)

  def explode(self):
    self.g_expl.add( BulletExplosion(self.pos) )
    self.kill()
    del self

class Shell(Projectile):
  offset = 6

  @staticmethod
  def comp(x, y):
    if   x.rect.bottom > y.rect.bottom:
      return -1
    elif x.rect.bottom == y.rect.bottom:
      return 0
    else:
      return 1

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, pos, *groups)
    
    self.image = pygame.Surface((1, 1))
    self.image.fill((110, 110, 110))
    self.image.set_colorkey((110, 110, 110))

    self._initialize_position((pos[0], 0), ('left', 'top'), (1, pos[1]))

    self.ship_top = pos[1]

  def update(self):
    self._detect_collisions()

  def _detect_collisions(self):
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

    size = self.gfx['energy']['w'], self.gfx['energy']['h']

    self.image = pygame.Surface(size)
    self.image.set_colorkey((255, 0, 0))
    self._blit_state('energy', 'frame2')

    self._initialize_position(pos, ('centerx', 'top'), size)

    self.period = self.time = 16
    self.frame = 0
    self.frame_span = 4

  def update(self):
    if self.time == self.period - self.frame * self.frame_span and self.time != 0:
      self._blit_state('energy', 'frame' + str(self.frame))
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
