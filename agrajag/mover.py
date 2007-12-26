#!/usr/bin/python
#coding: utf-8

"""
Module contain definitions of different types of movers (objects thay control
movement of other objects).

All non abstract movers must have the same constructor signature. This
allows to dynamically create movers for objects generated according to 
stage schemas.

Mover constructor takes exactly three parameters. First one is object's
current position, second one is object's maximal speed and third one is a 
dictionary containing parameters specific for different classes.
"""

import pygame
import random
import math

from base import AGObject
from clock import Clock
from groupmanager import GroupManager

from functions import sgn, deg2rad, rad2deg, normalize_rad

class Mover(AGObject):
  """
  Base class for all movers.

  @type clock: integer
  @ivar clock: Clock instance
  """

  def __init__(self):
    """
    Crate mover instance and initialize its clock. Should not be used
    as this class is designed as an abstract class and does not provide
    any useful functionality on its own.
    """

    AGObject.__init__(self)

    self.clock = Clock()


  def update(self):
    """
    Return updated object's coordinates in a tuple. Needs to be overriden
    by child classes.
    """
 
    return 0, 0


class RandomMover(Mover):
  """
  Randomly changes direction of an object but not its speed. May allow object
  to float out of the viewport.

  @type pos: list
  @ivar pos: object's current position

  @type period: float
  @ivar period: amount of time between changes of direction (in miliseconds) 

  @type time: float
  @ivar time: time passed since last change of direction (in miliseconds)
  
  @type speed: float
  @ivar speed: object's speed in pixels per second
  
  @type dir: integer
  @ivar dir: object's direction
  """

  period = 1500

  def __init__(self, pos, speed, params = {}):
    """
    Create instance of RandomMover.
    
    @type pos: tuple
    @param pos: object's initial position as tuple of two integers

    @type speed: float
    @param speed: object's maximal linear speed in pixels per second

    @type params: dict
    @param params: Custom parametrisation
    """

    Mover.__init__(self)
    self.pos = list(pos)
    self.speed = speed
    self._setattrs(('period'), params)

    self.time = self.period

  def update(self):
    if self.time >= self.period:
      self.dir = random.randint(0, 359)
      self.time -= self.period

    frame_span = self.clock.frame_span()
    self.time += frame_span

    delta_pos = frame_span * self.speed / 1000.
    self.pos[0] += round(delta_pos * math.sin(deg2rad(self.dir)))
    self.pos[1] += round(delta_pos * math.cos(deg2rad(self.dir)))

    return self.pos


class ZigZagMover(Mover):
  """
  Couses object to make zigzaging movement from top to the bottom. Exact
  trajectory is determined by objects C{speed} and zigzag C{radius}.

  @type init_pos: list
  @ivar init_pos: object's initial position

  @type speed: integer
  @ivar speed: object's linear speed in pixels per second

  @type radius: integer
  @ivar radius: zigzag radius in pixels

  @type period: float
  @ivar period: time needed for one zigzag segment (sec)

  @type ang_speed: float
  @ivar ang_speed: object's angular speed measured in radians per second

  @type time: float
  @ivar time: time passed since mover initialization (in miliseconds)
  """

  radius = 25

  def __init__(self, pos, speed, params = {}):
    """
    Create mover instance.

    @type pos: sequence
    @param pos: object's current position

    @type speed: integer
    @param speed: object's maximal linear speed

    @type params: dict
    @param params: Custom parametrisation
    """

    Mover.__init__(self)

    self.init_pos = list(pos)
    self.speed = speed
    self._setattrs(('radius'), params)
    self.period = math.pi * self.radius / float(self.speed)
    self.ang_speed = self.speed / float(self.radius)

    self.time = 0

  def update(self):
    k = math.floor(self.time / self.period / 1000.)
    x = self.radius * math.sin(self.ang_speed * self.time / 1000.) 
    y = self.radius * math.cos(self.ang_speed * self.time / 1000. % math.pi +
        math.pi)
    
    self.time += self.clock.frame_span()

    y += (2 * k + 1) * self.radius
    
    self.pos = self.init_pos[0] + x, self.init_pos[1] + y
    return round(self.pos[0]), round(self.pos[1])


class CircularMover(Mover):
  """
  Causes object to make circular movement around its initial position. Before
  starting circular movement object moves in random direction to enter its
  trajectory.

  @type init_pos: list
  @ivar init_pos: object's initial position

  @type speed: integer
  @ivar speed: object's linear speed on circular trajectory (px/sec)

  @type radius: integer
  @ivar radius: circle radius in pixels

  @type ang_speed: integer
  @ivar ang_speed: object's angular speed on circular trajectory measured in
  degrees per second

  @type init_speed: integer
  @ivar init_speed: object's linear speed used to enter circular trajectory

  @type init_time: integer
  @ivar init_time: time needed to enter circular trajectory with init_speed

  @type init_dir: integer
  @ivar init_dir: randomly chosen direction used to enter circular trajectory
  expressed in radians

  @type time: float
  @ivar time: time passed since mover initialization (in miliseconds)
  """

  radius = 20

  def __init__(self, pos, speed, params = {}):
    """
    Create CircularMover instance.

    @type pos: sequence
    @param pos: object's current position

    @type speed: integer
    @param speed: object's maximal linear speed in pixels per second

    @type params: dict
    @param params: Custom parametrisation
    """

    Mover.__init__(self)

    self.init_pos = list(pos)
    self.speed = speed
    self._setattrs(('radius'), params)
    self.ang_speed = self.speed / float(self.radius)
    self.init_speed = self.speed / \
        float(math.ceil(self.speed / float(self.radius)))

    self.init_time = 1000 * self.radius / float(self.init_speed)
    self.init_dir = 2 * math.pi * random.random()

    self.time = 0

  def update(self):
    if self.time <= self.init_time:
      x = self.time * self.init_speed * math.sin(self.init_dir) / 1000.
      y = self.time * self.init_speed * math.cos(self.init_dir) / 1000.
    else:
      a = (self.time - self.init_time) * self.ang_speed / 1000. + self.init_dir
      x = self.radius * math.sin(a)
      y = self.radius * math.cos(a)
    
    self.time += self.clock.frame_span()

    self.pos = self.init_pos[0] + x, self.init_pos[1] + y
    return round(self.pos[0]), round(self.pos[1])


class LinearMover(Mover):
  """
  Causes object to move in a straight line with constant speed.

  @type pos: tuple or array of two elements representing x- and y-coordinate
  @ivar pos: object's current position

  @type speed: integer
  @ivar speed: object's linear speed

  @type dir: integer
  @ivar dir: object's direction expressed in radians
  """

  dir = 0

  def __init__(self, pos, speed, params = {}):
    """
    Create mover instance.

    @type pos: tuple or array of two elements representing x- and y-coordinate
    @param pos: object's initial position

    @type speed: integer
    @param speed: object's maximal linear speed

    @type params: dict
    @param params: 'speed' - max speed in pixels per second;
                   'dir' - direction in degrees
    """

    Mover.__init__(self)

    self.pos = list(pos)
    self.speed = speed
    self._setattrs(('dir'), params)
    self.dir = deg2rad(self.dir)

  def get_dir(self):
    """
    Return current direction in degrees.
    """

    return rad2deg(self.dir)

  def update(self):
    try:
      delta_pos = self.clock.frame_span() * self.speed / 1000.

      self.pos[0] += delta_pos * math.sin(self.dir)
      self.pos[1] += delta_pos * math.cos(self.dir)
      
      return round(self.pos[0]), round(self.pos[1])
    except ValueError, value:
      print "Warning: unhandled ValueError: %s" % value


class LinearPlayerTargetingMover(Mover):
  """
  This mover choses its target from group 'ship' and tries to position
  owning ship in front of the target.

  @type vertical_div: float
  @ivar vertical_div: Angular divergence from default (vertical) direction (in
  radians).

  @type target:
  @ivar target: Object in front of which owner is positioned.
  """

  vertical_div = math.pi / 3.

  def __init__(self, pos, speed, params = {}):
    Mover.__init__(self)
    self._setattrs('vertical_div', params)

    self.pos = list(pos)
    self.speed = speed

    ships = GroupManager().get('ship').sprites()
    self.target = None if len(ships) == 0 else ships[0]

  def update(self):
    delta_pos = self.clock.frame_span() * self.speed / 1000.
    d = self.target.pos[0] - self.pos[0]

    dir = math.pi / 2. - self.vertical_div
    if delta_pos > math.fabs(d):
      self.pos[0] += d * math.sin(dir)
    else:
      self.pos[0] += delta_pos * d / math.fabs(d) * math.sin(dir)

    self.pos[1] += math.fabs(delta_pos * math.cos(dir))

    return round(self.pos[0]), round(self.pos[1])

class SeekingMover(Mover):
  """
  This mover makes its owner chase its C{target}. Trajectory of owner
  is determined by its C{speed} and C{ang_speed}.

  Interface for setting C{target} needs to be defined.

  @type speed: float
  @ivar speed: Object's maximal linear speed in pixels per second

  @type ang_speed: float
  @ivar ang_speed: Object's direction cannot be changed by more than
  C{ang_speed} radians per second.

  @type target:
  @ivar target: Targeted object.

  @type pos: sequence
  @ivar pos: Current position.

  @type dir: float
  @ivar dir: Current direction in radians.
  """

  def __init__(self, pos, speed, params = {}):
    """
    """

    Mover.__init__(self)
    self._setattrs('dir, ang_speed', params)

    self.pos = list(pos)
    self.speed = speed
    self.dir = deg2rad(self.dir)
    self.ang_speed = deg2rad(self.ang_speed)

    self.target = None

  def set_target(self, target):
    """
    Set target to follow.
    """

    self.target = target

  def get_dir(self):
    """
    Return current direction in degrees.
    """

    return rad2deg(self.dir)

  def _update_dir(self):
    """
    Update C{dir} based on C{target} position. Do nothing if there is no
    C{target}.
    """
   
    if self.target is None:
      return

    target_pos = self.target.center

    dx = self.pos[0] - self.target.center[0]
    dy = self.pos[1] - self.target.center[1]

    try:
      tan = dx / float(dy)
    except ZeroDivisionError:
      tan = 0

    new_dir = normalize_rad(math.atan(tan) + 2 * math.pi)
    if dy > 0:
      new_dir = normalize_rad(new_dir + math.pi)
 
    delta_dir = new_dir - self.dir
    max_delta_dir = self.ang_speed * self.clock.frame_span() / 1000.
    if math.fabs(delta_dir) > max_delta_dir:
      if math.fabs(delta_dir) < math.pi:
        delta_dir = sgn(delta_dir) * max_delta_dir
      else:
        delta_dir = -sgn(delta_dir) * max_delta_dir

    self.dir = normalize_rad(self.dir + delta_dir)

  def update(self):
    delta_pos = self.clock.frame_span() * self.speed / 1000.
    
    self._update_dir()

    self.pos[0] += delta_pos * math.sin(self.dir)
    self.pos[1] += delta_pos * math.cos(self.dir)
      
    return round(self.pos[0]), round(self.pos[1])

