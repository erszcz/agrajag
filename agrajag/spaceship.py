#!/usr/bin/python
#coding: utf-8

import pygame, math, random
import mover

from base import AGObject
from dbmanager import DBManager
from gfxmanager import GfxManager
from groupmanager import GroupManager
from clock import Clock
from signals import Signal

from functions import deg2rad


class AGSprite(AGObject, pygame.sprite.Sprite):
  '''
  Abstract sprite class used as a parent class for more specific classes
  like Ship, Projectile or Obstacle.

  @type cfg: dict
  @ivar cfg: Class configuration provided by C{L{DBManager}}.

  @type gfx: dict
  @ivar gfx: The graphics resources provided by C{L{GfxManager}}.
  
  @type mover: None or class derived from C{Mover}
  @ivar mover: Object responsible for controlling sprite movement.

  @type max_speed: integer
  @ivar max_speed: Maximal speed object can by moved with expressed in
  pixels per second.

  @type pos: tuple or list
  @ivar pos: Current position of arbitrary object's point.

  @type align: string or tuple
  @ivar align: Name or names of properties used to align object's C{rect}
  attribute.
  '''

  max_speed = 0

  def __init__(self, pos, *groups):
    '''
    @type  pos: pair of integers
    @param pos: Initial position of the object. This pair defines
    the top-left corner of the object's rectangle C{rect}.
    '''

    AGObject.__init__(self)
    pygame.sprite.Sprite.__init__(self, *groups)

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self.gfx = GfxManager().get(self.__class__.__name__)
    self._setattrs('max_speed', self.cfg)
    self.clock = Clock()

    self._initialize_position(pos, 'center', (0, 0))

    self.mover = None

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

    try:
      if type(align) is tuple or type(align) is list:
        setattr(self.rect, align[0], pos[0])
        setattr(self.rect, align[1], pos[1])
      elif type(align) is str:
        setattr(self.rect, align, pos)
      else:
        raise ValueError("Invalid align value")
    except Exception:
      print align
      print size
      raise

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

  def __init__(self, pos, *groups):
    """
    """

    AGSprite.__init__(self, pos, *groups)
    self._setattrs('durability, explosion_cls_name', self.cfg)

  def damage(self, damage):
    """
    Deal damage and check whether the object ceases to exist. If so, call
    C{L{explode}}.

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

      GroupManager().get('explosions').add( explosion )

    self.kill()
    del self


class Ship(Destructible):
  '''
  Base class for player's ship and enemy ships.
  
  @type rect: C{pygame.Rect}
  @ivar rect: Rectangle describing position and size of the ship.
  '''

  def __init__(self, pos, *groups):
    '''
    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines the top-left
        corner of the ship's rectangle C{rect}.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    '''

    Destructible.__init__(self, pos, *groups)
    

class PlayerShip(Ship):
  """
  Represents the player's ship (not necessarily a spaceship).

  @type weapons: sequence
  @ivar weapons: A sequence of weapons available on the ship.

  @type _current_weapon: integer
  @ivar _current_weapon: Index of the sequence C{L{weapons}} which
  designates the currently used weapon.

  @type cooldown: unsigned integer
  @ivar cooldown: Number of rounds that have to pass before the weapon/s
      can be fired again.
  """

  def __init__(self, pos, *groups):
    """
    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines position
    of the ship nose.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """

    Ship.__init__(self, pos, *groups)
    self._check_gfx(['ship', 'exhaust'])
    self._check_cfg(['max_speed'])

    size = self.gfx['ship']['w'], \
           self.gfx['ship']['h'] + self.gfx['exhaust']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['ship']['image'])

    self._initialize_position(pos, ('centerx', 'top'), size)

    self.exhaust(False) # inits the image
    self.weapons = (Bullet, EnergyProjectile, Shell)
    self._current_weapon = 0 # current weapon list index
    self.cooldown = 0

  def exhaust(self, on):
    """
    Change the image of the ship by adding or removing an engine
    exhaust at the bottom.
    """
    
    state = 'on' if on else 'off'

    self.image.fill((0, 0, 0, 0))
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

    @type  on: boolean
    @param on: Tells whether the ship is to start or to stop movement.
    """

    if on:
      self.exhaust(True)
      delta_y = -round(self.clock.frame_span() * self.max_speed / 1000.)
      if self.rect.top >= -delta_y:  # '-' because: delta_y < 0
        self.rect.move_ip(0, delta_y)
        self.pos = self.pos[0], self.pos[1] + delta_y
    else:
      self.exhaust(False)

  def fly_down(self, boundary):
    """
    Move the ship down.

    @type  boundary: unsigned integer
    @param boundary: Height of the viewport. Needed in order to check
        whether the ship may fly farther downwards.
    """

    delta_y = round(self.clock.frame_span() * self.max_speed / 1000.)
    if self.rect.bottom <= boundary + delta_y:
      self.rect.move_ip(0, delta_y)
      self.pos = self.pos[0], self.pos[1] + delta_y
      
      
  def fly_left(self):
    """
    Move the ship left.
    """

    delta_x = -round(self.clock.frame_span() * self.max_speed / 1000.)
    if self.rect.left >= -delta_x:  # '-' because: delta_x < 0
      self.rect.move_ip(delta_x, 0)
      self.pos = self.pos[0] + delta_x, self.pos[1]

  def fly_right(self, boundary):
    """
    Move the ship right.

    @type  boundary: unsigned integer
    @param boundary: Width of the viewport. Needed in order to check
        whether the ship may fly farther towards the right edge of the screen.
    """

    delta_x = round(self.clock.frame_span() * self.max_speed / 1000.)
    if self.rect.right <= boundary - delta_x:
      self.rect.move_ip(delta_x, 0)
      self.pos = self.pos[0] + delta_x, self.pos[1]

  def shoot(self):
    """
    Shoot the currently selected weapon. Appropriately
    increase C{L{cooldown}}.
    """
    
    groupmanager = GroupManager()

    g_coll = groupmanager.get('enemies')
    g_expl = groupmanager.get('explosions')
    g_projectiles = groupmanager.get('projectiles')

    if not self.cooldown:
      cls = self.weapons[self._current_weapon]
      if cls in (Bullet, Shell):
        p1 = cls(g_coll, g_expl, (self.pos[0] - cls.offset, self.pos[1])) 
        p2 = cls(g_coll, g_expl, (self.pos[0] + cls.offset, self.pos[1])) 

        g_projectiles.add(p1, p2)

        self.cooldown = p1.cooldown
      else:
        p = cls(g_coll, g_expl, self.pos)
        g_projectiles.add(p)

        self.cooldown = p.cooldown
    else:
      self.cooldown -= 1

  def next_weapon(self):
    """Select next weapon."""
    if self._current_weapon == self.weapons.__len__() - 1:
      self._current_weapon = 0
    else:
      self._current_weapon += 1

  def previous_weapon(self):
    """Select previous weapon."""
    if self._current_weapon == 0:
      self._current_weapon = self.weapons.__len__() - 1
    else:
      self._current_weapon -= 1

class EnemyShip(Ship):
  def __init__(self, pos, *groups):
    """
    @type  pos: pair of integers
    @param pos: Initial position of the ship. This pair defines the top-left
        corner of the ship's rectangle C{rect}.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """

    Ship.__init__(self, pos, *groups)
 
    size = self.gfx['ship']['w'], self.gfx['ship']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['ship']['image'])

    self._blit_state('ship', 'def')

    self._initialize_position(pos, ('centerx', 'bottom'), size)

  def update(self):
    self._update_position();


class AdvancedPlayerShip(PlayerShip):
  """
  Represents the player's ship in more advanced version described in project's
  wiki. In later stage some funcionality of this class may be moved to not
  yet existant class Hull.

  @type center: sequence
  @ivar center: Position of ships center (ship itself, without exhaust
  and such).

  @type weapons: sequence
  @ivar weapons: A sequence of C{L{Weapon}}s available on the ship.

  @type _current_weapon: integer
  @ivar _current_weapon: Index of the sequence C{L{weapons}} which designates
  the currently used weapon. 

  @type shield: L{Shield}
  @ivar shield: Shield installed on the ship (may be None).

  @type armour: L{Armour}
  @ivar armour: Ship's armour.

  @type reactor: L{Reactor}
  @ivar reactor: Ship's reactor.
  """

  def __init__(self, pos, *groups):
    """
    @type  pos: sequence
    @param pos: Initial position of the ship. This pair defines position
    of ship nose.

    @type  groups: pygame.sprite.Group
    @param groups: A sequence of groups the object will be added to.
    """

    PlayerShip.__init__(self, pos, *groups)

    self.center = self.pos[0], self.pos[1] + self.gfx['ship']['h']/2

    self.weapons = [BasicBeamer(), BasicProjectileEnergyWeapon(), BasicPAW()]
    self._current_weapon = 0
    self.cooldown = None

    self.shield = BasicShield(self)
    self.armour = BasicArmour()
    self.reactor = BasicReactor()

    # signals
    self.shield_updated = Signal()
    self.armour_updated = Signal()
    self.weapon_updated = Signal()
    self.shield.shield_state_updated.connect(self.shield_updated)
    self.armour.armour_state_updated.connect(self.armour_updated)
    self.weapons[self._current_weapon].weapon_state_updated.connect(self.weapon_updated)

  def get_current_weapon(self):
    return self.weapons[self._current_weapon]
  current_weapon = property(get_current_weapon)

  def next_weapon(self):
    """Select next weapon."""
    self.current_weapon.weapon_state_updated.disconnect(self.weapon_updated)
    PlayerShip.next_weapon(self)
    self.current_weapon.weapon_state_updated.connect(self.weapon_updated)
    if isinstance(self.current_weapon, AmmoWeapon):
      self.weapon_updated('ammo', self.current_weapon.current)
    elif isinstance(self.current_weapon, EnergyWeapon):
      self.weapon_updated('energy', self.current_weapon.current, self.current_weapon.maximum)
      

  def previous_weapon(self):
    """Select previous weapon."""
    self.current_weapon.weapon_state_updated.disconnect(self.weapon_updated)
    PlayerShip.previous_weapon(self)
    self.current_weapon.weapon_state_updated.connect(self.weapon_updated)
    if isinstance(self.current_weapon, AmmoWeapon):
      self.weapon_updated('ammo', self.current_weapon.current)
    elif isinstance(self.current_weapon, EnergyWeapon):
      self.weapon_updated('energy', self.current_weapon.current, self.current_weapon.maximum)

  def shoot(self):
    """
    Shot from currently selected weapon. Do nothing if there is no 
    weapon selected.
    """

    if self._current_weapon is not None:
      self.weapons[self._current_weapon].shoot(self.pos)

  def activate_shield(self, on):
    if self.shield is not None:
      self.shield.activate(on)

  def damage(self, damage):
    """
    Deal damage and check whether the object ceases to exist. If so, call
    C{L{explode}}.

    @type  damage: integer
    @param damage: Amount of raw damage the ship takes.
    """

    if damage > 0 and self.shield is not None:
      damage = self.shield.absorb(damage, 1)

    if damage > 0 and self.armour is not None:
      damage = self.armour.absorb(damage, 1)

    if damage == 0:
      return

    self.durability -= damage
    if self.durability <= 0:
      self.explode()

  def update(self):
    """
    Update ship state (center, weapons, shield, armour, reactor, etc.)
    """

    self.center = self.pos[0], self.pos[1] + self.gfx['ship']['h']/2

    self._recharge()

    for w in self.weapons:
      w.update()

    if self.shield is not None:
      self.shield.update()
      
  def _recharge(self):
    """
    Recharge energy consuming items if ship is equipped with a reactor.

    Distribution of energy is determined by the reactor based on provided
    demands.
    """

    if self.reactor is None:
      return

    rechargables = []
    demands = []
    for w in self.weapons:
      if isinstance(w, EnergyWeapon):
        rechargables.append(w)
        demands.append(w.get_demand())

    if self.shield is not None:
      rechargables.append(self.shield)
      demands.append(self.shield.get_demand())

    supplies = self.reactor.supply(demands)
    if supplies is None:
      return

    for i in xrange(len(rechargables)):
      rechargables[i].recharge(supplies[i])


class Weapon(AGObject):
  """
  Base class for all weapons.

  @type cfg: dict
  @ivar cfg: Class configuration provided by C{L{DBManager}}.

  @type cooldown: integer
  @ivar cooldown: Minimal number of iterations between subsequent shots.

  @type remaining_cooldown: integer
  @ivar remaining_cooldown: Number of iterations that need to pass before
  weapon may shoot again.

  @type last_shot_time: float
  @ivar last_shot_time: Previous shot time.
  """

  cooldown = 0
  remaining_cooldown = 0

  def __init__(self):
    AGObject.__init__(self)

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self._setattrs('cooldown', self.cfg)

    # signals
    self.weapon_state_updated = Signal()

  def update(self):
    if self.remaining_cooldown > 0:
      self.remaining_cooldown -= 1


class EnergyWeapon(Weapon):
  """
  Base class for all weapons that consume energy to shoot.

  @type maximum: float
  @ivar maximum: Maximum amount of energy that weapon can store at a time

  @type current: float
  @ivar current: Currently stored amount of energy

  @type recharge_rate: float
  @ivar recharge_rate: Maximum number of energy points recharged per second.

  @type cost: float
  @ivar cost: Amount of energy needed for one shot.
  """

  maximum = 0
  current = 0
  recharge_rate = 1
  cost = 1

  def __init__(self):
    """
    """

    Weapon.__init__(self)
    self._setattrs('maximum, recharge_rate, cost', self.cfg)

    self.current = self.maximum

  def get_demand(self):
    """
    Return energy demand, that is difference between maximal and current 
    energy level.
    """

    return self.maximum - self.current

  def recharge(self, supply):
    """
    Recharge energy. Amount of energy recharged depends on amount
    of energy supplied and recharge rate. It is assumed that supply is
    never larger than demand. If there is any excess it is lost.
    """

    supply = supply if supply <= self.recharge_rate else self.recharge_rate
    self.current += supply

    if self.current > self.maximum:
      self.current = self.maximum

    self.weapon_state_updated('energy', self.current, self.maximum)


  def shoot(self):
    self.weapon_state_updated('energy', self.current, self.maximum)


class AmmoWeapon(Weapon):
  """
  Base class for all weapons that need ammunition to shoot.

  @type maximum: integer
  @ivar maximum: maximum number of ammo pieces in weapon storage

  @type current: integer
  @ivar current: current number of ammo pieces in weapon storage
  """

  def __init__(self):
    Weapon.__init__(self)
    self._setattrs('maximum', self.cfg)

    self.current = self.maximum

  def shoot(self):
    self.weapon_state_updated('ammo', self.current)

class InstantAmmoWeapon(AmmoWeapon):
  """
  """

  pass

class ProjectileAmmoWeapon(AmmoWeapon):
  """
  Base class for all ammo weapons that shoot projectiles moving with finite
  speed.
  """

  def __init__(self):
    AmmoWeapon.__init__(self)
    self._setattrs('projectile_cls_name', self.cfg)

  def shoot(self, pos):
    """
    Perform shot if the weapon has cooled and there is ammo left. Create
    projectile instance.
    """
  
    if self.remaining_cooldown > 0:
      return

    if self.current < 1:
      return

    self.remaining_cooldown = self.cooldown
    self.current -= 1

    projectile_cls = eval(self.projectile_cls_name)
    projectile = projectile_cls(pos)

    GroupManager().get('projectiles').add(projectile)

    AmmoWeapon.shoot(self)


class BasicPAW(ProjectileAmmoWeapon):
  """
  Basic type of C{L{ProjectileAmmoWeapon}}.
  """

  pass

class InstantEnergyWeapon(EnergyWeapon):
  """
  Base class for instantly hitting C{L{EnergyWeapon}}s.

  @type damage: float
  @ivar damage: Damage caused by single hit.
  """

  damage = 1

  def __init__(self):
    EnergyWeapon.__init__(self)
    self._setattrs('damage, explosion_cls_name, beam_cls_name', self.cfg)

  @staticmethod
  def _compare_target_pos(a, b):
    if a.rect.bottom > b.rect.bottom:
      return -1
    elif a.rect.bottom == b.rect.bottom:
      return 0
    else:
      return 1

  def shoot(self, pos):
    """
    Perform shot if the weapon has cooled and there is enough energy. Find
    closest colliding object and damage it. Create visual representation of
    the beam.
    """
  
    if self.remaining_cooldown > 0:
      return

    if self.current < self.cost:
      return

    self.remaining_cooldown = self.cooldown
    self.current -= self.cost

    beam_cls = eval(self.beam_cls_name)
    beam = beam_cls()

    GroupManager().get('projectiles').add(beam)

    all_targets = GroupManager().get('enemies').sprites()
    targets = []

    for t in all_targets:
      if pos[0] < t.rect.right and pos[0] > t.rect.left \
          and pos[1] > t.rect.bottom:
            targets.append(t)

    if len(targets) == 0:
      beam.set_position(pos, (pos[0], 0))
      return 

    targets.sort(cmp = self._compare_target_pos)
    t = targets[0]

    t_pos = pos[0], t.rect.bottom

    beam.set_position(pos, t_pos)

    expl_cls = eval(self.explosion_cls_name)
    expl = expl_cls(t_pos)

    GroupManager().get('explosions').add(expl)

    t.damage(self.damage)

    EnergyWeapon.shoot(self)


class BasicBeamer(InstantEnergyWeapon):
  """
  The least powerful yet energy effective instant energy weapon.
  """

  def __init__(self):
    InstantEnergyWeapon.__init__(self)


class InstantEnergyBeam(AGSprite):
  """
  Visual representation of energy fired by C{L{InstantEnergyWeapon}}s.

  @type pos: sequence
  @ivar pos: Central point of the farthests part of the beam.

  @type vanish_speed: integer
  @ivar vanish_speed: number of alpha levels per second

  @type init: bool
  @ivar init: Inital iteration or not
  """

  def __init__(self):
    """
    """

    AGSprite.__init__(self, (0,0))
    self.vanish_speed = self.cfg['vanish_speed']
    self.init = True

  def get_width(self):
    """Return width of the beam graphics in pixels."""

    return self.gfx['beam_slice']['w']

  def set_position(self, begin, end):
    """Set positions of beam ends and resize beam image accordingly."""

    size = self.get_width(), int(math.fabs(begin[1] - end[1]))

    self._initialize_position(end, ('centerx', 'top'), size)
    self.image = pygame.Surface(size)
    self.image.set_alpha(255)
    for i in xrange(0, self.rect.height - 1):
      self._blit_state('beam_slice', 'def', (0, i))

  def update(self):
    if self.init:
      self.init = False
      return

    current_alpha = self.image.get_alpha()
    if current_alpha > self.vanish_speed:
      self.image.set_alpha(current_alpha - self.vanish_speed)
    else:
      self.kill()
      del self


class BasicBeam(InstantEnergyBeam):
  """
  Beam used by BasicBeamer gun.
  """

  def __init__(self):
    InstantEnergyBeam.__init__(self)


class ProjectileEnergyWeapon(EnergyWeapon):
  """
  Base class for C{L{EnergyWeapon}}s that shoot energy in the form of
  projectiles moving with finite speed.
  """

  def __init__(self):
    EnergyWeapon.__init__(self)
    self._setattrs('projectile_cls_name', self.cfg)

  def shoot(self, pos):
    """
    Perform shot if the weapon has cooled and there is enough energy. Create
    projectile instance.
    """
  
    if self.remaining_cooldown > 0:
      return

    if self.current < self.cost:
      return

    self.remaining_cooldown = self.cooldown
    self.current -= self.cost

    projectile_cls = eval(self.projectile_cls_name)
    projectile = projectile_cls(pos)

    GroupManager().get('projectiles').add(projectile)

    EnergyWeapon.shoot(self)


class BasicProjectileEnergyWeapon(ProjectileEnergyWeapon):
  """
  The least powerful, yet energy effective projectile energy weapon.
  """

  def __init__(self):
    ProjectileEnergyWeapon.__init__(self)


class Shield(AGSprite):
  """
  Base class for all shield types used both by player ship and enemies. A
  working shield may and should be represented by some graphics, but should
  not collide on its own.

  @type owner: C{L{AGSprite}}
  @ivar owner: Game object that owns the shield.

  @type maximum: float
  @ivar maximum: Maximum amount of damage shield can absorb in one hit.

  @type current: float
  @ivar current: Amount of damage the shield can absorb at this moment.

  @type recharge_rate: float
  @ivar recharge_rate: Maximum number of energy points recharged per second.

  @type active: bool
  @ivar active: Tells whether shield is working or not.
  """

  maximum = 0
  current = 0
  recharge_rate = 0

  owner = None
  active = False

  def __init__(self, owner):
    AGSprite.__init__(self, owner.rect.center)
    self._check_gfx(['shield'])
    self._check_cfg(['maximum', 'recharge_rate'])

    self._setattrs('maximum, recharge_rate', self.cfg)

    self.owner = owner
    self.current = self.maximum

    size = self.gfx['shield']['w'], self.gfx['shield']['h']
    self.image = pygame.Surface(size, pygame.SRCALPHA, 
        self.gfx['shield']['image'])

    GroupManager().get('shields').add(self)

    # signals
    self.shield_state_updated = Signal()

  def update(self):
    if self.active:
      size = self.gfx['shield']['w'], self.gfx['shield']['h']

      pos = self.owner.center
      self._initialize_position(pos, 'center', size)

    self.shield_state_updated(self.current, self.maximum)


  def activate(self, on):
    """
    Activate or deactivate the shield. Display shield graphics if shield is 
    activated.
    """

    self.active = on
    if on and self.current > 0:
      self._blit_state('shield', 'def')
    else:
      self.image.fill((0, 0, 0, 0))


  def absorb(self, damage, efficiency):
    """
    If shield is active absorb specified amount of raw C{damage} caused with
    C{efficiency} and return remaining raw damage to be absorbed. Turn shield
    off it current energy drops to zero. If shield is not active, return
    unmodified raw damage.
    """

    if not self.active:
      return damage

    total = damage * efficiency
    absorbed = self.current if total > self.current else total
    remaining = (total - absorbed) / efficiency

    self.current -= absorbed

    if self.current == 0:
      self.activate(False)

    return remaining


  def get_demand(self):
    """
    Return energy demand, that is difference between maximal and current 
    energy level.
    """

    return self.maximum - self.current


  def recharge(self, supply):
    """
    Recharge shield energy. Amount of energy recharged depends on amount
    of energy supplied and recharge rate. It is assumed that supply is
    never larger than demand. If there is any excess it is lost.
    """

    supply = supply if supply <= self.recharge_rate else self.recharge_rate
    self.current += supply

    if self.current > self.maximum:
      self.current = self.maximum

    
class BasicShield(Shield):
  def __init__(self, owner):
    Shield.__init__(self, owner)

    
class Armour(AGObject):
  """
  Base class for all ship armours.

  @type maximum: float
  @ivar maximum: maximal amount of damage armour can absorb in one hit (maximal durability)

  @type current: float
  @ivar current: amount of damage the armour can absorb at this moment (current durability)
  """

  maximum = 0
  current = 0

  def __init__(self):
    """
    """

    AGObject.__init__(self)

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self._setattrs('maximum', self.cfg)

    # signals
    self.armour_state_updated = Signal()

  def absorb(self, damage, efficiency):
    """
    Absorb specified amount of raw C{damage} caused with C{efficiency} and
    return remaining raw damage to be absorbed.
    """

    total = damage * efficiency
    absorbed = self.current if total > self.current else total
    remaining = (total - absorbed) / efficiency

    self.current -= absorbed

    self.armour_state_updated(self.current)
    return remaining


class BasicArmour(Armour):
  """
  The weakest armour type player ship can use.
  """

  def __init__(self):
    Armour.__init__(self)


class Reactor(AGObject):
  """
  Base class for all ship reactors. Reactor is responsible for providing
  energy to all energy consuming components of a ship (i.e. shields, 
  energy weapons).
  """

  def __init__(self):
    """
    """

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self._setattrs('power', self.cfg)

  def supply(self, demands):
    """
    Return all energy available at this moment distribited in accordance
    to provided demands.
    """

    total_demand = float(sum(demands))
    if math.fabs(total_demand) < 0.1:
      return None

    supplies = []
    for i in xrange(len(demands)):
      supplies.append(self.power * demands[i] / total_demand)

    return supplies


class BasicReactor(Reactor):
  """
  """

  def __init__(self):
    Reactor.__init__(self)


class Explosion(AGSprite):
  def __init__(self, pos, *groups):
    AGSprite.__init__(self, pos, *groups)

    self.time = 0
    self.frame_length = self.cfg['frame_length']
    self.frame_count = self.cfg['frame_count']


  def update(self):
  # improving this method to increase the animation look wouldn't hurt
    if self.time >= self.frame_count * self.frame_length:
      self.kill()
      del self
    else:
      try:
        for frame in range(0, self.frame_count):
          if self.time in range(frame * self.frame_length,
                                (frame + 1) * self.frame_length):
            self.image.fill((0, 0, 0, 0))
            self._blit_state('expl', 'frame' + str(frame))
            break
      except ValueError, value:
        print "Warning: unhandled ValueError: %s" % value
      self.time += self.clock.frame_span()


class BulletExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['expl']['image'])
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, ('centerx', 'centery'), size)


class ShellExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['expl']['image'])
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, 'center', size)


class BasicBeamExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['expl']['image'])
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, 'center', size)


class ObstacleExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['expl']['image'])
    self._blit_state('expl', 'frame0')

    self._initialize_position(pos, ('centerx', 'centery'), size)

class EnergyProjectileExplosion(Explosion):
  def __init__(self, pos, *groups):
    Explosion.__init__(self, pos, *groups)

    size = self.gfx['expl']['w'], self.gfx['expl']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['expl']['image'])
    self._blit_state('expl', 'frame4')

    self._initialize_position(pos, ('centerx', 'centery'), size)

class Projectile(AGSprite):
  damage = 0
  cooldown = 0
  offset = 0

  def __init__(self, pos, *groups):
    AGSprite.__init__(self, pos, *groups)
 
    self._setattrs('damage, cooldown', self.cfg)

    self.g_coll = GroupManager().get('enemies')
    self.g_expl = GroupManager().get('explosions')

    self.mover = mover.LinearMover(pos, self.max_speed, {'dir' : 180})

  def update(self):
    self._update_position()
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

  def __init__(self, pos, *groups):
    Projectile.__init__(self, pos, *groups)
    
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

  def __init__(self, pos, *groups):
    Projectile.__init__(self, pos, *groups)
    
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
        l_gc[ind].damage(self.damage)
      else:
        l_gc = l_gc[(ind + 1):]
        ind = self.rect.collidelist(l_gc)
        if ind != -1:
          self.explode((self.rect.centerx, l_gc[ind].rect.bottom))
          l_gc[ind].damage(self.damage)

  def explode(self, pos):
    self.g_expl.add( ShellExplosion(pos) )
    self.kill()
    del self

class EnergyProjectile(Projectile):
  def __init__(self, pos, *groups):
    Projectile.__init__(self, pos, *groups)

    size = self.gfx['energy']['w'], self.gfx['energy']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['energy']['image'])
    self._blit_state('energy', 'frame2')

    self._initialize_position(pos, ('centerx', 'top'), size)

    #self.period = 400
    self.period = (100, 200, 300, 400, 800)[random.randint(0, 4)]
    self.frame_count = 4  # const
    self.time = random.randint(0, self.period)
    self.frame_length = self.period / self.frame_count

  def update(self):
    while self.time >= self.period:
      self.time -= self.period
    for frame in range(0, self.frame_count):
      if self.time in range(frame * self.frame_length,
                            (frame + 1) * self.frame_length):
        self.image.fill((0, 0, 0, 0))
        self._blit_state('energy', 'frame' + str(frame))
        break
    self.time += self.clock.frame_span()
    
    Projectile.update(self)

  def explode(self):
    self.g_expl.add( EnergyProjectileExplosion(self.rect.center) )
    self.kill()
    del self
