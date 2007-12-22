#!/usr/bin/python
#coding: utf-8

"""
This module contains base definitions needed by different modules.
"""

import pygame

from dbmanager import DBManager


class AGObject:
  """
  Base class for all game objects.
  """

  def __init__(self):
    """
    """

    pass

  def _setattrs(self, params, values):
    """
    Setup instance attributes. 
    
    This is an auxiliary method that will set value of instance attribute if its
    name exists in C{params} and C{values} (as a key). All attributes
    whose names exist in C{params} should have default values. If there is
    no default value for attribute which does not have value defined in
    C{values} an exception is raised.

    @type  params: string, list or tuple
    @param params: Names of allowed parameters - if string, names should be 
    comma-separated

    @type  values: dict
    @param values: Dictionary containing instance attribute values
    """

    if type(params) not in (str, list, tuple):
      raise TypeError("attribute 'params' must be a string, a list or a tuple")

    if type(values) is not dict:
      raise TypeError("attribute 'values' must be a dict")

    if type(params) is str:
      params = params.split(',')
      params = map(lambda s: s.strip(), params)

    for name in params:
      if name in values.keys():
        setattr(self, name, values[name])
      elif not hasattr(self, name): 
        v = "%s.%s does not have any value defined" % \
            (self.__class__.__name__, name)
        raise ValueError(v)


class Overlay(pygame.sprite.Sprite):
  """
  Overlay can be used to display auxiliary animated effects over a sprite.
  Overlays are not independent game objects. Overlays do not contain
  any graphics resources on their own. Overlays do not collide. Overlay's
  image size is changed dynamically. Overlay's image has to be initialized 
  with owner's image in order to preserve surface properites. Overlay itself
  should be added to group 'draw' immediatelly after its owner is added to
  that groups in order to display properly (not to display over other 
  objects).
  """

  def __init__(self, *groups):
    pygame.sprite.Sprite.__init__(self, *groups)

    #tmp
    self.size = 200, 200

    self.rect = AGRect((0, 0), self.size)
    self.image = pygame.Surface((0, 0), pygame.SRCALPHA)

  def init_image(self, owner_image):
    self.image = pygame.Surface(self.size, pygame.SRCALPHA, owner_image)

  def has_image(self):
    return self.image.get_size() != (0, 0)

  def fill(self, colour, rect = None):
    """
    Fill overlay fragment with C{colour}.

    @type  colour: sequence
    @param colour: Fill colour

    @type  rect: C{L{AGRect}} or C{None}
    @param rect: Area to be filled. Size and coordinates of top-left
    corner of area relative to overlay center. If C{None} entire
    overlay area is filled.
    """

    if rect is None:
      rect = AGRect((0, 0), self.image.get_size())
    else:
      rect = AGRect(rect)
      
      rect[0] += self.rect.width / 2.
      rect[1] += self.rect.height / 2.

    self.image.fill(colour, rect)

  def clear(self, rect = None):
    """
    Clear overlay fragment.

    @type  rect: C{L{AGRect}} or C{None}
    @param rect: Area to be cleared. Size and coordinates of top-left
    corner of area relative to overlay center. If C{None} entire
    overlay area is cleared.
    """

    self.fill((0, 0, 0, 0), rect)

  def blit(self, image, dest, area):
    """
    Blit C{image} on overlay.

    @type  image: C{pygame.Surface}
    @param image: Image to blit

    @type  dest: sequence
    @param dest: Position of top-left corner of image relative to overlay
    center.

    @type  area: C{L{AGRect}}
    @param area: Image fragment to be blit.
    """

    dest = list(dest)

    dest[0] += self.rect.width / 2.
    dest[1] += self.rect.height / 2.

    self.image.blit(image, dest, area)

  def align(self, pos, align = 'center'):
    """
    Position overlay.
    """

    self.rect.align(pos, align)


class AGRect(pygame.Rect):
  """
  C{pygame.Rect} with extended functionality.
  """

  def align(self, pos, align):
    """
    Position rectangle using C{pygame.Rect} properties such as 'topleft',
    'center' or pairs of properties such as ('top', left'), ('bottom',
    'right'), etc.

    @type  pos: sequence
    @param pos: New position of rectangle's point relative to which
    rectangle is aligned.

    @type  align: str or sequence
    @param align: String naming C{pygame.Rect} property or sequence containing
    pair of such strings.
    """

    if type(align) is tuple or type(align) is list:
      setattr(self, align[0], pos[0])
      setattr(self, align[1], pos[1])
    elif type(align) is str:
      setattr(self, align, pos)
    else:
      raise ValueError("Invalid align value")

