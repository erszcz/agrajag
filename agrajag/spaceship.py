#!/usr/bin/python
#coding: utf-8

import pygame


class AGSprite(pygame.sprite.Sprite):
  '''Abstract sprite class used as a parent class for more specific classes like Spaceship, Enemy, Projectile or Obstacle'''

  def __init__(self, conf, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)

    self.conf = self.check_conf(conf)

  def check_conf(self, conf):
    '''Checks whether provided config object contains all required information and whether this information is valid'''
    return conf
    

class Spaceship(pygame.sprite.Sprite):
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

  @type gfxman: L{GFXManager}
  @ivar gfxman: The graphics manager, which takes care of different images
     used by in-game objects.

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
  def __init__(self, g_coll, g_expl, gfxman, pos, speed, *groups):
    """
    @type  g_coll: C{pygame.sprite.Group}
    @param g_coll: Group of objects (C{pygame.sprite.Sprite}) the ship
       can collide with.

    @type  g_expl: C{pygame.sprite.Group}
    @param g_expl: Group of independent (which perish in time) objects
        (C{pygame.sprite.Sprite}) such as explosions, salvage, etc.
    @type  gfxman: L{GFXManager}
    @param gfxman: The graphics manager, which takes care of different
       images used by in-game objects.
    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines the top-left
        corner of the ship's rectangle C{rect}.
    @type  speed: integer
    @param speed: Speed of the ship (in both x and y axes).
    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """
    pygame.sprite.Sprite.__init__(self, *groups)
    
    self.g_coll = g_coll
    self.g_expl = g_expl
    self.gfxman = gfxman
    self.exhaust_off() # inits the image
    self.rect = pygame.Rect(pos, (self.image.get_width(),
                                  self.image.get_height()))
    self.speed = speed

    #self.weapon = 'bullets'

    self.weapons = (Bullet, EnergyProjectile, Shell)
    self.cw = 0 # current weapon list index
    self.cooldown = 0

  def exhaust_on(self):
    """
    Changes the image of the ship by adding an engine exhaust at the bottom.
    """
    self.image = pygame.Surface((self.gfxman['ship'].get_width(),
                                 self.gfxman['ship'].get_height() +
                                 self.gfxman['exhaust'].get_height()))
    self.image.fill((50, 250, 0))
    self.image.set_colorkey((50, 250, 0))
    self.image.blit(self.gfxman['ship'], (0, 0))
    self.image.blit(self.gfxman['exhaust'], (13, self.gfxman['ship'].get_height()))

  def exhaust_off(self):
    """
    Changes the image of the ship by removing the engine exhaust.
    """
    self.image = pygame.Surface((self.gfxman['ship'].get_width(),
                                 self.gfxman['ship'].get_height() +
                                 self.gfxman['exhaust2'].get_height()))
    self.image.fill((50, 250, 0))
    self.image.set_colorkey((50, 250, 0))
    self.image.blit(self.gfxman['ship'], (0, 0))
    self.image.blit(self.gfxman['exhaust2'], (14, self.gfxman['ship'].get_height()))

  # moving
  def fly_up_start(self):
    """
    Turns on engine exhaust by calling C{L{exhaust_on}} and
    moves the ship up.
    """
    self.exhaust_on()
    if self.rect.top >= self.speed:
      self.rect.move_ip(0, -self.speed)
  def fly_up_stop(self):
    """
    Turns off the engine exhaust (by calling C{L{exhaust_off}}) when ship stops moving up.
    """
    self.exhaust_off()
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

  # shooting
  #def shoot(self, g_projectiles):
  #  if not self.cooldown:
  #    if   self.weapon == 'bullets':
  #      self.cooldown = 3
  #      g_projectiles.add( Bullet(self.g_coll, self.g_expl, self.gfxman, (self.rect.left + 12, self.rect.top)) )
  #      g_projectiles.add( Bullet(self.g_coll, self.g_expl, self.gfxman, (self.rect.left + 25, self.rect.top)) )
  #    elif self.weapon == 'energy':
  #      self.cooldown = 7
  #      g_projectiles.add( EnergyProjectile(self.g_coll, self.g_expl, self.gfxman, (self.rect.left + 16, self.rect.top)) )
  #  else:
  #    self.cooldown -= 1
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
                                                  self.gfxman,
                                                  (self.rect.centerx + 1, self.rect.top))
    else:
      self.cooldown -= 1

  #def next_weapon(self):
  #  if self.weapon == 'bullets':
  #    self.weapon = 'energy'
  #    self.cooldown = 5
  #  else:
  #    self.weapon = 'bullets'
  #    self.cooldown = 3
  def next_weapon(self):
    """
    Select next weapon.
    """
    if self.cw == self.weapons.__len__() - 1:
      self.cw = 0
    else:
      self.cw += 1

  #def previous_weapon(self):
  #  self.next_weapon()
  def previous_weapon(self):
    """
    Select previous weapon.
    """
    if self.cw == 0:
      self.cw = self.weapons.__len__() - 1
    else:
      self.cw -= 1

class Projectile(pygame.sprite.Sprite):
  class Explosion(pygame.sprite.Sprite):
    pass

  damage = 0
  cooldown = 3
  offset = 0

  def __init__(self, g_coll, g_expl, gfxman, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)

    self.g_coll = g_coll
    self.g_expl = g_expl
    self.gfxman = gfxman

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
  def shoot(cls, g_proj, g_coll, g_expl, gfxman, pos):
    if cls == Bullet or cls == Shell:
      g_proj.add( cls(g_coll, g_expl, gfxman, (pos[0] - cls.offset, pos[1])) )
      g_proj.add( cls(g_coll, g_expl, gfxman, (pos[0] + cls.offset, pos[1])) )
    else:
      g_proj.add( cls(g_coll, g_expl, gfxman, pos) )
    return cls.cooldown
  shoot = classmethod(shoot)

class Bullet(Projectile):
  class Explosion(pygame.sprite.Sprite):
    def __init__(self, gfxman, pos, *groups):
      pygame.sprite.Sprite.__init__(self, *groups)
      self.gfxman = gfxman
      self.image = pygame.Surface((19, 19))
      self.image.blit(self.gfxman['expl_small'], (0, 0), (1, 1, 20, 20))
      self.image.set_colorkey((0, 138, 118))
      self.rect = pygame.Rect((0, 0), (19, 19))
      self.rect.center = pos[0] + 1, pos[1]

      self.time = 14

    def update(self):
      if   self.time == 12:
        self.time -= 1
        self.image.blit(self.gfxman['expl_small'], (0, 0), (21, 1, 20, 20))
      elif self.time == 10:
        self.time -= 1
        self.image.blit(self.gfxman['expl_small'], (0, 0), (41, 1, 20, 20))
      elif self.time == 8:
        self.time -= 1
        self.image.blit(self.gfxman['expl_small'], (0, 0), (61, 1, 20, 20))
      elif self.time == 6:
        self.time -= 1
        self.image.blit(self.gfxman['expl_small'], (0, 0), (81, 1, 20, 20))
      elif self.time == 4:
        self.time -= 1
        self.image.blit(self.gfxman['expl_small'], (0, 0), (101, 1, 20, 20))
      elif self.time == 2:
        self.time -= 1
        self.image.blit(self.gfxman['expl_small'], (0, 0), (121, 1, 20, 20))
      elif self.time == 0:
        self.kill()
        del self
      else:
        self.time -= 1

  cooldown = 3
  offset = 6

  def __init__(self, g_coll, g_expl, gfxman, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, gfxman, *groups)
    
    self.image = pygame.Surface((1, 2))
    self.image.set_colorkey((0, 0, 0))
    self.image.fill((255, 210, 0))
    self.rect = pygame.Rect(pos, (1, 2))
    
  def update(self):
    Projectile.update(self, -11)

  def explode(self):
    self.g_expl.add( Bullet.Explosion(self.gfxman, self.rect.center) )
    self.kill()
    del self

class Shell(Projectile):
  class Explosion(pygame.sprite.Sprite):
    def __init__(self, gfxman, pos, *groups):
      pygame.sprite.Sprite.__init__(self, *groups)
      self.gfxman = gfxman
      self.image = pygame.Surface((10, 8))
      self.image.blit(self.gfxman['ricochet'], (0, 0), (10, 0, 10, 8))
      self.image.set_colorkey((191, 220, 191))
      self.rect = pygame.Rect((0, 0), (10, 8))
      self.rect.center = pos

      self.time = 12

    def update(self):
      if   self.time == 9:
        self.time -= 1
        self.image.blit(self.gfxman['ricochet'], (0, 0), (10, 0, 10, 8))
      elif   self.time == 6:
        self.time -= 1
        self.image.blit(self.gfxman['ricochet'], (0, 0), (20, 0, 10, 8))
      elif   self.time == 3:
        self.time -= 1
        self.image.blit(self.gfxman['ricochet'], (0, 0), (30, 0, 10, 8))
      elif self.time == 0:
        self.kill()
        del self
      else:
        self.time -= 1

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

  def __init__(self, g_coll, g_expl, gfxman, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, gfxman, *groups)
    
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
    self.g_expl.add( Shell.Explosion(self.gfxman, pos) )
    self.kill()
    del self

class EnergyProjectile(Projectile):
  class Explosion(pygame.sprite.Sprite):
    def __init__(self, gfxman, pos, *groups):
      pygame.sprite.Sprite.__init__(self, *groups)
      self.gfxman = gfxman
      self.image = pygame.Surface((19, 19))
      self.image.blit(self.gfxman['expl_med'], (0, 0), (1, 1, 20, 20))
      self.image.set_colorkey((0, 138, 118))
      self.rect = pygame.Rect((0, 0), (19, 19))
      self.rect.center = pos

      self.time = 18

    def update(self):
      if   self.time == 16:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (21, 1, 20, 20))
      elif self.time == 14:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (41, 1, 20, 20))
      elif self.time == 12:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (61, 1, 20, 20))
      elif self.time == 10:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (81, 1, 20, 20))
      elif self.time == 8:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (101, 1, 20, 20))
      elif self.time == 6:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (121, 1, 20, 20))
      elif self.time == 4:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (141, 1, 20, 20))
      elif self.time == 2:
        self.time -= 1
        self.image.blit(self.gfxman['expl_med'], (0, 0), (161, 1, 20, 20))
      elif self.time == 0:
        self.kill()
        del self
      else:
        self.time -= 1

  cooldown = 5

  def __init__(self, g_coll, g_expl, gfxman, pos, *groups):
    Projectile.__init__(self, g_coll, g_expl, gfxman, *groups)

    self.image = self.gfxman['energy1_c']
    self.rect = pygame.Rect((0, 0), (1, 1))
    self.rect.centerx, self.rect.top = pos[0] - 3, pos[1]
    self.rect.size = self.gfxman['energy1_c'].get_width(), \
                     self.gfxman['energy1_c'].get_height()

    self.stage = 0
    self.wait = 3

  def update(self):
    center = self.rect.center
    if   self.stage == 0 and not self.wait:
      self.wait = 3
      self.stage = 1
      self.image = self.gfxman['energy1_d']
      self.rect.size = self.gfxman['energy1_d'].get_width(), \
                       self.gfxman['energy1_d'].get_height()
      self.rect.center = center
    elif self.stage == 1 and not self.wait:
      self.wait = 3
      self.stage = 2
      self.image = self.gfxman['energy1_e']
      self.rect.size = self.gfxman['energy1_e'].get_width(), \
                       self.gfxman['energy1_e'].get_height()
      self.rect.center = center
    elif self.stage == 2 and not self.wait:
      self.wait = 3
      self.stage = 3
      self.image = self.gfxman['energy1_b']
      self.rect.size = self.gfxman['energy1_b'].get_width(), \
                       self.gfxman['energy1_b'].get_height()
      self.rect.center = center
    elif self.stage == 3 and not self.wait:
      self.wait = 3
      self.stage = 0
      self.image = self.gfxman['energy1_c']
      self.rect.size = self.gfxman['energy1_c'].get_width(), \
                       self.gfxman['energy1_c'].get_height()
      self.rect.center = center
    else:
      self.wait -= 1
    
    Projectile.update(self, -9)

  def explode(self):
    self.g_expl.add( EnergyProjectile.Explosion(self.gfxman, self.rect.center) )
    self.kill()
    del self
