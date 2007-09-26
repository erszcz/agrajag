#!/usr/bin/python
#coding: utf-8

import pygame, math
from dbmanager import DBManager
from gfxmanager import GfxManager


class AGSprite(pygame.sprite.Sprite):
  '''
  Abstract sprite class used as a parent class for more specific classes like Spaceship, Enemy, Projectile or Obstacle
  
  @type gfxman: L{GFXManager}
  @ivar gfxman: The graphics manager, which takes care of different images
     used by in-game objects.

  '''

  def __init__(self, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)

    self.cfg = self.check_cfg(DBManager().get(self.__class__.__name__))['props']
    self.gfx = GfxManager().get(self.__class__.__name__)

  def check_cfg(self, cfg):
    '''Checks whether provided config object contains all required information and whether this information is valid'''
    return cfg
 
  def blit_state(self, image, state, pos = (0, 0)):
    '''Blits selected image state aquired from GfxManager on image representing current instance'''

    area = self.gfx[image]['states'][state]['x_off'], self.gfx[image]['states'][state]['y_off'], self.gfx[image]['w'], self.gfx[image]['h']
    self.image.blit(self.gfx[image]['image'], pos, area)

class Spaceship(AGSprite):
  """
  Represents the player's ship (not necessarily a spaceship).

  In near future this class should probably be split into a base class
  (e.g. C{Ship}) and a subclass (C{PlayerShip}).
  C{Ship} could be a parent class for both player and enemy ships.

  @type g_coll: C{pygame.sprite.Group}
  @ivar g_coll: Group of objects (C{pygame.sprite.Sprite}) the ship can
      collide with.

  @type g_expl: C{pygame.sprite.Group}
  @ivar g_expl: Group of independent objects (C{pygame.sprite.Sprite})
     such as explosions, salvage, etc.

  @type rect: C{pygame.Rect}
  @ivar rect: Rectangle describing position and size of the ship.

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

  def __init__(self, g_coll, g_expl, pos, speed, *groups):
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

    @type  speed: integer
    @param speed: Speed of the ship (in both x and y axes).

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """
    AGSprite.__init__(self, *groups)
    
    
    self.g_coll = g_coll
    self.g_expl = g_expl
    self.exhaust(False) # inits the image
    self.rect = pygame.Rect(pos, (self.image.get_width(),
                                  self.image.get_height()))
    self.speed = speed

    #self.weapon = 'bullets'

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
    Changes the image of the ship by adding or removing an engine exhaust at the bottom.
    """
    
    self.image = pygame.Surface((self.gfx['ship']['w'],
                                 self.gfx['ship']['h'] + self.gfx['exhaust']['h']))

    self.image.fill((50, 250, 0))
    self.image.set_colorkey((50, 250, 0))

    state = 'on' if on else 'off'

    self.blit_state('ship', 'def')
    self.blit_state('exhaust', state, (self.gfx['ship']['w']/2 - self.gfx['exhaust']['w']/2, self.gfx['ship']['h']))

  # moving
  def fly_up_start(self):
    """
    Turns on engine exhaust by calling C{L{exhaust(True)}} and
    moves the ship up.
    """
    self.exhaust(True)
    if self.rect.top >= self.speed:
      self.rect.move_ip(0, -self.speed)
  def fly_up_stop(self):
    """
    Turns off the engine exhaust (by calling C{L{exhaust(False)}}) when ship stops moving up.
    """
    self.exhaust(False)
  def fly_down(self, boundary):
    """
    Moves the ship down.

    @type  boundary: unsigned integer
    @param boundary: Height of the viewport. Needed in order to check
       whether the ship may fly farther downwards.
    """
    if self.rect.top <= boundary - (self.rect.height + self.speed):
      self.rect.move_ip(0, self.speed)
  def fly_left(self):
    """
    Moves the ship left.
    """
    if self.rect.left >= self.speed:
      self.rect.move_ip(-self.speed, 0)
  def fly_right(self, boundary):
    """
    Moves the ship right.

    @type  boundary: unsigned integer
    @param boundary: Width of the viewport. Needed in order to check
       whether the ship may fly farther towards the right edge of the screen.
    """
    if self.rect.left <= boundary - (self.rect.width + self.speed):
      self.rect.move_ip(self.speed, 0)

  def shoot(self, g_projectiles):
    """
    Shoots the currently selected weapon. Appropriately
    increases C{L{cooldown}}.

    @type  g_projectiles: pygame.sprite.Group
    @param g_projectiles: Group to add the newly created projectiles to.
    """
    if not self.cooldown:
      self.cooldown = self.weapons[self.cw].shoot(g_projectiles,
                                                  self.g_coll,
                                                  self.g_expl,
                                                  (self.rect.centerx + 1, self.rect.top))
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

class Explosion(AGSprite):
  def __init__(self, *groups):
    AGSprite.__init__(self, *groups)

    self.time = float(self.cfg['animation_length'])
    self.frame = 1
    self.frm_cnt = float(self.cfg['frame_count'])

  def update(self):
    if self.time == self.time - math.floor(self.frame * self.time / self.frm_cnt):
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
    Explosion.__init__(self, *groups)

    self.image = pygame.Surface((19, 19))
    self.image.set_colorkey((0, 138, 118))
    self.blit_state('expl', 'frame0')
    self.rect = pygame.Rect((0, 0), (19, 19))
    self.rect.center = pos[0] + 1, pos[1]

class ShellExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, *groups)

    self.image = pygame.Surface((10, 8))
    self.image.set_colorkey((191, 220, 191))
    self.blit_state('expl', 'frame0')
    self.rect = pygame.Rect((0, 0), (10, 8))
    self.rect.center = pos

class EnergyProjectileExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, *groups)

    self.image = pygame.Surface((19, 19))
    self.blit_state('expl', 'frame0')
    self.image.set_colorkey((0, 138, 118))
    self.rect = pygame.Rect((0, 0), (19, 19))
    self.rect.center = pos

class Projectile(AGSprite):
  damage = 0
  cooldown = 3
  offset = 0

  def __init__(self, g_coll, g_expl, *groups):
    AGSprite.__init__(self, *groups)

    self.g_coll = g_coll
    self.g_expl = g_expl

  def update(self, speed):
    self.rect.move_ip(0, speed)
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
        #sprite.damage(self.damage)

      #self.weapons[self.cw].shoot(g_projectiles,
      #                            self.g_coll,
      #                            self.g_expl,
      #                            self.gfxman,
      #                            (self.centerx, self.top))
  #      g_projectiles.add( Bullet(self.g_coll, self.g_expl, self.gfxman, (self.rect.left + 12, self.rect.top)) )
  def shoot(cls, g_proj, g_coll, g_expl, pos):
    if cls == Bullet or cls == Shell:
      g_proj.add( cls(g_coll, g_expl, (pos[0] - cls.offset, pos[1])) )
      g_proj.add( cls(g_coll, g_expl, (pos[0] + cls.offset, pos[1])) )
    else:
      g_proj.add( cls(g_coll, g_expl, pos) )
    return cls.cooldown
  shoot = classmethod(shoot)

class Bullet(Projectile):
  cooldown = 3
  offset = 6

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, *groups)
    
    self.image = pygame.Surface((1, 2))
    self.image.set_colorkey((0, 0, 0))
    self.image.fill((255, 210, 0))
    self.rect = pygame.Rect(pos, (1, 2))
    
  def update(self):
    Projectile.update(self, -11)

  def explode(self):
    self.g_expl.add( BulletExplosion(self.rect.center) )
    self.kill()
    del self

class Shell(Projectile):
  cooldown = 1
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
    Projectile.__init__(self, g_coll, g_expl, *groups)
    
    self.image = pygame.Surface((1, 1))
    self.image.fill((110, 110, 110))
    self.image.set_colorkey((110, 110, 110))
    #self.rect = pygame.Rect(pos, (1, 1))
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
        #l_gc[ind].damage()
      else:
        l_gc = l_gc[(ind + 1):]
        ind = self.rect.collidelist(l_gc)
        if ind != -1:
          self.explode((self.rect.centerx, l_gc[ind].rect.bottom))
          #l_gc[ind].damage()

  def explode(self, pos):
    self.g_expl.add( ShellExplosion(pos) )
    self.kill()
    del self

class EnergyProjectile(Projectile):
  cooldown = 5

  def __init__(self, g_coll, g_expl, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, *groups)

    self.image = pygame.Surface((10, 10))
    self.image.set_colorkey((255, 255, 255))
    self.blit_state('energy', 'a')
    self.rect = pygame.Rect((0, 0), (1, 1))
    self.rect.centerx, self.rect.top = pos[0] - 3, pos[1]
    self.rect.size = 10, 10

    self.stage = 0
    self.wait = 5

  def update(self):
    self.stage += 1
    self.stage %= 20

    if   self.stage in range(1, 5) and not self.wait:
      self.wait = 5
      self.image.fill((255, 255, 255))
      self.blit_state('energy', 'a')
    elif self.stage in range(6, 10) and not self.wait:
      self.wait = 5
      self.image.fill((255, 255, 255))
      self.blit_state('energy', 'b')
    elif self.stage in range(11, 15) and not self.wait:
      self.wait = 5
      self.image.fill((255, 255, 255))
      self.blit_state('energy', 'c')
    elif self.stage in range(16, 20) and not self.wait:
      self.wait = 5
      self.image.fill((255, 255, 255))
      self.blit_state('energy', 'd')
    else:
      self.wait -= 1
    
    Projectile.update(self, -self.cfg['speed'])

  def explode(self):
    self.g_expl.add( EnergyProjectileExplosion(self.rect.center) )
    self.kill()
    del self
