#!/usr/bin/python
#coding: utf-8

import pygame, math, random
import sys

import mover
from base import AGObject, AGRect, Overlay
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

  @type pos: sequence
  @ivar pos: Current position of arbitrary object's point in global
  coordinate system.

  @type center: sequence
  @ivar center: Current position of object's center in global coordinate
  system.

  @type align: string or tuple
  @ivar align: Name or names of properties used to align object's C{rect}
  attribute.

  @type _overlay: C{L{Overlay}}
  @ivar _overlay: Object used to display auxiliary animations.
  '''

  max_speed = 0

  _overlay = None
  _animations = []

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
    self._overlay = Overlay()

    g_draw = GroupManager().get('draw')
    g_draw.add(self)
    g_draw.add(self._overlay)

  def set_mover(self, mover):
    """
    """

    self.mover = mover

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

  def _state_area(self, image, state):
    """
    Return C{pygame.Rect} containing information on position and area
    of graphic resource representing selected state.

    @type  image: string
    @param image: Name of graphic resource.

    @type  state: string
    @param state: Name of state.
    """

    return self.gfx[image]['states'][state]['x_off'], \
           self.gfx[image]['states'][state]['y_off'], \
           self.gfx[image]['w'], \
           self.gfx[image]['h']

  def _blit_state(self, image, state, pos = (0, 0)):
    '''
    Blit selected image state aquired from GfxManager on image
    representing current instance
    
    @type  image: string
    @param image: Name of resource in object's C{gfx} dictionary.

    @type  state: string
    @param state: Name of resource's state.

    @type  pos: sequence
    @param pos: Position of upper-left corner of the image to be blit in 
    object's C{image} coordinate space.
    '''

    area = self._state_area(image, state)
    self.image.blit(self.gfx[image]['image'], pos, area)

  def _init_animation(self, res, pos = (0, 0), align = 'center'):
    """
    Initialize animation of resource C{res} on object's overlay.
    If object's overlay is not initialized, do it.

    @type  res: string
    @param res: Name of graphic resource contained by C{self.gfx}

    @type  pos: sequence
    @param pos: Position of a point relative to which image drawn is aligned.
    Point cooridinates itself must be relative to C{self.center}.

    @type  align: string or sequence
    @param align: String or sequence used to align drawn images relative
    to C{pos} (as when aligning C{L{AGRect}}.
    """

    if not self._overlay.has_image():
      self._overlay.init_image(self.image)

    size = self.gfx[res]['w'], self.gfx[res]['h']
    anim = {
        'period'    : 0.45,
        'time'      : 0,
        'resource'  : res,
        'states'    : self.gfx[res]['states'].keys(),
        'size'      : size,
        'pos'       : pos,
        'align'     : align
        }

    self._animations.append(anim)

  def _update_animations(self):
    """
    """
    
    if len(self._animations) == 0:
      return

    self._overlay.align(self.center)

    frame_span = self.clock.frame_span() / 1000.
    for anim in self._animations:
      dest = AGRect((0, 0), anim['size'])
      dest.align(anim['pos'], anim['align'])

      if anim['time'] >= anim['period']:
        self._animations.remove(anim)
        self._overlay.clear(dest)
        continue

      i = int(math.floor(anim['time'] * len(anim['states']) / anim['period']))

      res = anim['resource']
      area = self._state_area(res, anim['states'][i])

      self._overlay.blit(self.gfx[res]['image'], dest, area)
      anim['time'] += frame_span


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
    self.rect = AGRect((0, 0), size)

    self.rect.align(pos, align)
    self.center = self.rect.center
  
  def _update_position(self):
    """
    Set new position of the object. New position is determined by
    object's C{mover} if object has one. If not position is not changed.
    Object's C{align} attribute is used to properly align object's C{rect}.
    """

    if self.mover is not None:
      self.pos = self.mover.update()
      self.rect.align(self.pos, self.align)
      self.center = self.rect.center

  def distance(self, peer):
    """
    Return distance (city) between self and peer.

    @type  peer: AGSprite
    @param peer: 
    """

    return math.fabs(self.center[0] - peer.center[0]) + \
        math.fabs(self.center[1] - peer.center[1])

  @staticmethod
  def _closest_compare_dists(a, b):
    """
    For dictionaries C{a} and {b} return -1, 0, 1 depending on 
    values for C{dict} keys.

    This method is used by C{AGSprite.closest(peers)}.
    """

    if a['dist'] < b['dist']:
      return -1
    elif a['dist'] == b['dist']:
      return 0
    else:
      return 1

  def closest(self, peers):
    """
    Return object selected from C{peers} closest to C{self}. Return 
    C{None} if C{peers} is empty.

    @type  peers: sequence of C{L{AGSprite}}s
    @param peers:
    """

    if len(peers) == 0:
      return None

    dists = []
    for p in peers:
      d = { 'dist' : self.distance(p),
            'index': peers.index(p) }

      dists.append(d)

    dists.sort(cmp = self._closest_compare_dists)
    return peers[dists[0]['index']]


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
  destroyed = False

  def __init__(self, pos, *groups):
    """
    """

    AGSprite.__init__(self, pos, *groups)
    self._setattrs('durability, explosion_cls_name', self.cfg)

  def damage(self, damage, speed = None):
    """
    Deal damage and check whether the object ceases to exist. If so, call
    C{L{explode}}.

    @type  damage: integer
    @param damage: Amount of damage the object takes.

    @type  speed: float or None
    @param speed: Speed of damaging projectile. None for instant hits.
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

    self.destroyed = True
    self.kill()
    del self


class Ship(Destructible):
  '''
  Base class for player's ship and enemy ships.
  
  @type rect: C{pygame.Rect}
  @ivar rect: Rectangle describing position and size of the ship.

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

    self.weapons = []
    self._current_weapon = None

    self.shield = None
    self.armour = None
    self.reactor = None

  def update(self):
    """
    Update ship state (center, weapons, shield, armour, reactor, etc.)
    """

    if self.reactor is not None:
      self.recharge(self.reactor.supply())

    for w in self.weapons:
      w.update()

    if self.shield is not None:
      self.shield.update()

  def recharge(self, supply, ignore_recharge_rates = False):
    """
    Recharge energy consuming items with C{supply} units of energy.

    Distribution of energy is proportional to energy demands.

    @type  supply: float
    @param supply: Amount of energy to divide between rechargable items.

    @type  ignore_recharge_rates: bool
    @param ignore_recharge_rates: If True items' can be recharged faster
    than their recharge rates allow.
    """

    # find rechargable items and their energy demands
    rechargables = []
    demands = []
    for w in self.weapons:
      if isinstance(w, EnergyWeapon):
        rechargables.append(w)
        demands.append(w.get_demand())

    if self.shield is not None:
      rechargables.append(self.shield)
      demands.append(self.shield.get_demand())

    # distribute supply according to demands
    total_demand = float(sum(demands))

    # avoid division by zero
    if math.fabs(total_demand) < 0.01:
      return

    for i in xrange(len(rechargables)):
      rechargables[i].recharge(supply * demands[i] / total_demand,
          ignore_recharge_rates)

  def damage(self, damage, speed = None):
    """
    Deal damage and check whether the object ceases to exist. If so, call
    C{L{explode}}.

    @type  damage: integer
    @param damage: Amount of raw damage the ship takes.

    @type  speed: float
    @param speed: Speed of projectile dealing damage or None if projectile
    does not have finite speed or damage comes from other source. This
    parameter is used to determine whether autoshield will activate or not.
    """

    if damage > 0 and self.shield is not None:
      if isinstance(self.shield, AutoShield):
        damage = self.shield.absorb(damage, 1, speed)
      else:
        damage = self.shield.absorb(damage, 1)

    if damage > 0 and self.armour is not None:
      damage = self.armour.absorb(damage, 1)

    if damage == 0:
      return

    self.durability -= damage
    if self.durability <= 0:
      self.explode()

  def explode(self):
    if self.shield is not None:
      self.shield.kill()
      del self.shield

    Destructible.explode(self)


class PlayerShip(Ship):
  """
  Represents the player's ship (not necessarily a spaceship).
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

    self.exhaust(False) 

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
  """
  """

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

    self._equip()

  def _equip(self):
    """
    Initialize ship equipment (weapons, shield, armour, reactor, etc) 
    according to class configuration.
    """

    if self.cfg.has_key('weapons_cls_names'):
      for c in self.cfg['weapons_cls_names']:
        weapon_cls = eval(c)
        self.weapons.append(weapon_cls(self))

    if len(self.weapons) > 0:
      self._current_weapon = 0

    if self.cfg.has_key('shield_cls_name'):
      shield_cls = eval(self.cfg['shield_cls_name'])
      self.shield = shield_cls(self)

    if self.cfg.has_key('armour_cls_name'):
      armour_cls = eval(self.cfg['armour_cls_name'])
      self.armour = armour_cls()
    
    if self.cfg.has_key('reactor_cls_name'):
      reactor_cls = eval(self.cfg['reactor_cls_name'])
      self.reactor = reactor_cls()

  def shoot(self):
    """
    Shot from currently selected weapon. Do nothing if there is no 
    weapon selected.
    """

    if self._current_weapon is not None:
      self.weapons[self._current_weapon].shoot(self.pos)

  def update(self):
    Ship.update(self)

    self._update_position()
    self.shoot()


class EnemyInterceptor(EnemyShip):
  """
  """

  def __init__(self, pos, *groups):
    EnemyShip.__init__(self, pos, *groups)


class AdvancedPlayerShip(PlayerShip):
  """
  Represents the player's ship in more advanced version described in project's
  wiki. In later stage some funcionality of this class may be moved to not
  yet existant class Hull.

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

    self.weapons = [SeekingPEW(self), BasicBeamer(self),
        BasicTPEW(self), BasicPAW(self)]
    self._current_weapon = 0

    self.shield = BasicAutoShield(self)
    self.armour = BasicArmour()
    self.reactor = BasicReactor()

    # signals
    self.shield_updated = Signal()
    self.armour_updated = Signal()
    self.weapon_updated = Signal()
    self.shield.shield_state_updated.connect(self.shield_updated)
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

  def damage(self, damage, speed = None):
    """
    Deal damage and check whether the object ceases to exist. If so, call
    C{L{explode}}.

    @type  damage: integer
    @param damage: Amount of raw damage the ship takes.
    """

    Ship.damage(self, damage, speed)
    self.armour_updated(self.durability + self.armour.current)

  def update(self):
    """
    Update ship state (center, weapons, shield, armour, reactor, etc.)
    """

    Ship.update(self)

    self.center = self.pos[0], self.pos[1] + self.gfx['ship']['h']/2
    self._update_animations()
      

class Weapon(AGObject):
  """
  Base class for all weapons.

  @type cfg: dict
  @ivar cfg: Class configuration provided by C{L{DBManager}}.

  @type cooldown: float
  @ivar cooldown: Time between subsequent shots in seconds.

  @type remaining_cooldown: float
  @ivar remaining_cooldown: Time that need to pass before
  weapon may shoot again (in seconds).

  @type last_shot_time: float
  @ivar last_shot_time: Previous shot time.

  @type owner: C{L{AGSprite}}
  @ivar owner: Game object that owns the weapon.
  """

  cooldown = 0
  remaining_cooldown = 0

  def __init__(self, owner):
    AGObject.__init__(self)

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self._setattrs('cooldown', self.cfg)
    self.owner = owner

    # signals
    self.weapon_state_updated = Signal()

  def update(self):
    if self.remaining_cooldown > 0:
      self.remaining_cooldown -= Clock().frame_span() / 1000.


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

  def __init__(self, owner):
    """
    """

    Weapon.__init__(self, owner)
    self._setattrs('maximum, recharge_rate, cost', self.cfg)

    self.current = self.maximum

  def get_demand(self):
    """
    Return energy demand, that is difference between maximal and current 
    energy level.
    """

    return self.maximum - self.current

  def recharge(self, supply, ignore_recharge_rate = False):
    """
    Recharge energy. Amount of energy recharged depends on amount
    of energy supplied and recharge rate. It is assumed that supply is
    never larger than demand. If there is any excess it is lost.
    """

    if not ignore_recharge_rate:
      recharge = self.recharge_rate * Clock().frame_span() / 1000.
      supply = supply if supply <= recharge else recharge

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

  def __init__(self, owner):
    Weapon.__init__(self, owner)
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

  @type targeted: bool
  @ivar targeted: Indicates whether weapon automatically finds target
  and shoots projectiles towards it or not.

  @type target: 
  @ivar target: Reference to selected target or None.

  @type targeting_angle: float
  @ivar targeting_angle: Half of the shooting arc in radians.
  """

  targeted = False
  target = None
  targeting_angle = 60

  def __init__(self, owner):
    AmmoWeapon.__init__(self, owner)
    self._setattrs('projectile_cls_name, targeted, targeting_angle', self.cfg)

    self._find_target()

  def _find_target(self):
    """
    Find random object within the shooting arc and target it (if weapon is not
    targeted do nothing).
    """

    if self.targeted:
      if isinstance(self.owner, EnemyShip):
        targets = GroupManager().get('ship').sprites()
      else:
        targets = GroupManager().get('enemies').sprites()

      for t in targets:
        if self._target_dir(t) is None:
          targets.remove(t)

      target = self.owner.closest(targets)
      if target is not None:
        self.target = target

    return self.target

  def _target_dir(self, target):
    """
    Return target direction measured in degrees. If weapon is not targeted
    it shoots straight on. If shot cannot be performed for some reason 
    (target not within shooting arc or no target at all) return None.

    @type  target:
    @param target:
    """

    if not self.targeted:
      return 0 if isinstance(self.owner, EnemyShip) else -180

    if target is None:
      return None

    dx = self.owner.center[0] - target.center[0]
    dy = self.owner.center[1] - target.center[1]

    if dy == 0:
      return 0 if isinstance(self.owner, EnemyShip) else -180

    if isinstance(self.owner, EnemyShip):
      if dy > 0:
        return None
    else:
      if dy < 0:
        return None

    tg = dx / float(dy)
    if math.fabs(tg) > math.radians(self.targeting_angle):
      return None

    dir = math.degrees(math.atan(tg))
    if isinstance(self.owner, PlayerShip):
      dir += 180

    return dir

  def shoot(self, pos):
    """
    Perform shot if the weapon has cooled and there is ammo left. Create
    projectile instance.
    """
 
    if self.remaining_cooldown > 0:
      return

    if self.current < 1:
      return

    if self.target is not None and self.target.destroyed:
      self.target = None
      return

    dir = self._target_dir(self.target)
    if dir is None:
      self._find_target()
      dir = self._target_dir(self.target)

    if dir is None:
      return

    self.remaining_cooldown = self.cooldown
    self.current -= 1

    if isinstance(self.owner, EnemyShip):
      g_proj = GroupManager().get('enemy_projectiles')
      g_coll = GroupManager().get('ship')
    else:
      g_proj = GroupManager().get('player_projectiles')
      g_coll = GroupManager().get('enemies')

    projectile_cls = eval(self.projectile_cls_name)
    projectile = projectile_cls(pos, dir, g_coll, g_proj)

    AmmoWeapon.shoot(self)


class BasicPAW(ProjectileAmmoWeapon):
  """
  Basic type of C{L{ProjectileAmmoWeapon}}.
  """

  def __init__(self, owner):
    ProjectileAmmoWeapon.__init__(self, owner)


class InstantEnergyWeapon(EnergyWeapon):
  """
  Base class for instantly hitting C{L{EnergyWeapon}}s.

  @type damage: float
  @ivar damage: Damage caused by single hit.
  """

  damage = 1

  def __init__(self, owner):
    EnergyWeapon.__init__(self, owner)
    self._setattrs('damage, explosion_cls_name, beam_cls_name', self.cfg)

  @staticmethod
  def _compare_player_target_pos(a, b):
    if a.rect.bottom > b.rect.bottom:
      return -1
    elif a.rect.bottom == b.rect.bottom:
      return 0
    else:
      return 1

  @staticmethod
  def _compare_enemy_target_pos(a, b):
    if a.rect.top < b.rect.top:
      return -1
    elif a.rect.top == b.rect.top:
      return 0
    else:
      return 1

  def _find_target(self, pos):
    """
    Return target that will be hit by the beam or None.
    """

    targets = []
    if isinstance(self.owner, EnemyShip):
      all_targets = GroupManager().get('ship').sprites()

      for t in all_targets:
        if pos[0] < t.rect.right and pos[0] > t.rect.left \
          and pos[1] < t.rect.top:
            targets.append(t)

      targets.sort(cmp = self._compare_enemy_target_pos)
    else:
      all_targets = GroupManager().get('enemies').sprites()

      for t in all_targets:
        if pos[0] < t.rect.right and pos[0] > t.rect.left \
          and pos[1] > t.rect.bottom:
            targets.append(t)

      targets.sort(cmp = self._compare_player_target_pos)

    return targets[0] if len(targets) > 0 else None

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

    GroupManager().get('beams').add(beam)

    if isinstance(self.owner, EnemyShip):
      g_coll = GroupManager().get('ship')
    else:
      g_coll = GroupManager().get('enemies')

    target = self._find_target(pos)
    if target is None:
      if isinstance(self.owner, EnemyShip):
        #tmp
        beam.set_position((pos[0], 500), pos)
      else:
        beam.set_position(pos, (pos[0], 0))

      return 

    if isinstance(self.owner, EnemyShip):
      t_pos = pos[0], target.rect.top
      beam.set_position(t_pos, pos)
    else:
      t_pos = pos[0], target.rect.bottom
      beam.set_position(pos, t_pos)

    expl_cls = eval(self.explosion_cls_name)
    expl = expl_cls(t_pos)

    GroupManager().get('explosions').add(expl)

    target.damage(self.damage)

    EnergyWeapon.shoot(self)


class BasicBeamer(InstantEnergyWeapon):
  """
  The least powerful yet energy effective instant energy weapon.
  """

  def __init__(self, owner):
    InstantEnergyWeapon.__init__(self, owner)


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

  @type targeted: bool
  @ivar targeted: Indicates whether weapon automatically finds target
  and shoots projectiles towards it or not.

  @type target: 
  @ivar target: Reference to selected target or None.

  @type targeting_angle: float
  @ivar targeting_angle: Half of the shooting arc in radians.
  """

  targeted = False
  target = None
  targeting_angle = 60

  def __init__(self, owner):
    EnergyWeapon.__init__(self, owner)
    self._setattrs('projectile_cls_name, targeted, targeting_angle', self.cfg)

    self._find_target()

  def _find_target(self):
    """
    Find random object within the shooting arc and target it (if weapon is not
    targeted do nothing).
    """

    if self.targeted:
      if isinstance(self.owner, EnemyShip):
        targets = GroupManager().get('ship').sprites()
      else:
        targets = GroupManager().get('enemies').sprites()

      for t in targets:
        if self._target_dir(t) is None:
          targets.remove(t)

      target = self.owner.closest(targets)
      if target is not None:
        self.target = target

    return self.target

  def _target_dir(self, target):
    """
    Return target direction measured in degrees. If weapon is not targeted
    it shoots straight on. If shot cannot be performed for some reason 
    (target not within shooting arc or no target at all) return None.

    @type  target:
    @param target:
    """

    if not self.targeted:
      return 0 if isinstance(self.owner, EnemyShip) else -180

    if target is None:
      return None

    dx = self.owner.center[0] - target.center[0]
    dy = self.owner.center[1] - target.center[1]

    if dy == 0:
      return 0 if isinstance(self.owner, EnemyShip) else -180

    if isinstance(self.owner, EnemyShip):
      if dy > 0:
        return None
    else:
      if dy < 0:
        return None

    tg = dx / float(dy)
    if math.fabs(tg) > math.radians(self.targeting_angle):
      return None

    dir = math.degrees(math.atan(tg))
    if isinstance(self.owner, PlayerShip):
      dir += 180

    return dir

  def shoot(self, pos):
    """
    Perform shot if the weapon has cooled and there is enough energy. Create
    and return projectile instance.

    In case of targeted weapons projectile is shot towards the target if
    target is still in shooting arc. New target is chosen if current
    target is no longer in shooting arc (or there is no current target).
    """
 
    if self.remaining_cooldown > 0:
      return

    if self.current < self.cost:
      return

    if self.target is not None and self.target.destroyed:
      self.target = None
      return

    dir = self._target_dir(self.target)
    if dir is None:
      self._find_target()
      dir = self._target_dir(self.target)

    if dir is None:
      return

    self.remaining_cooldown = self.cooldown
    self.current -= self.cost

    if isinstance(self.owner, EnemyShip):
      g_proj = GroupManager().get('enemy_projectiles')
      g_coll = GroupManager().get('ship')
    else:
      g_proj = GroupManager().get('player_projectiles')
      g_coll = GroupManager().get('enemies')


    EnergyWeapon.shoot(self)

    projectile_cls = eval(self.projectile_cls_name)
    projectile = projectile_cls(pos, dir, g_coll, g_proj)

    return projectile


class BasicProjectileEnergyWeapon(ProjectileEnergyWeapon):
  """
  The least powerful, yet energy effective projectile energy weapon.
  """

  def __init__(self, owner):
    ProjectileEnergyWeapon.__init__(self, owner)


class BasicTPEW(ProjectileEnergyWeapon):
  """
  Targeted version of C{L{BasicProjectileEnergyWeapon}}.
  """

  def __init__(self, owner):
    ProjectileEnergyWeapon.__init__(self, owner)


class SeekingPEW(ProjectileEnergyWeapon):
  """
  Blaster shooting C{L{SeekingProjectile}}s (attempts to
  shoot projectiles not derived from C{SeekingProjectile}
  will fail).
  """

  def __init__(self, owner):
    ProjectileEnergyWeapon.__init__(self, owner)

  def shoot(self, pos):
    p = ProjectileEnergyWeapon.shoot(self, pos)
    if p is not None:
      if isinstance(self.owner, EnemyShip):
        targets = GroupManager().get('ship').sprites()
      else:
        targets = GroupManager().get('enemies').sprites()

      p.set_target(self.owner.closest(targets))


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
  @ivar recharge_rate: Maximum amount of energy recharged per second.

  @type cost: float
  @ivar cost: Amount of energy used per second when shield is active.

  @type active: bool
  @ivar active: Tells whether shield is working or not.
  """

  maximum = 0
  current = 0
  recharge_rate = 0
  cost = 0

  owner = None
  active = False

  def __init__(self, owner):
    AGSprite.__init__(self, owner.rect.center)
    self._check_gfx(['shield'])
    self._check_cfg(['maximum', 'recharge_rate', 'cost'])

    self._setattrs('maximum, recharge_rate, cost', self.cfg)

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
      self.current -= self.cost * Clock().frame_span() / 1000.
      if self.current <= 0:
        self.current = 0
        self.activate(False)

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


  def absorb(self, damage, efficiency = 1.0, speed = None):
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


  def recharge(self, supply, ignore_recharge_rate):
    """
    Recharge shield energy. Amount of energy recharged depends on amount
    of energy supplied and recharge rate. It is assumed that supply is
    never larger than demand. If there is any excess it is lost.
    """

    if not ignore_recharge_rate:
      recharge = self.recharge_rate * Clock().frame_span() / 1000.
      supply = supply if supply <= recharge else recharge

    self.current += supply

    if self.current > self.maximum:
      self.current = self.maximum
    
class AutoShield(Shield):
  """
  Base class for all automatically activated shields. AutoShield is activated
  automatically when projectile moving with speed lesser than C{critical_speed}
  approaches owner so that it could hit it in next iteration. Automatically 
  activated shield is also automatically deactivated. If player activates
  shield manually it cannot be automatically deactivated unless there is
  no more energy.

  @type critical_speed: float
  @ivar critical_speed: Maximal speed of objects that will automatically
  trigger shield expressed in pixels per second.

  @type auto: bool
  @ivar auto: Tells whether shield was activated automatically or not.
  """

  critical_speed = 0
  vanish_speed = 1
  auto = True

  vanish_time = 0
  
  def __init__(self, owner):
    Shield.__init__(self, owner)
    self._setattrs('critical_speed, vanish_speed', self.cfg)

  def activate(self, on, auto = False):
    """
    Activate or deactivate the shield. Display shield graphics if shield
    is activated. Do not allow the shield to be automatically deactivated
    id it was activated by player.

    @type  activate: bool
    @param activate: Tells whether shield should be activated or deactivated.

    @type  auto: bool
    @param auto: Tells whether action is taken by player or automatically.
    """

    if on is self.active:
      return

    if on is False and self.auto is not True and auto is True:
      return

    self.auto = auto
    self.vanish_time = self.vanish_speed if auto is True else 0

    Shield.activate(self, on)

  def absorb(self, damage, efficiency = 1.0, speed = None):
    """
    If shield is not active and C{speed} is not higher than 
    C{self.critical_speed} activate it and absorb damage. Return remaining
    raw damage.
    """

    if self.active is False and speed is not None and \
        speed <= self.critical_speed:
      self.activate(True, True)

    return Shield.absorb(self, damage, efficiency, speed)    


  def update(self):
    self.vanish_time -= Clock().frame_span() / 1000.
    if self.vanish_time <= 0:
      self.activate(False, True)

    Shield.update(self)


class BasicShield(Shield):
  def __init__(self, owner):
    Shield.__init__(self, owner)


class BasicAutoShield(AutoShield):
  def __init__(self, owner):
    AutoShield.__init__(self, owner)


class EnemyShipShield(AutoShield):
  def __init__(self, owner):
    AutoShield.__init__(self, owner)
 

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


  def absorb(self, damage, efficiency):
    """
    Absorb specified amount of raw C{damage} caused with C{efficiency} and
    return remaining raw damage to be absorbed.
    """

    total = damage * efficiency
    absorbed = self.current if total > self.current else total
    remaining = (total - absorbed) / efficiency

    self.current -= absorbed

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

  @type power: float
  @ivar power: Amount of energy produced per second.
  """

  power = 0

  def __init__(self):
    """
    """

    AGObject.__init__(self)

    self.cfg = DBManager().get(self.__class__.__name__)['props']
    self._setattrs('power', self.cfg)

  def supply(self):
    """
    Return all energy available at this moment.
    """

    return self.power * Clock().frame_span() / 1000.


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

  def __init__(self, pos, dir, g_coll, *groups):
    """
    Create projectile moving in direction C{dir} colliding with
    objects from group C{g_coll}. Add created projectile to C{groups}.

    @type  dir: float
    @param dir: Approximate direction in which the projectile is shoot. This
    should be used but may be ignored by projectile's mover.
    """

    AGSprite.__init__(self, pos, *groups)
 
    self._setattrs('damage, explosion_cls_name', self.cfg)

    self.g_coll = g_coll
    self.g_expl = GroupManager().get('explosions')

    self.mover = mover.LinearMover(pos, self.max_speed, {'dir' : dir})

  def update(self):
    self._update_position()
    self._detect_collisions()
    # tmp
    if self.rect.bottom < 0 or self.rect.top > 600:
      self.kill()
      del self

  def explode(self):
    explosion_cls = eval(self.explosion_cls_name)

    self.g_expl.add( explosion_cls(self.pos) )
    self.kill()
    del self

  def _detect_collisions(self):
    hit = pygame.sprite.spritecollide(self, self.g_coll, False)
    if hit:  # hit is a list
      hit[0].damage(self.damage, self.max_speed)
      self.explode()


class ScatteringProjectile(Projectile):
  """
  At the moment of explosion or after a C{lifetime} seconds   
  C{ScatteringProjectile}s explode and spawn C{child_cnt} of C{child_cls_name}
  projectiles moving in random directions.

  @type time: float
  @ivar time: Time since spawning projectile expressed in seconds.

  @type lifetime: float
  @ivar lifetime: Time before projectile's self-destruction expressed
  in seconds.

  @type child_cnt: int
  @ivar child_cnt: Number of child projectiles.

  @type child_cls_name: string
  @ivar child_cls_name: Classname of child projectile.

  @type scatter_type: string
  @ivar scatter_type: Determines direction of child projectiles ('forward', 
  'random', 'regular' - defaults to 'forward')
  """

  time = 0.

  lifetime = 2
  child_cnt = 2
  child_cls_name = None

  scatter_type = 'forward'

  def __init__(self, pos, dir, g_coll, *groups):
    Projectile.__init__(self, pos, dir, g_coll, *groups)

    self._setattrs('lifetime, child_cnt, child_cls_name', self.cfg)
    if self.child_cls_name is None:
      raise ValueError("Unknown child class name")

  def _spawn_children(self):
    """
    Spawn children and add them to proper groups.
    """

    child_cls = eval(self.child_cls_name)
    for i in xrange(self.child_cnt):
      if self.scatter_type == 'random':
        dir = 360 * random.random()
      elif self.scatter_type == 'regular':
        dir = self.mover.get_dir() + 360. * i / self.child_cnt
      else:
        dir = self.mover.get_dir() + 90. * i / (self.child_cnt - 1) - 45

      child = child_cls(self.pos, dir, self.g_coll, self.groups())

  def update(self):
    self.time += Clock().frame_span() / 1000.
    if self.time >= self.lifetime:
      self.explode()
      return

    Projectile.update(self)

  def explode(self):
    """
    Spawn children and explode.
    """
    
    self._spawn_children()

    Projectile.explode(self)


class SeekingProjectile(Projectile):
  """
  Base class for projectiles following chosen target.
  """

  def __init__(self, pos, dir, g_coll, *groups):
    Projectile.__init__(self, pos, dir, g_coll, *groups)

    self._setattrs('ang_speed', self.cfg)

    mover_params = {'dir' : dir, 'ang_speed' : self.ang_speed}
    self.mover = mover.SeekingMover(pos, self.max_speed, mover_params)

  def set_target(self, target):
    """
    Set target the projectile has to follow.
    """

    self.mover.set_target(target)


class Bullet(Projectile):
  def __init__(self, pos, dir, g_coll, *groups):
    Projectile.__init__(self, pos, dir, g_coll, *groups)

    size = 1, 2

    self.image = pygame.Surface(size)
    self.image.set_colorkey((0, 0, 0))
    self.image.fill((255, 210, 0))

    self._initialize_position(pos, 'center', size)


class EnergyProjectile(Projectile):
  def __init__(self, pos, dir, g_coll, *groups):
    Projectile.__init__(self, pos, dir, g_coll, *groups)

    size = self.gfx['energy']['w'], self.gfx['energy']['h']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['energy']['image'])
    self._blit_state('energy', 'frame2')

    self._initialize_position(pos, 'center', size)

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


class ScatterBlasterProjectile(ScatteringProjectile):
  """
  Projectile intended to be shot by C{L{ScatterBlaster}}.
  """

  def __init__(self, pos, dir, g_coll, *groups):
    ScatteringProjectile.__init__(self, pos, dir, g_coll, *groups)

    size = self.gfx['energy']['size']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['energy']['image'])
    self._blit_state('energy', 'frame2')

    self._initialize_position(pos, 'center', size)


class SeekingEnergyProjectile(SeekingProjectile):
  """
  """

  def __init__(self, pos, dir, g_coll, *groups):
    SeekingProjectile.__init__(self, pos, dir, g_coll, *groups)

    size = self.gfx['energy']['size']

    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['energy']['image'])
    self._blit_state('energy', 'frame2')

    self._initialize_position(pos, 'center', size)


class Bonus(AGSprite):
  """
  Base class for bonuses/powerups that can be collected by players. Bonuses
  collide with objects belonging to group 'ship'.

  W momencie kolizji wywolywana jest metoda, ktorej argumentem jest 
  referencja do obiektu, z ktorym nastapila kolizja. Ta metoda ma 
  za zadanie wywolac jakis pozytywny dla obiektu efekt.
  """

  def __init__(self, pos, *groups):
    """
    Create bonus instance. Initialize its C{image} and C{rect}.
    """

    AGSprite.__init__(self, pos, *groups)

    size = self.gfx['bonus']['w'], self.gfx['bonus']['h']
    self.image = pygame.Surface(size, pygame.SRCALPHA,
        self.gfx['bonus']['image'])

    self._blit_state('bonus', 'def')
    self._initialize_position(pos, 'center', size)

    self.mover = mover.CircularMover(pos, self.max_speed)

  def _detect_collisions(self):
    """
    Detect collisions and return single colliding ship or None.
    """

    ships = GroupManager().get('ship').sprites()
    i = self.rect.collidelist(ships)
    return None if i == -1 else ships[i]

  def update(self):
    self.pos = self._update_position()

    ship = self._detect_collisions()
    if ship is not None:
      self._use(ship)
      self.kill()
      del self

  def _use(self, ship):
    """
    Use bonus on C{ship}. Classes derived from C{Bonus} need to override
    this method.
    """
  
    pass


class RechargeBonus(Bonus):
  """
  This bonus recharges player ship's shields and energy weapons.
  """

  power = 100

  def __init__(self, pos, *groups):
    Bonus.__init__(self, pos, *groups)
    self._setattrs('power', self.cfg)

  def _use(self, ship):
    """
    Recharge C{ship}'s shields and energy weapons.
    """

    ship.recharge(self.power, True)
