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

from functions import deg2rad, rad2deg

class Mover:
  """
  Base class for all movers.

  @type clock: integer
  @ivar clock: internal clock needed to perform simulation
  """

  def __init__(self):
    """
    Crate mover instance and initialize its clock. Should not be used as this
    class is designed as abstract class and does not provide useful
    functionality on its own.
    """

    self.clock = 0

  def _setattrs(self, params, values):
    """
    Setup instance attributes. 
    
    This is auxiliary method that will set value of instance attribute if its
    name exists in C{params} and C{values} (as a key). If key from C{value}
    does not exist in C{params} an exception is raised. All attributes
    whose names exist in C{params} should have default values.

    @type params: string, list or tuple
    @param params: Names of allowed parameters - if string, names should be 
    comma-separated

    @type values: dict
    @param values: Dictionary containing instance attribute values
    """

    if type(params) not in (str, list, tuple):
      raise TypeError("attribute 'params' must be a string, a list or a tuple")

    if type(values) is not dict:
      raise TypeError("attribute 'values' must be a dict")

    if type(params) is str:
      params = params.split(',')
      params = map(lambda s: s.strip(), params)

    for name in values:
      if name not in params:
        v = "param named '%s' is not allowed for %s, allowed params: %s" % \
            (name, self.__class__.__name__, ', '.join(params))
        raise ValueError(v)

      setattr(self, name, values[name])


  def update(self):
    """
    Return updated object's coordinates in a tuple. Needs to be overriden
    by child classes.
    """
 
    self.clock += 1
    return 0, 0


class RandomMover(Mover):
  """
  Randomly changes direction of an object but not its speed. May allow object
  to float out of the viewport.
  
  @type pos: list
  @ivar pos: object's current position

  @type period: integer
  @ivar period: amount of time between changes of direction 

  @type speed: integer
  @ivar speed: object's speed
  
  @type dir: integer
  @ivar dir: object's direction
  """

  period = 120

  def __init__(self, pos, speed, params):
    """
    Create instance of RandomMover.
    
    @type pos: tuple
    @param pos: object's initial position as tuple of two integers

    @type speed: integer
    @param speed: object's maximal linear speed

    @type params: dict
    @param params: Custom parametrisation
    """

    Mover.__init__(self)
    self.pos = list(pos)
    self.speed = speed
    self._setattrs(('period'), params)

  def update(self):
    if self.clock % self.period == 0:
      self.dir = random.randint(0, 359)

    self.clock += 1

    self.pos[0] += round(self.speed * math.sin(deg2rad(self.dir)))
    self.pos[1] += round(self.speed * math.cos(deg2rad(self.dir)))

    return self.pos


class ZigZagMover(Mover):
  """
  Couses object to make zigzaging movement from top to the bottom. Exact
  trajectory is determined by objects C{speed} and zigzag C{radius}.

  @type init_pos: array
  @ivar init_pos: object's initial position

  @type speed: integer
  @ivar speed: object's linear speed in pixels per iteration

  @type radius: integer
  @ivar radius: zigzag radius

  @type period: float
  @ivar period: time needed for one zigzag segment

  @type ang_speed: float
  @ivar ang_speed: object's angular speed measured in radians per iteration
  """

  radius = 25

  def __init__(self, pos, speed, params):
    """
    Create mover instance.

    @type pos: array or tuple
    @param pos: object's current position

    @type speed: integer
    @param speed: object's maximal linear speed

    @type params: dict
    @param params: Custom parametrisation
    """

    Mover.__init__(self)

    self.init_pos = [pos[0], pos[1]]
    self.speed = speed
    self._setattrs(('radius'), params)
    self.period = math.pi * self.radius / float(self.speed)
    self.ang_speed = self.speed / float(self.radius)

  def update(self):
    self.clock += 1

    k = math.floor(self.clock / self.period)
    x = self.radius * math.sin(self.ang_speed * self.clock) 
    y = self.radius * math.cos(self.ang_speed * self.clock % math.pi + math.pi)

    y += (2 * k + 1) * self.radius
    
    self.pos = self.init_pos[0] + x, self.init_pos[1] + y
    return self.pos


class CircularMover(Mover):
  """
  Causes object to make circular movement around its initial position. Before
  starting circular movement object moves in random direction to enter its
  trajectory.

  @type init_pos: array
  @ivar init_pos: object's initial position

  @type speed: integer
  @ivar speed: object's linear speed on circular trajectory

  @type radius: integer
  @ivar radius: circle radius

  @type ang_speed: integer
  @ivar ang_speed: object's angular speed on circular trajectory measured in degrees per iteration

  @type init_speed: integer
  @ivar init_speed: object's linear speed used to enter circular trajectory

  @type init_time: integer
  @ivar init_time: number of iterations needed to enter circular trajectory

  @type init_dir: integer
  @ivar init_dir: randomly chosen direction used to enter circular trajectory
  expressed in radians
  """

  radius = 20

  def __init__(self, pos, speed, params):
    """
    Create CircularMover instance.

    @type pos: array or tuple
    @param pos: object's current position

    @type speed: integer
    @param speed: object's maximal linear speed

    @type params: dict
    @param params: Custom parametrisation
    """

    Mover.__init__(self)

    self.init_pos = [pos[0], pos[1]]
    self.speed = speed
    self._setattrs(('radius'), params)
    self.ang_speed = self.speed / float(self.radius)
    self.init_speed = self.speed / \
        float(math.ceil(self.speed / float(self.radius)))

    self.init_time = self.radius / float(self.init_speed)
    self.init_dir = 2 * math.pi * random.random()

  def update(self):
    self.clock += 1
    if self.clock <= self.init_time:
      x = self.clock * self.init_speed * math.sin(self.init_dir)
      y = self.clock * self.init_speed * math.cos(self.init_dir)
    else:
      a = (self.clock - self.init_time) * self.ang_speed + self.init_dir
      x = self.radius * math.sin(a)
      y = self.radius * math.cos(a)
    
    self.pos = self.init_pos[0] + x, self.init_pos[1] + y
    return self.pos

class LinearMover(Mover):
  """
  Causes object to move in a straight line with constant speed.

  @type pos: tuple or array of two elements representing x- and y-coordinate
  @ivar pos: object's initial position

  @type speed: integer
  @ivar speed: object's linear speed

  @type dir: integer
  @ivar dir: object's direction expressed in radians
  """

  dir = 0

  def __init__(self, pos, speed, params):
    """
    Create mover instance.

    @type pos: tuple or array of two elements representing x- and y-coordinate
    @param pos: object's initial position

    @type speed: integer
    @param speed: object's maximal linear speed

    @type params: dict
    @param params: 'speed' - max speed in pixels per iteration;
                   'dir' - direction in degrees
    """

    Mover.__init__(self)

    self.pos = pos
    self.speed = speed
    self._setattrs(('dir'), params)
    self.dir = deg2rad(self.dir)

  def update(self):
    self.clock += 1

    try:
      return self.pos[0] + self.clock * self.speed * math.sin(self.dir), \
             self.pos[1] + self.clock * self.speed * math.cos(self.dir)
    except ValueError, value:
      print "Warning: unhandled ValueError: %s" % value

